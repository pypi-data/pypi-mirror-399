from __future__ import annotations

import yaml
from everai_autoscaler.builtin import SimpleAutoScaler, BuiltinFactory

from everai import constants
from everai.app.app_versioned import AppVersionedMixin
from everai.placeholder import Placeholder, PlaceholderValue
from everai.utils.k8s_sort_key import sort_key
from everai.utils.show_mixin import ShowMixin, TableField
from everai_autoscaler.model import AutoScaler, BuiltinAutoScaler, Decorators, Decorator
from everai_autoscaler.builtin.is_builtin import is_builtin

from everai.image import Image, BasicAuth
from everai.environment import Environment
from everai.resource_requests.resource_requests import ResourceRequests
from everai.app.volume_request import VolumeRequest
from typing import (
    List, Optional, Dict, TypeVar, Tuple, Any, IO
)

from everai.volume import regular_name
from generated.apps import (
    V1App,
    V1AppV1Alpha1,
    V1Metadata,
    V1ImagePullSecrets,
    V1Volume as V1AppVolume,
    VolumeVolumeItem,
    VolumeSecretItem,
    VolumeConfigMapItem,
    V1Environment,
    V1AppSpecV1Alpha1,
    V1Probe,
    V1HttpGet, V1Autoscaler, AutoscalerContainerScaler, AutoscalerBuiltinScaler, Commonv1Value, V1EntryPath, V1HttpPost,
    AutoscalerDecorators, AutoscalerDecoratorsItem,
)
from everai.app.app_runner import AppRunnerMixin
from everai.utils.datetime import format_datetime

T = TypeVar('T')


