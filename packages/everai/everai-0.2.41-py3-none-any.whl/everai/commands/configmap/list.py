from everai.commands.command import ClientCommand, command_error, ListDisplayer
from argparse import _SubParsersAction

from everai.configmap import ConfigMapManager, ConfigMap


class ListCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        list_parser = parser.add_parser('list', aliases=['ls'], help='List configmaps')
        ListDisplayer.add_output_to_parser(list_parser)
        list_parser.set_defaults(func=ListCommand)

    @command_error
    def run(self):
        configmaps = ConfigMapManager().list()
        ListDisplayer[ConfigMap](configmaps).show_list(self.args.output)

