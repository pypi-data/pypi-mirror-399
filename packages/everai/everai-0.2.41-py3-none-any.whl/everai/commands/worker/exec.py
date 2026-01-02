import argparse
from typing import (
    List,
    Optional,
)

from everai.app import App, AppManager
from everai.commands.command import ClientCommand, command_error, ListDisplayer
from argparse import _SubParsersAction, Namespace
from everai.worker import Worker
import sys

class ExecCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args: Namespace):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        exec_parser = parser.add_parser('exec', help='Run a command in a running worker')
        exec_parser.add_argument('--interactive', '-i', action='store_true',
                                 help='Keep STDIN open even if not attached')
        exec_parser.add_argument('--tty', '-t', action='store_true',
                                 help='Allocate a pseudo-TTY, just for compatible client, no effect')
        exec_parser.add_argument('worker', type=str,
                                 help='worker id')

        exec_parser.add_argument('command', type=str,
                                 help='command')

        exec_parser.add_argument('args', nargs=argparse.REMAINDER,
                                 help='arguments for command in worker')

        exec_parser.set_defaults(func=ExecCommand)
        ExecCommand.parser = exec_parser

    @command_error
    def run(self):
        commands = [self.args.command]
        if self.args.args is not None and len(self.args.args) > 0:
            commands.extend(self.args.args)
        if sys.platform.startswith('win'):
            print("Windows systems do not support tty, use wsl or a UniX-like subsystem")
            return

        AppManager().exec_worker(
            worker_id=self.args.worker,
            commands=commands,
            interactive=self.args.interactive,
        )
