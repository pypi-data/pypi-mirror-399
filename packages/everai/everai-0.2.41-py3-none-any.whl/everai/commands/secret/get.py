from everai.commands.command import ClientCommand, command_error, ListDisplayer
from argparse import _SubParsersAction

from everai.secret import Secret
from everai.secret.secret_manager import SecretManager


class GetCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        get_parser = parser.add_parser('get', help='Get secret')
        get_parser.add_argument('name', help='The secret name')
        ListDisplayer.add_output_to_parser(get_parser)
        get_parser.set_defaults(func=GetCommand)

    @command_error
    def run(self):
        secret = SecretManager().get(name=self.args.name)
        ListDisplayer[Secret](secret).show_list(self.args.output)
