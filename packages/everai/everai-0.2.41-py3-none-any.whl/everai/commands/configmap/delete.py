from everai.commands.command import ClientCommand, command_error
from argparse import _SubParsersAction

from everai.configmap import ConfigMapManager


class DeleteCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        delete_parser = parser.add_parser('delete', help='Delete configmap')
        delete_parser.add_argument('name', help='The configmap name')

        delete_parser.set_defaults(func=DeleteCommand)

    @command_error
    def run(self):
        ConfigMapManager().delete(name=self.args.name)
        print(f'Configmap `{self.args.name}` deleted successfully')

