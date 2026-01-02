from everai.commands.command import ClientCommand, setup_subcommands
from argparse import _SubParsersAction
from everai.commands.secret.create import CreateCommand
from everai.commands.secret.delete import DeleteCommand
from everai.commands.secret.list import ListCommand
from everai.commands.secret.get import GetCommand
from everai.commands.secret.update import UpdateCommand


class SecretCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        secret_parser = parser.add_parser('secret',
                                          aliases=['secrets', 'sec', 's'],
                                          help='Manage secrets')
        secret_subparser = secret_parser.add_subparsers(help="Secret command help")

        setup_subcommands(secret_subparser, [
            CreateCommand,
            DeleteCommand,
            ListCommand,
            GetCommand,
            UpdateCommand,
        ])

        secret_parser.set_defaults(func=SecretCommand)
        SecretCommand.parser = secret_parser

    def run(self):
        SecretCommand.parser.print_help()
        return
