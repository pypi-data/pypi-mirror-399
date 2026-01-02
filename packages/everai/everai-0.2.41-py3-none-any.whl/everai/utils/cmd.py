import subprocess
import os
import typing
from contextlib import contextmanager

Command = typing.Union[str, typing.List[str]]


def run_command(command: Command, need_stderr: bool = False) -> typing.Union[str, tuple[str, str]]:
    shell = True if isinstance(command, str) else False
    # command = command.split()
    cmd_resp = subprocess.run(
        command,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        encoding='utf-8',
        errors='replace',
        cwd=os.getcwd(),
        input='',
        shell=shell,
    )
    if need_stderr:
        return cmd_resp.stdout, cmd_resp.stderr
    return cmd_resp.stdout


@contextmanager
def run_command_interactive(command: Command) -> (
        typing.Generator)[tuple[typing.IO[str], typing.IO[str], typing.IO[str]], None, None]:
    shell = True if isinstance(command, str) else False
    with subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8',
        errors='replace',
        shell=shell
    ) as process:
        assert process.stdin is not None, "Subprocess is opened as subprocess.PIPE"
        assert process.stdout is not None, "Subprocess is opened as subprocess.PIPE"
        assert process.stderr is not None, "Subprocess is opened as subprocess.PIPE"
        yield process.stdin, process.stdout, process.stderr
