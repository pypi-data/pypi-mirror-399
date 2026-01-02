import _thread
import threading

from typing import (
    List,
    Dict,
    Tuple,
    Optional,
    Callable
)

from docker.utils import config

from everai import constants
from everai.app.app import App
from everai.app.app_runtime import AppRuntime
from everai.app.autocaler_handler import register_autoscaling_handler
from everai.configmap import ConfigMapManager, ConfigMap
from everai.constants import EVERAI_FORCE_PULL_VOLUME
from everai.event import Event
from everai.namespace import Namespace
from everai.queue import QueuedRequest
from everai.runner import must_find_target
from everai.api import API
from everai.secret import Secret, SecretManager
from everai.utils.verbose import verbose_print
from everai.volume import Volume, VolumeManager
from gevent.pywsgi import WSGIServer
import gevent.signal
import signal
import sys

from flask import Flask, Blueprint, Response

from everai.worker.worker import Worker
from generated.volumes.exceptions import NotFoundException as VolumeNotFoundException

import docker
from docker.constants import DEFAULT_TIMEOUT_SECONDS, DEFAULT_MAX_POOL_SIZE


autoscaling_warning = """
You are deploying an app without autoscaling_policy, 
that will cause the app to run only one worker and always one worker,
if you want to setup an autoscaling_policy for this app after deploy,
you must rebuild image and upgrade it use everai app upgrade --image
"""


