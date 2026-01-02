from __future__ import annotations
import subprocess
import typing
from contextlib import contextmanager
from .image import Image, Auth
from abc import ABC, abstractmethod
from everai.utils.verbose import verbose_print
from threading import Thread
from everai.utils.docker_manager import DockerManager
from everai.constants import *


BuildAction = typing.Callable[[], None]


class Builder(ABC):
    pre_build_funcs: typing.List[BuildAction]
    post_build_funcs: typing.List[BuildAction]

    def __init__(self,
                 repository: str,
                 labels: typing.Optional[typing.Dict[str, str]] = None,
                 platform: typing.List[str] = None,
                 ):
        self.labels = labels or {}
        self.platform = platform or ['linux/arm64', 'linux/x86_64']
        self.repository = repository
        self.pre_build_funcs = []
        self.post_build_funcs = []

    @staticmethod
    def from_dockerfile(
            dockerfile: str,
            *args, **kwargs
    ):
        return LocalBuilder(dockerfile=dockerfile, *args, **kwargs)

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError()

    def pre_build(self, action: BuildAction) -> Builder:
        self.pre_build_funcs.append(action)
        return self

    def post_build(self, action: BuildAction) -> Builder:
        self.post_build_funcs.append(action)
        return self

    def do_pre_build(self):
        for action in self.pre_build_funcs:
            action()

    def do_post_build(self):
        for action in self.post_build_funcs:
            action()

    @contextmanager
    def do_action(self):
        self.do_pre_build()
        yield None
        self.do_post_build()


class LocalBuilder(Builder):
    def __init__(self, dockerfile: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dockerfile = dockerfile

    def run(self, *args, **kwargs):
        with super().do_action():
            docker_manager = DockerManager(
                repository=self.repository,
                platforms=self.platform,
                dockerfile=self.dockerfile,
                builder=BUILDER,
                labels=self.labels,
            )

            ok, prompt = docker_manager.check_docker_environment()
            if ok is False:
                print(prompt)
                return
            if docker_manager.check_builder() is False:
                docker_manager.create_builder()

            dockerfile_content = ''
            have_entrypoint = False
            with open(self.dockerfile, 'r') as f:
                for line in f.readlines():
                    if line.strip().startswith('ENTRYPOINT'):
                        dockerfile_content += 'ENTRYPOINT ["ever", "run"]\n'
                        have_entrypoint = True
                    else:
                        dockerfile_content += line

            if have_entrypoint is False:
                dockerfile_content += '\nENTRYPOINT ["ever", "run"]\n'

            docker_manager.build_from_content(dockerfile_content=dockerfile_content)
            print(f'Image build successful, {self.repository}')


class BuilderMixin:
    @contextmanager
    def image_builder(self) -> Builder:
        # builder = Builder()
        # yield builder
        pass
