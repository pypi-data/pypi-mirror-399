import datetime
import threading
import typing

from everai.app.context import Context
from everai.configmap import ConfigMap, ConfigMapManager
from everai.logger import logger
from everai.secret import Secret, SecretManager
from everai.utils.singleton import Singleton
from everai.volume import Volume, VolumeManager
from timeloop import Timeloop


tl: Timeloop = Timeloop()


class AppRuntime(metaclass=Singleton):
    secrets: typing.Dict[str, Secret]
    configmaps: typing.Dict[str, ConfigMap]
    volumes: typing.Dict[str, Volume]

    is_prepare_mode: bool

    volume_manager: VolumeManager
    secret_manager: SecretManager
    configmap_manager: ConfigMapManager

    _lock: threading.Lock
    _update_running: bool

    # def __new___(cls, *args, **kwargs):
    #     if not hasattr(cls, 'instance'):
    #         cls.instance = super(AppRuntime, cls).__new__(cls, *args, **kwargs)
    #     return cls.instance

    def __init__(self):
        self._lock = threading.Lock()
        self.tl = Timeloop()
        self._update_running = False

        self.secrets = {}
        self.configmaps = {}
        self.volumes = {}
        self.volume_manager = VolumeManager()
        self.secret_manager = SecretManager()
        self.configmap_manager = ConfigMapManager()
        self.is_prepare_mode = False
        print('AppRuntime construct')
        tl.job(interval=datetime.timedelta(seconds=30))(self._update_routine)

    def context(self) -> Context:
        return Context(secrets=self.secrets,
                       configmaps=self.configmaps,
                       volumes=self.volumes,
                       volume_manager=self.volume_manager,
                       is_prepare_mode=self.is_prepare_mode)

    def update_secrets(self, secrets: typing.List[str]):
        try:
            prepared_secrets: typing.Dict[str, Secret] = {}
            for name in secrets:
                secret = self.secret_manager.get(name=name)
                prepared_secrets[secret.name] = secret
            with self._lock:
                self.secrets = prepared_secrets
        except Exception as e:
            logger.error(f'update secrets got error, {e}, ignore update')

    def update_configmaps(self, configmaps: typing.List[str]):
        try:
            prepared_configmaps: typing.Dict[str, ConfigMap] = {}
            for name in configmaps:
                configmap = self.configmap_manager.get(name=name)
                prepared_configmaps[name] = configmap
            with self._lock:
                self.configmaps = prepared_configmaps
        except Exception as e:
            logger.error(f'update configmaps got error, {e}, ignore update')

    @property
    def update_running(self) -> bool:
        return self._update_running

    def _update_routine(self):
        print('enter update routine')
        secrets = list(self.secrets.keys())
        configmaps = list(self.configmaps.keys())
        self.update_secrets(secrets)
        self.update_configmaps(configmaps)

    def start_update(self):
        print('start_update')
        with self._lock:
            if not self._update_running:
                tl.start()
                self._update_running = True
                print("update job started")

    def stop_update(self):
        print('stop_update')
        with self._lock:
            if self._update_running:
                tl.stop()
                self._update_running = False
                print("update job stopped")