class App(AppRunnerMixin, AppVersionedMixin, ShowMixin):
    table_fields: List[TableField] = [
        TableField('name'),
        TableField('namespace'),
        TableField('status', picker=lambda dt: dt.status.status.value.removeprefix('STATUS_')),
        TableField('workers', picker=lambda dt: f'{dt.status.ready_worker or 0}/{dt.status.desired_worker or 0}'),
        TableField('created_at', formatter=lambda dt: format_datetime(dt)),
    ]

    wide_table_extra_fields: List[TableField] = [
        TableField('updated_at', formatter=lambda dt: format_datetime(dt)),
    ]

    @staticmethod
    def _get_image_info(image: Optional[Image]) -> Tuple[str, Optional[V1ImagePullSecrets]]:
        if image is None:
            return "", None

        image_path = image.image

        if image is None or image.auth is None:
            return image_path, None
        if not isinstance(image.auth, BasicAuth):
            raise ValueError(f'unsupported auth method {type(image.auth)}')

        return image_path, V1ImagePullSecrets(
            username=image.auth.username.to_proto(),
            password=image.auth.password.to_proto(),
        )

    # @staticmethod
    # def _get_envs(envs: Optional[List[Environment]]) -> Optional[List[V1Environment]]:
    #     if envs is None:
    #         return []
    #
    #     result = []
    #     for env in envs:
    #         item = V1Environment(
    #             name=env.name,
    #             env_value=env.value.to_proto(),
    #         )
    #         result.append(item)
    #
    #     return result

    @staticmethod
    def _get_volumes(
            volume_requests: Optional[List[VolumeRequest]] = None,
            secret_requests: Optional[List[str]] = None,
            configmap_requests: Optional[List[str]] = None,
    ) -> List[V1AppVolume]:
        volumes_volumes = [
            V1AppVolume(
                name=regular_name(v.name),
                volume=VolumeVolumeItem(volume=regular_name(v.name)),
            )
            for v in volume_requests or []
        ]
        secrets_volumes = [
            V1AppVolume(
                name=v,
                secret=VolumeSecretItem(secret_name=v),
            )
            for v in secret_requests or []
        ]
        configmap_requests = [
            V1AppVolume(
                name=v,
                config_map=VolumeConfigMapItem(name=v),
            )
            for v in configmap_requests or []
        ]
        result = sum([volumes_volumes, secrets_volumes, configmap_requests], [])
        return None if result is None or len(result) == 0 else result

    @classmethod
    def _make_decorator(cls,
                        decorators: Optional[List[Decorator]]
                        ) -> Optional[List[AutoscalerDecoratorsItem]]:
        if decorators is None or len(decorators) == 0:
            return None

        result = []
        for decorator in decorators:
            item = AutoscalerDecoratorsItem(name=decorator.name)
            arguments = {}
            for k, v in decorator.arguments.items():
                if callable(v):
                    if not isinstance(v, Placeholder):
                        raise TypeError(f'Unsupported argument {k} type {type(v)} for autoscaler')
                    arguments[k] = PlaceholderValue(placeholder=v).to_proto()
                else:
                    arguments[k] = PlaceholderValue(value=str(v)).to_proto()

            item.arguments = arguments
            result.append(item)

        return result

    @classmethod
    def _make_decorators(cls, decorators: Optional[Decorators] = None) -> Optional[AutoscalerDecorators]:
        if decorators is None:
            return None
        return AutoscalerDecorators(
            arguments=cls._make_decorator(decorators.arguments),
            factors=cls._make_decorator(decorators.factors),
        )

    @classmethod
    def _make_autoscaler(cls,
                         autoscaler: AutoScaler,
                         image: Optional[str],
                         image_pull_secrets: V1ImagePullSecrets,
                         volumes: Optional[List[V1AppVolume]]
                         ) -> Optional[V1Autoscaler]:
        if autoscaler is None:
            return None

        if is_builtin(autoscaler) and constants.EVERAI_DISABLE_BUILTIN is None:
            assert isinstance(autoscaler, BuiltinAutoScaler)
            target_dict = {}
            for k, v in autoscaler.autoscaler_arguments().items():
                if callable(v):
                    if not isinstance(v, Placeholder):
                        raise TypeError(f'Unsupported argument {k} type {type(v)} for autoscaler')
                    target_dict[k] = PlaceholderValue(placeholder=v).to_proto()
                else:
                    target_dict[k] = PlaceholderValue(value=str(v)).to_proto()

            return V1Autoscaler(
                scheduler=autoscaler.scheduler_name(),
                builtin=AutoscalerBuiltinScaler(
                    name=autoscaler.autoscaler_name(),
                    arguments=target_dict,
                    decorators=cls._make_decorators(autoscaler.decorators)
                ),
            )
        else:
            return V1Autoscaler(
                scheduler=autoscaler.scheduler_name(),
                container=AutoscalerContainerScaler(
                    image=image,
                    image_pull_secrets=image_pull_secrets,
                    command=['everai', 'autoscaler'],
                    entry_path=V1EntryPath(
                        http_post=V1HttpPost(path='/-everai-/autoscaler')
                    ),
                    port=80,
                    volumes=[v for v in volumes if v.secret is not None or v.config_map is not None],
                ),
            )

    def __init__(self,
                 name: str,
                 resource_requests: Optional[ResourceRequests] = None,
                 namespace: str = 'default',
                 labels: Optional[Dict[str, str]] = None,
                 image: Optional[Image] = None,
                 request_quota: Optional[int] = None,
                 autoscaler: Optional[AutoScaler] = None,
                 secret_requests: Optional[List[str]] = None,
                 configmap_requests: Optional[List[str]] = None,
                 volume_requests: Optional[List[VolumeRequest]] = None,
                 # env: Optional[List[Environment]] = None,
                 *args, **kwargs):
        resource_requests = resource_requests or ResourceRequests()
        image_name, image_pull_secrets = App._get_image_info(image)
        volumes = App._get_volumes(volume_requests, secret_requests, configmap_requests)
        # environments = App._get_envs(env)

        self._autoscaler = autoscaler

        _v1_autoscaler = self._make_autoscaler(autoscaler, image_name, image_pull_secrets, volumes)

        self._app = V1App(
            app_v1alpha1=V1AppV1Alpha1(
                metadata=V1Metadata(
                    name=name,
                    namespace=namespace,
                    labels=labels,
                ),
                spec=V1AppSpecV1Alpha1(
                    image=image.image if image is not None else None,
                    image_pull_secrets=image_pull_secrets,
                    volume_mounts=None,
                    env=None,
                    command=None,
                    port=None,
                    readiness_probe=V1Probe(http_get=V1HttpGet(path='/-everai-/healthy')),
                    volumes=volumes,
                    resource=resource_requests.to_proto() if resource_requests is not None else None,
                    route_auth_type=None,
                    route_public_key=None,
                    autoscaler=_v1_autoscaler,
                    request_quota=request_quota,
                ),
                status=None,
            )
        )

    @staticmethod
    def from_proto(v1app: V1App) -> App:
        app = App(name='', resource_requests=ResourceRequests())
        app._app = v1app
        if app.metadata.namespace is None or app.metadata.namespace == '':
            app.metadata.namespace = 'default'
        return app

    def to_proto(self) -> V1App:
        return self._app

    def to_dict(self) -> Dict[str, Any]:
        data = self.get_to_dict()
        data.update(dict(
            version="everai/v1alpha1",
            kind="App",
        ))

        return dict(sorted(data.items(), key=lambda item: sort_key(item[0])))

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> App:
        version = data.pop('version', None)
        if version is None:
            raise ValueError("version is required")

        kind = data.pop("kind", None)
        if kind is None:
            raise ValueError("version is required")
        if kind != 'App':
            raise ValueError('kind should be "App"')

        if version == "everai/v1alpha1":
            data = App.convert_from_dict(data, "v1alpha1")

            v1alpha1 = V1AppV1Alpha1.from_dict(data)
            return App.from_proto(V1App(app_v1alpha1=v1alpha1))
        else:
            raise ValueError(f"unsupported version {version}")

    def to_yaml(self) -> str:
        d = self.to_dict()
        return yaml.dump(d, default_flow_style=False, sort_keys=False)

    @staticmethod
    def from_yaml_file(filename: str) -> App:
        with open(filename, 'r') as f:
            return App.from_yaml_stream(f)

    @staticmethod
    def from_yaml_stream(stream: IO) -> App:
        data = yaml.safe_load(stream)
        return App.from_dict(data)

    @property
    def volume_requests(self) -> List[VolumeRequest]:
        return [VolumeRequest(x.volume.volume) for x in self.spec.volumes or [] if x.volume is not None]

    @property
    def secret_requests(self) -> List[str]:
        return [x.secret.secret_name for x in self.spec.volumes or [] if x.secret is not None]

    @property
    def configmap_requests(self) -> List[str]:
        return [x.config_map.name for x in self.spec.volumes or [] if x.config_map is not None]

    @property
    def autoscaler(self) -> AutoScaler:
        if self.spec.autoscaler is None:
            return SimpleAutoScaler()
        elif self.spec.autoscaler.container is not None:
            return self._autoscaler
        elif self.spec.autoscaler.builtin is not None:
            BuiltinFactory().create(
                self.spec.autoscaler.builtin.name,
                # self.spec.autoscaler.builtin.arguments,
                {k: PlaceholderValue.from_proto(v)() for k, v in self.spec.autoscaler.builtin.arguments.items()}
            )
            return self._autoscaler
        else:
            raise ValueError(f"invalid autoscaler")
