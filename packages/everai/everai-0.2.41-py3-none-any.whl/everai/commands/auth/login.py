import os

from everai.commands.command import ClientCommand, command_error
from argparse import _SubParsersAction
from everai.token_manager import TokenManager
from everai.api import API


class LoginCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        login_parser = parser.add_parser('login',
                                         help='Login, if you do not have a token, please visit https://everai.expvent.com ')
        login_parser.add_argument(
            '--token',
            type=str,
            help='Get token from everai',
            required=True,
        )

        login_parser.set_defaults(func=LoginCommand)

    @command_error
    def run(self):
        API().login(self.args.token)

        TokenManager.set_token(self.args.token)
        print('Login successful!')
