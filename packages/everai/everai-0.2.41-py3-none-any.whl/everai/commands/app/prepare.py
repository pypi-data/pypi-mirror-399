from everai.commands.command import ClientCommand, command_error
from argparse import _SubParsersAction, ArgumentParser

from everai.commands.app import app_detect
from everai.app import App, AppManager


class PrepareCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        pause_parser = parser.add_parser("prepare", help="Prepare an app, all of function "
                                                         "which decorated by @app.prepare would be called")

        pause_parser.set_defaults(func=PrepareCommand)

    @command_error
    @app_detect(optional=False)
    def run(self, app: App):
        AppManager().prepare(app)
