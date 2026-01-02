import typing

from everai.app import App
from everai.commands.app.utils import add_app_namespace_to_parser
from everai.commands.command import ClientCommand, command_error
from argparse import _SubParsersAction
from everai.app.app_manager import AppManager
from everai.commands.app import add_app_name_to_parser, app_detect


class ResumeCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    @app_detect(optional=True)
    def setup(parser: _SubParsersAction, app: typing.Optional[App]):
        resume_parser = parser.add_parser("resume", help="Resume an app")

        add_app_name_to_parser(resume_parser, app, arg_name='name')
        add_app_namespace_to_parser(resume_parser, app)

        resume_parser.set_defaults(func=ResumeCommand)

    @command_error
    def run(self):
        AppManager().resume(self.args.name, self.args.namespace)
