import typing

from everai.app import App, AppManager
from everai.commands.app.utils import add_app_namespace_to_parser
from everai.commands.command import ClientCommand, command_error, ListDisplayer
from argparse import _SubParsersAction
from everai.commands.app import app_detect, add_app_name_to_parser
from everai.event import Event


class EventsCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    @app_detect(optional=True)
    def setup(parser: _SubParsersAction, app: typing.Optional[App]):
        queue_parser = parser.add_parser('events', aliases=['e', 'event'], help='List events of app')

        add_app_name_to_parser(queue_parser, app, arg_name='name')
        add_app_namespace_to_parser(queue_parser, app)
        ListDisplayer.add_output_to_parser(queue_parser)

        queue_parser.set_defaults(func=EventsCommand)

    @command_error
    def run(self):
        events = AppManager().list_events(app_name=self.args.name, namespace=self.args.namespace)
        ListDisplayer[Event](events).show_list(self.args.output)
