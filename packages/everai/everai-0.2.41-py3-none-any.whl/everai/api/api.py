import functools
import typing
import certifi

from everai.token_manager import TokenManager
from generated.configmaps import (
    ApiClient as ConfigMapsClient,
    ConfigmapServiceApi, V1Configmap, ConfigmapServiceCreateBody, ConfigmapServiceUpdateBody
)

from generated.resources import (
    ApiClient as ResourcesClient,
    ResourcesServiceApi as ResourcesServiceApi,
)

from generated.apps import (
    ApiClient as AppsClient,
    ApiClient as NamespacesClient,
    V1App,
    AppServiceApi as AppServiceApi,
    NamespaceServiceApi as NamespaceServiceApi,
    V1Worker,
    V1ListRequestQueuesResponseRequestQueue,
    ApiException as AppApiException, V1Namespace, V1Event,
)

from generated.volumes import (
    ApiClient as VolumesClient,
    Configuration,
    V1Volume,
    V1File,
    VolumeServiceSignUploadBody,
    VolumeServiceCommitFileBody,
    V1Revision,
    VolumeServiceCommitRevisionBody,
    VolumeServiceInitializeMultipartUploadBody,
    VolumeServiceCompleteMultipartUploadBody,
    V1Part,
    VolumeServiceSignMultipartUploadBody,
    V1HeaderValue,
    V1UploadAction,
    VolumeServiceCommitFileBodyFile,
    VolumeServiceApi,
    VolumeServiceCreateBody
)

from generated.secrets import (
    ApiClient as SecretsClient,
    V1Secret,
    SecretServiceApi,
    SecretServiceCreateBody, SecretServiceUpdateBody,
)

from everai.constants import EVERAI_ENDPOINT


class ConflictException(Exception):
    ...

class ValueFromSecret:
    secret_name: str
    key: str

    def __init__(self, secret_name: str, key: str):
        self.secret_name = secret_name
        self.key = key


def check_token(func):
    @functools.wraps(func)
    def wrapper(s, *args, **kwargs):
        if s.token is None:
            raise ValueError("token not found, please login first")
        return func(s, *args, **kwargs)

    return wrapper


T = typing.TypeVar('T')
S = typing.TypeVar('S')


def _create_api(cli_type: T,
                svc_type: S,
                token: str,
                endpoint: str):
    cfg = Configuration(
        host=endpoint,
        ssl_ca_cert=certifi.where()
    )
    # cfg.debug = True
    client = cli_type(
        header_name='Authorization',
        header_value=f'Bearer {token}',
        configuration=cfg,
    )
    service_api = svc_type(client)
    return client, service_api