class AppManager:
    def __init__(self):
        self.api = API()
        self.secret_manager = SecretManager()
        self.configmap_manager = ConfigMapManager()
        self.volume_manager = VolumeManager()
        self._running = False

    def create(self, app: App, dry_run: bool = False) -> App:
        verbose_print(app.to_yaml())
        if not dry_run:
            resp = self.api.create_app(app=app.to_proto())
            resp_app = App.from_proto(resp)
            verbose_print(resp_app.to_yaml())
            return resp_app
        else:
            return app

    def update(self, app: App, dry_run: bool = False) -> App:
        verbose_print(app.to_yaml())
        if not dry_run:
            resp = self.api.update_app(app=app.to_proto())
            resp_app = App.from_proto(resp)
            verbose_print(resp_app.to_yaml())
            return resp_app
        else:
            return app

    def pause(self, app_name: str, namespace: str):
        self.api.pause_app(name=app_name, namespace=namespace)

    def resume(self, app_name: str, namespace: str):
        self.api.resume_app(name=app_name, namespace=namespace)

    def prepare_secrets(self, app: App, runtime: AppRuntime):
        prepared_secrets: Dict[str, Secret] = {}
        for name in app.secret_requests or []:
            secret = self.secret_manager.get(name=name)
            prepared_secrets[secret.name] = secret
        runtime.secrets = prepared_secrets

    def prepare_configmaps(self, app: App, runtime: AppRuntime):
        prepared_configmaps: Dict[str, ConfigMap] = {}
        for name in app.configmap_requests or []:
            configmap = self.configmap_manager.get(name=name)
            prepared_configmaps[configmap.name] = configmap
        runtime.configmaps = prepared_configmaps

    def prepare_volumes(self, app: App, runtime: AppRuntime):
        prepared_volumes: Dict[str, Volume] = {}
        for req in app.volume_requests or []:
            try:
                volume = self.volume_manager.get(req.name)
                prepared_volumes[volume.name] = volume
            except VolumeNotFoundException as e:
                raise e
                # if req.create_if_not_exists:
                #     volume = self.volume_manager.create_volume(name=req.name)
                # else:
                #     raise e

            volume.set_path(self.volume_manager.volume_path(volume.id))
            prepared_volumes[volume.name] = volume

            if EVERAI_FORCE_PULL_VOLUME:
                self.volume_manager.pull(volume.name)
        # app.prepared_volumes = prepared_volumes
        runtime.volumes = prepared_volumes

    def everai_handler(self, flask_app: Flask):
        everai_blueprint = Blueprint('everai', __name__, url_prefix='/-everai-')

        @everai_blueprint.route('/healthy', methods=['GET'])
        def healthy():
            status = 200 if self._running else 503
            message = 'Running' if self._running else 'Preparing'
            return Response(message, status=status, mimetype='text/plain')

        flask_app.register_blueprint(everai_blueprint)

    def run_autoscaling(self, app: Optional[App] = None, *args, **kwargs):
        app = app or must_find_target(target_type=App)

        print("------ run_autoscaling ------ ")
        flask_app = Flask(app.name)
        app, runtime = self.prepare_secrets_configmaps(app)
        runtime.start_update()

        register_autoscaling_handler(flask_app, app)
        AppManager.start_http_server(flask_app=flask_app, cb=lambda: runtime.stop_update(), *args, **kwargs)

    @staticmethod
    def start_debug_http_server(flask_app: Flask, cb: Optional[Callable[[], None]] = None,
                                *args, **kwargs):

        port = kwargs.pop('port', 8866)
        listen = kwargs.pop('listen', '0.0.0.0')

        flask_app.run(host=listen, port=port, debug=False)
        if cb is not None:
            cb()

    @staticmethod
    def start_http_server(flask_app: Flask, cb: Optional[Callable[[], None]] = None, *args,
                          **kwargs):
        if not constants.EVERAI_PRODUCTION_MODE:
            return AppManager.start_debug_http_server(flask_app=flask_app, cb=cb, *args, **kwargs)

        port = kwargs.pop('port', 8866)
        listen = kwargs.pop('listen', '0.0.0.0')

        http_server = WSGIServer((listen, port), flask_app)

        def graceful_stop(*args, **kwargs):
            print(f'Got stop signal, worker do final clear')
            if http_server.started:
                http_server.stop()
            if cb is not None:
                cb()

        gevent.signal.signal(signal.SIGTERM, graceful_stop)
        gevent.signal.signal(signal.SIGINT, graceful_stop)

        http_server.serve_forever()
        # flask_app.run(host=listen, port=port, debug=False)

    def run(self, app: Optional[App] = None, *args, **kwargs):
        app = app or must_find_target(target_type=App)
        app.runtime = AppRuntime()
        # start prepare thread
        prepare_thread = threading.Thread(target=self.prepare,
                                          args=(app,),
                                          kwargs=dict(
                                              is_prepare_mode=False,
                                          ))
        prepare_thread.start()

        # self.prepare(app, False)
        # print('prepare finished')

        flask_app = Flask(app.name)
        self.everai_handler(flask_app)
        app.service.create_handler(flask_app)

        def final_clear():
            app.do_clear()
            app.runtime.stop_update()

        if threading.current_thread().name == 'MainThread':
            print('start http server')
            AppManager.start_http_server(flask_app=flask_app, cb=final_clear, *args, **kwargs)

    def prepare_secrets_configmaps(self,
                                   app: Optional[App] = None) -> Tuple[App, AppRuntime]:
        app = app or must_find_target(target_type=App)
        runtime = AppRuntime()
        self.prepare_secrets(app, runtime)
        self.prepare_configmaps(app, runtime)
        runtime.volume_manager = self.volume_manager
        runtime.secret_manager = self.secret_manager
        runtime.configmap_manager = self.configmap_manager
        runtime.is_prepare_mode = False
        runtime.volumes = []
        app.runtime = runtime
        return app, runtime

    def prepare(self,
                app: Optional[App] = None,
                is_prepare_mode: bool = True,
                *args, **kwargs):
        # traceback.print_stack()
        try:
            app, runtime = self.prepare_secrets_configmaps(app)

            runtime.is_prepare_mode = is_prepare_mode
            self.prepare_volumes(app, runtime)

            app.do_prepare()
            print('prepare finished')
            if len(app.service.routes) > 0 and not is_prepare_mode:
                self._running = True
                runtime.start_update()
        except Exception as e:
            print(f'prepare got error ${e}')
            _thread.interrupt_main()

    def delete(self, app_name: str, namespace: str) -> None:
        self.api.delete_app(app_name, namespace=namespace)

    def list(self, namespace: Optional[str] = 'None', all_namespaces: bool = False) -> List[App]:
        return [App.from_proto(app) for app in self.api.list_apps(namespace=namespace, all_namespaces=all_namespaces)]

    def get(self, app_name: str, namespace: str) -> App:
        v1app = self.api.get_app(app_name, namespace=namespace)
        return App.from_proto(v1app)

    def list_namespaces(self) -> List[Namespace]:
        return [Namespace.from_proto(x) for x in self.api.list_namespaces()]

    def get_namespace(self, name: str) -> Namespace:
        return Namespace.from_proto(self.api.get_namespace(name))

    def create_namespace(self, name: str) -> Namespace:
        return Namespace.from_proto(self.api.create_namespace(name))

    def delete_namespace(self, name: str):
        self.api.delete_namespace(name)

    def list_worker(self,
                    app_name: str,
                    namespace: Optional[str] = 'default',
                    show_all: bool = False,
                    recent_days: int = 2,
                    ) -> List[Worker]:
        workers = self.api.list_worker(
            app_name=app_name,
            namespace=namespace,
            show_all=show_all,
            recent_days=recent_days,
        )
        return [Worker.from_proto(worker) for worker in workers]
    
    def exec_worker(self, worker_id: str, commands: List[str], interactive: bool = False):
        assert worker_id and len(worker_id) > 0
        assert commands is not None and len(commands) > 0

        def get_client():
            timeout = DEFAULT_TIMEOUT_SECONDS
            max_pool_size = DEFAULT_MAX_POOL_SIZE
            version = None
            use_ssh_client = False
            c = docker.DockerClient(
                timeout=timeout,
                max_pool_size=max_pool_size,
                version=version,
                use_ssh_client=use_ssh_client,
                base_url=constants.EVERAI_EXEC_ENTRYPOINT,
                tls=not constants.EVERAI_EXEC_DISABLE_TLS,
            )
            return c

        old_f = config.load_general_config

        def new_f(config_path=None):
            result = old_f(config_path)
            if isinstance(result, dict):
                result['HttpHeaders'] = {
                    'Authorization': f'Bearer {self.api.token}',
                    constants.HEADER_WORKER_ID: worker_id,
                }
            return result

        config.load_general_config = new_f

        cli = get_client()
        cmd = ' '.join(commands)
        if not sys.platform.startswith('win'):
            import dockerpty
            dockerpty.exec_command(cli.api, worker_id, cmd, interactive=interactive)

        config.load_general_config = old_f

    def list_queue(self, app_name: str, namespace: str) -> List[QueuedRequest]:
        requests = self.api.list_queue(app_name, namespace=namespace) or []
        return [QueuedRequest.from_proto(req) for req in requests]

    def list_events(self, app_name: str, namespace: str) -> List[Event]:
        events = self.api.list_events(app_name, namespace=namespace) or []
        return [Event.from_proto(ev) for ev in events]

