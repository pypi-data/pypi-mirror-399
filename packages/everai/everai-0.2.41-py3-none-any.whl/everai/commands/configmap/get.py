from everai.commands.command import ClientCommand, command_error, ListDisplayer
from argparse import _SubParsersAction

from everai.configmap import ConfigMapManager, ConfigMap
from everai.secret.secret_manager import SecretManager


class GetCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        get_parser = parser.add_parser('get', help='Get configmap')
        get_parser.add_argument('name', help='The configmap name')
        ListDisplayer.add_output_to_parser(get_parser)
        get_parser.set_defaults(func=GetCommand)

    @command_error
    def run(self):
        configmap = ConfigMapManager().get(name=self.args.name)
        ListDisplayer[ConfigMap](configmap).show_list(self.args.output)
