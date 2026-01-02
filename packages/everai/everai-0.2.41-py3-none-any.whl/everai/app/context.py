import typing

from werkzeug.local import LocalProxy
from contextvars import ContextVar

from everai.configmap import ConfigMap
from everai.secret import Secret
from contextlib import contextmanager
from typing import Optional
from everai.volume import Volume, VolumeManager
import everai.constants


class Context:
    secrets: typing.Dict[str, Secret]
    configmaps: typing.Dict[str, ConfigMap]
    volumes: typing.Dict[str, Volume]
    _volume_manager: VolumeManager
    _is_prepare_mode: bool

    def __init__(self,
                 secrets: Optional[typing.Dict[str, Secret]] = None,
                 configmaps: Optional[typing.Dict[str, ConfigMap]] = None,
                 volumes: Optional[typing.Dict[str, Volume]] = None,
                 volume_manager: VolumeManager = None,
                 is_prepare_mode: bool = False,
                 ):
        self.secrets = secrets or {}
        self.volumes = volumes or {}
        self.configmaps = configmaps or {}
        self._volume_manager = volume_manager
        self._is_prepare_mode = is_prepare_mode

    def add_secret(self, secret: Secret):
        if self.secrets.get(secret.name):
            raise ValueError(f'Key conflict {secret.name} when add_secret')
        self.secrets[secret.name] = secret

    def get_secret(self, name: str) -> Optional[Secret]:
        return self.secrets.get(name)

    def get_configmap(self, name: str) -> Optional[ConfigMap]:
        return self.configmaps.get(name)

    def add_volume(self, volume: Volume):
        if self.volumes.get(volume.name):
            raise ValueError(f'Key conflict {volume.name} when add_volume')
        self.volumes[volume.name] = volume

    def get_volume(self, name: str) -> Optional[Volume]:
        if name.count('/') == 0:
            return self.volumes.get(name)

        if name.count('/') != 1:
            raise ValueError(f'invalid volume name {name}')
        result = name.split("/")
        for k, v in self.volumes.items():
            if v.username == result[0] and v.name == result[1]:
                return v

        return None

    @property
    def volume_manager(self) -> VolumeManager:
        return self._volume_manager

    @property
    def is_prepare_mode(self) -> bool:
        return self._is_prepare_mode

    @property
    def is_in_cloud(self) -> bool:
        return everai.constants.EVERAI_IN_CLOUD == '1'


@contextmanager
def service_context(ctx: Context):
    a = _everai_context.set(ctx)
    yield ctx
    _everai_context.reset(a)


_everai_context: ContextVar[Context] = ContextVar("everai.context")

_no_context_msg = """
Working outside of everai context.
"""

context: Context = LocalProxy(  # type: ignore[assignment]
    _everai_context, None, unbound_message=_no_context_msg
)
