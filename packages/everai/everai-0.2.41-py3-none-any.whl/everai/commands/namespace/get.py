import logging

from everai.app import App, AppManager
from everai.commands.command import ClientCommand, command_error, ListDisplayer
from argparse import _SubParsersAction, Namespace
from everai.namespace import Namespace as EveraiNamespace
from generated.apps.rest import logger


class GetCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args: Namespace):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        get_parser = parser.add_parser('get', help='Get the namespace')
        get_parser.add_argument('name', nargs='?', default='default', help="The namespace name")
        ListDisplayer.add_output_to_parser(get_parser)
        get_parser.set_defaults(func=GetCommand)
        GetCommand.parser = get_parser

    @command_error
    def run(self):
        # logging.basicConfig(
        #     handlers=[logging.StreamHandler(stream=sys.stdout)],
        #     format='[%(asctime)s] %(message)s',
        #     level=logging.DEBUG
        # )

        # logger = logging.getLogger('generated.apps.rest')

        # logger = logging.getLogger('everai.namespace.namespace')
        logger.setLevel(logging.DEBUG)
        namespace = AppManager().get_namespace(self.args.name)
        ListDisplayer[EveraiNamespace](namespace).show_list(self.args.output)
