import everai.constants

from everai.commands.command import ClientCommand
from argparse import _SubParsersAction

from everai.commands.command import command_error


class ConfigCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        deploy_parser = parser.add_parser("config", help="Print current configuration")

        deploy_parser.set_defaults(func=ConfigCommand)

    @command_error
    def run(self):
        print('EVERAI_HOME', everai.constants.EVERAI_HOME)
        print('EVERAI_ENDPOINT', everai.constants.EVERAI_ENDPOINT)
        print('EVERAI_VOLUME_ROOT', everai.constants.EVERAI_VOLUME_ROOT)
