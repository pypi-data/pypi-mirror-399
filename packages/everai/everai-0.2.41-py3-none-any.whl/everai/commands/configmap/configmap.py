from everai.commands.command import ClientCommand, setup_subcommands
from argparse import _SubParsersAction
from everai.commands.configmap.create import CreateCommand
from everai.commands.configmap.delete import DeleteCommand
from everai.commands.configmap.list import ListCommand
from everai.commands.configmap.get import GetCommand
from everai.commands.configmap.update import UpdateCommand


class ConfigMapCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        configmap_parser = parser.add_parser('configmap',
                                             aliases=['cm', 'configmaps'],
                                             help='Manage configmaps')
        configmap_subparser = configmap_parser.add_subparsers(help="Configmap command help")

        setup_subcommands(configmap_subparser, [
            CreateCommand,
            DeleteCommand,
            ListCommand,
            GetCommand,
            UpdateCommand,
        ])

        configmap_parser.set_defaults(func=ConfigMapCommand)
        ConfigMapCommand.parser = configmap_parser

    def run(self):
        ConfigMapCommand.parser.print_help()
        return