class API:
    token: typing.Optional[str]
    volumes_client: VolumesClient
    apps_client: AppsClient
    namespaces_client: NamespacesClient
    secrets_client: SecretsClient
    configmaps_client: ConfigMapsClient
    resources_client: ResourcesClient

    app_service_api: AppServiceApi
    namespaces_service_api: NamespaceServiceApi
    secret_service_api: SecretServiceApi
    volume_service_api: VolumeServiceApi
    configmap_service_api: ConfigmapServiceApi
    resources_service_api: ResourcesServiceApi

    def __init__(self, endpoint: str = None):
        endpoint = endpoint or EVERAI_ENDPOINT
        self.token = TokenManager().get_token()

        self.volumes_client, self.volume_service_api = (
            _create_api(VolumesClient, VolumeServiceApi, self.token, endpoint))

        self.apps_client, self.app_service_api = (
            _create_api(AppsClient, AppServiceApi, self.token, endpoint))

        self.namespaces_client, self.namespaces_service_api = (
            _create_api(NamespacesClient, NamespaceServiceApi, self.token, endpoint))

        self.secrets_client, self.secret_service_api = (
            _create_api(SecretsClient, SecretServiceApi, self.token, endpoint))

        self.configmaps_client, self.configmap_service_api = (
            _create_api(ConfigMapsClient, ConfigmapServiceApi, self.token, endpoint))

        self.resources_client, self.resources_service_api = (
            _create_api(ResourcesClient, ResourcesServiceApi, self.token, endpoint))

    def login(self, token: str) -> None:
        # do some check
        TokenManager().set_token(token)

    def create_volume(self, name: str, labels: typing.Dict[str, str] = None) -> V1Volume:
        body = VolumeServiceCreateBody()
        body.labels = labels
        v1_volume = self.volume_service_api.create_volume(name, body)
        return v1_volume

    def list_volume_files(self, name: str) -> typing.List[V1File]:
        list_file_resp = self.volume_service_api.list_files(name)

        return list_file_resp.files

    # noinspection PyMethodMayBeStatic
    def headers(self, headers: typing.Optional[typing.Dict[str, V1HeaderValue]]) -> [
        typing.Dict[str, typing.List[str]]]:
        return {key: value.value for key, value in headers.items()}

    def sign_download(self, name: str, file_path: str) -> tuple[str, str, typing.Dict[str, typing.List[str]]]:
        resp = self.volume_service_api.sign_download(name, path=file_path)
        assert resp.method is not None
        assert resp.url is not None
        return resp.method, resp.url, self.headers(resp.headers)

    def sign_upload(self, name: str, revision_name: str, file_path: str, file_size: int,
                    file_sha256: str) -> (bool, str, str, typing.Dict[str, typing.List[str]]):
        """
        :return:
            bool    True means need upload, False means already uploaded
            str     http method
            str     url
            dict    headers
        """
        body = VolumeServiceSignUploadBody().from_dict({'file': {'size': str(file_size), 'sha256': file_sha256}})
        resp = self.volume_service_api.sign_upload(volume_name=name, revision_name=revision_name,
                                                   file_path=file_path, body=body)
        return (resp.action == V1UploadAction.UPLOAD, resp.response.method, resp.response.url,
                self.headers(resp.response.headers))

    def create_revision(self, name: str) -> V1Revision:
        return self.volume_service_api.create_revision(volume_name=name)

    def volume_cancel_revision(self, name: str, revision_name: str) -> None:
        self.volume_service_api.cancel_revision(volume_name=name, revision_name=revision_name)

    def commit_revision(self, name: str, revision_name: str, files: typing.List[V1File]) -> None:
        self.volume_service_api.commit_revision(
            volume_name=name,
            revision_name=revision_name,
            body=VolumeServiceCommitRevisionBody(files=files),
        )

    def init_multipart_upload(self, name: str, revision_name: str, file_path: str, file_size: int,
                              file_sha256: str) -> tuple[bool, str]:
        """
        :return:
            bool True means need upload, False means already uploaded
            str Upload ID
        """
        resp = self.volume_service_api.initialize_multipart_upload(
            volume_name=name,
            revision_name=revision_name,
            file_path=file_path,
            body=VolumeServiceInitializeMultipartUploadBody().from_dict(
                {'file': {'size': str(file_size), 'sha256': file_sha256}})
        )

        return resp.action == V1UploadAction.UPLOAD, resp.upload_id

    def cancel_multipart_upload(self, name: str, revision_name: str, upload_id: str) -> None:
        self.volume_service_api.cancel_multipart_upload(
            volume_name=name,
            revision_name=revision_name,
            upload_id=upload_id)

    def complete_multipart_upload(self, name: str, revision_name: str, upload_id: str, parts: typing.List[V1Part],
                                  mime_type: str = None) -> None:
        self.volume_service_api.complete_multipart_upload(
            name,
            revision_name,
            upload_id,
            VolumeServiceCompleteMultipartUploadBody(parts=parts, mime_type=mime_type),
        )

    def list_multipart_upload_parts(self, name: str, revision_name: str, upload_id: str) -> typing.List[V1Part]:
        resp = self.volume_service_api.list_parts(name, revision_name, upload_id)
        return resp.parts

    def sign_multipart_upload(self, name: str, revision_name: str, upload_id: str,
                              part_number: int) -> tuple[str, str, typing.Dict[str, typing.List[str]]]:
        resp = self.volume_service_api.sign_multipart_upload(
            name,
            revision_name,
            upload_id,
            VolumeServiceSignMultipartUploadBody(part_number=part_number),
        )
        headers = {key: value.value for (key, value) in resp.headers.items()}
        return resp.method, resp.url, headers

    def commit_file(self, name: str, revision_name: str, file: V1File) -> None:
        self.volume_service_api.commit_file(
            volume_name=name,
            revision_name=revision_name,
            file_path=file.path,
            body=VolumeServiceCommitFileBody(file=VolumeServiceCommitFileBodyFile(
                size=file.size,
                sha256=file.sha256,
                created_at=file.created_at,
                modified_at=file.modified_at,
            ))
        )
        return

    def publish_volume(self, name: str):
        return self.volume_service_api.publish_volume(volume_name=name)

    def get_volume(self, name: str) -> V1Volume:
        return self.volume_service_api.get_volume(name)

    def delete_volume(self, name: str) -> None:
        self.volume_service_api.delete_volume(name)

    def list_volumes(self) -> typing.List[V1Volume]:
        resp = self.volume_service_api.list_volume()
        return resp.volumes or []

    def create_secret(self, secret: V1Secret) -> V1Secret:
        resp = self.secret_service_api.create_secret(secret.name, body=SecretServiceCreateBody(
            data=secret.data,
            labels=secret.labels,
        ))
        return resp

    def update_secret(self, secret: V1Secret) -> V1Secret:
        resp = self.secret_service_api.update_secret(secret.name, body=SecretServiceUpdateBody(
            data=secret.data,
            labels=secret.labels,
        ))
        return resp

    def list_secrets(self) -> typing.List[V1Secret]:
        resp = self.secret_service_api.list_secret()
        return resp.secrets or []

    def get_secret(self, name: str) -> V1Secret:
        resp = self.secret_service_api.get_secret(name)
        return resp

    def delete_secret(self, name: str) -> None:
        self.secret_service_api.delete_secret(name)

    def list_namespaces(self) -> typing.List[V1Namespace]:
        return self.namespaces_service_api.list_namespaces().namespaces

    def get_namespace(self, name: str) -> V1Namespace:
        resp = self.namespaces_service_api.get_namespace_with_http_info(name)
        return resp.data

    def create_namespace(self, name: str, labels: typing.Optional[typing.Dict[str, str]] = None) -> V1Namespace:
        return self.namespaces_service_api.create_namespace(V1Namespace(
            name=name,
            labels=labels,
        ))

    def delete_namespace(self, name: str):
        self.namespaces_service_api.delete_namespace(name)

    def get_app(self, name: str, namespace: str) -> V1App:
        return self.app_service_api.get_app(namespace=namespace, name=name)

    def delete_app(self, name: str, namespace: str) -> None:
        self.app_service_api.delete_app(namespace=namespace, name=name)

    def list_apps(self, namespace: str, all_namespaces: bool = False) -> typing.List[V1App]:
        if all_namespaces:
            apps = self.app_service_api.list_all_apps().apps
        else:
            apps = self.app_service_api.list_apps(namespace).apps
        return apps or []

    def pause_app(self, name: str, namespace: str) -> None:
        self.app_service_api.pause_app(namespace=namespace, name=name)

    def resume_app(self, name: str, namespace: str) -> None:
        self.app_service_api.resume_app(namespace=namespace, name=name)

    @check_token
    def create_app(self, app: V1App) -> V1App:
        namespace = app.app_v1alpha1.metadata.namespace or 'default'
        try:
            return self.app_service_api.create_app(
                namespace=namespace,
                app=app,
            )
        except AppApiException as e:
            if e.status == 409:
                raise ConflictException('App name already exists')
            else:
                raise e

    @check_token
    def update_app(self, app: V1App):
        namespace = app.app_v1alpha1.metadata.namespace or 'default'
        return self.app_service_api.update_app(
            namespace=namespace,
            name=app.app_v1alpha1.metadata.name,
            app=app,
        )

    def list_worker(self,
                    app_name: str,
                    namespace: str = 'default',
                    show_all: bool = False,
                    recent_days: int = 2,
                    ) -> typing.List[V1Worker]:
        resp = self.app_service_api.list_workers(
            name=app_name,
            namespace=namespace,
            show_all=show_all,
            recent_days=recent_days,
        )
        return resp.workers or []

    def create_configmap(self, configmap: V1Configmap) -> V1Configmap:
        resp = self.configmap_service_api.create_configmap(configmap.name, body=ConfigmapServiceCreateBody(
            data=configmap.data,
            labels=configmap.labels,
        ))
        return resp

    def update_configmap(self, configmap: V1Configmap) -> V1Configmap:
        resp = self.configmap_service_api.update_configmap(configmap.name, body=ConfigmapServiceUpdateBody(
            data=configmap.data,
            labels=configmap.labels,
        ))
        return resp

    def list_configmaps(self) -> typing.List[V1Configmap]:
        resp = self.configmap_service_api.list_configmaps()
        return resp.configmaps or []

    def get_configmap(self, name: str) -> V1Configmap:
        resp = self.configmap_service_api.get_configmap(name)
        return resp

    def delete_configmap(self, name: str) -> None:
        self.configmap_service_api.delete_configmap(name)

    def list_queue(self, app_name: str, namespace: str) -> typing.List[V1ListRequestQueuesResponseRequestQueue]:
        resp = self.app_service_api.list_request_queues(name=app_name, namespace=namespace)
        return resp.queues

    def list_events(self, app_name: str, namespace: str) -> typing.List[V1Event]:
        resp = self.app_service_api.list_app_events(name=app_name, namespace=namespace)
        return resp.events

    def list_regions(self) -> typing.List[str]:
        return self.resources_service_api.list_regions().regions

    def list_gpus(self) -> typing.List[str]:
        return self.resources_service_api.list_gpu_model().gpus

    def list_cpus(self) -> typing.List[str]:
        return self.resources_service_api.list_cpu_model().cpus
