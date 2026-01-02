from everai.commands.command import ClientCommand, command_error
from argparse import _SubParsersAction
from everai.secret.secret_manager import SecretManager


class DeleteCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        delete_parser = parser.add_parser('delete', help='Delete secret')
        delete_parser.add_argument('name', help='The secret name')

        delete_parser.set_defaults(func=DeleteCommand)

    @command_error
    def run(self):
        SecretManager().delete(name=self.args.name)
        print('Secret deleted successfully')

