import sys
from everai.utils.cmd import run_command
from typing import Tuple, List, Dict
from everai.utils.verbose import verbose_print
from everai.constants import BUILDER
import subprocess
from threading import Thread


class DockerManager:
    def __init__(
            self,
            repository: str = None,
            labels: Dict[str, str] = None,
            platforms: List[str] = None,
            dockerfile: str = "Dockerfile",
            builder: str = BUILDER,
    ):
        self.platforms: List[str] = []
        platforms = platforms or ['linux/amd64', 'linux/arm64']
        for platform in platforms:
            if 'x86_64' in platform:
                platform = platform.replace('x86_64', 'amd64')

            self.platforms.append(platform)

        self.repository = repository
        self.dockerfile = dockerfile
        self.builder = builder
        self.labels = labels

    def check_docker(self) -> Tuple:
        verbose_print(f'system platform: {sys.platform}')
        if sys.platform == 'win32':
            out = run_command('where.exe docker')
        elif sys.platform == 'darwin' or sys.platform == 'linux':
            out = run_command('which docker')
        else:
            raise Exception(f'Unsupported platform: {sys.platform}')

        verbose_print('check_docker:', out)
        if 'docker' in out.strip():
            return True, None

        return False, self.__docker_install_prompt()

    def check_docker_buildx(self) -> Tuple:
        out = run_command('docker buildx version')
        verbose_print('check_docker_buildx: ', out)
        if 'docker/buildx' in out.strip() or 'docker buildx' in out.strip():
            return True, None

        return False, self.__docker_buildx_install_prompt()

    def docker_buildx_platform_support(self) -> Tuple:
        out = run_command('docker buildx ls')
        check_through = True
        for platform in self.platforms:
            if platform not in out:
                check_through = False

        if check_through:
            return True, None
        return False, self.__docker_buildx_platform_install_prompt()

    def check_docker_environment(self) -> Tuple:
        ok, prompt = self.check_docker()
        if ok is False:
            return ok, prompt

        ok, prompt = self.check_docker_buildx()
        if ok is False:
            return ok, prompt

        ok, prompt = self.docker_buildx_platform_support()
        if ok is False:
            return ok, prompt

        return ok, None

    def create_builder(self):
        create_cmd = f'docker buildx create --name {self.builder}'
        verbose_print('create builder: ', create_cmd)
        stdout, stderr = run_command(create_cmd, need_stderr=True)
        verbose_print(f'create_docker_builder:[{stdout}]; err:[{stderr}]')
        if stderr is not None and len(stderr) > 0:
            raise Exception(stderr)
        return

    def check_builder(self) -> bool:
        stdout = run_command('docker buildx ls')
        for line in stdout.splitlines():
            for v in line.split():
                if v.startswith(self.builder):
                    return True

        return False

    def build_from_content(self, dockerfile_content: str):
        if self.repository is None or len(self.repository) <= 0:
            raise Exception('Image repository address is empty')

        docker_build_cmd = ['docker', 'buildx', 'build', '-f', '-', '-t', self.repository]
        if self.builder is not None:
            docker_build_cmd.extend(['--builder', self.builder])

        if self.labels is not None and len(self.labels) > 0:
            for k, v in self.labels.items():
                docker_build_cmd.extend(['--label', f'{k}={v}'])

        if self.platforms is not None and len(self.platforms) > 0:
            docker_build_cmd.append('--platform')
            str_platform = ','.join(str(elm) for elm in self.platforms)
            docker_build_cmd.append(str_platform)

        docker_build_cmd.extend(['.', '--push'])

        verbose_print('dockerfile content:', dockerfile_content)
        verbose_print(' '.join(docker_build_cmd))

        process = subprocess.Popen(
            docker_build_cmd,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print('Starting image build...')
        process.stdin.write(dockerfile_content.encode())
        process.stdin.close()
        error_info = []

        def reader(pipe):
            with pipe:
                nonlocal error_info
                for l in iter(lambda: pipe.readline(), b''):
                    reader_line = l.decode('utf-8').strip()
                    if 'ERROR' in reader_line:
                        error_info.append(reader_line)
                    verbose_print(reader_line)

        Thread(target=reader, args=[process.stdout]).start()
        Thread(target=reader, args=[process.stderr]).start()

        process.wait()
        if process.returncode != 0:
            verbose_print('Docker build failed:\n', '\n'.join(error_info))
            raise Exception('Docker build failed:\n', '\n'.join(error_info))

    def __docker_buildx_install_prompt(self) -> str:
        return 'Your need install buildx, please visit https://docs.docker.com/build/architecture/#install-buildx'

    def __docker_buildx_platform_install_prompt(self) -> str:
        sudo_v = ''
        if sys.platform == 'linux':
            sudo_v = 'sudo '
        return (f'Cross-platform compilation is currently required, '
                f'please run `{sudo_v}docker run --privileged --rm tonistiigi/binfmt --install all`')

    def __docker_install_prompt(self) -> str:
        linux_v = ''
        if sys.platform == 'linux':
            linux_v = (', after installed docker, visit '
                       'https://docs.docker.com/engine/security/rootless/')

        return ('Your need install docker, please visit https://docs.docker.com/engine/install/'
                + linux_v)

