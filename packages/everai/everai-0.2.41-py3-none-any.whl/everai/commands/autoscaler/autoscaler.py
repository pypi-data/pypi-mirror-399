from everai import constants
from everai.commands.command import ClientCommand, command_error
from argparse import _SubParsersAction, Namespace

from everai.app import AppManager, App
from everai.commands.app import app_detect


class AutoscalerCommand(ClientCommand):
    def __init__(self, args: Namespace):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction) -> None:
        run_parser = parser.add_parser('autoscaler', help='Run the autoscaler service')
        run_parser.add_argument('--port', type=int, default=constants.EVERAI_PORT, help='The port to bind to')
        run_parser.add_argument('--listen', type=str, default='0.0.0.0', help='The interface to bind to')

        run_parser.set_defaults(func=AutoscalerCommand)

    @command_error
    @app_detect(optional=False)
    def run(self, app: App):
        AppManager().run_autoscaling(app=app,
                                     port=self.args.port,
                                     listen=self.args.listen, )
