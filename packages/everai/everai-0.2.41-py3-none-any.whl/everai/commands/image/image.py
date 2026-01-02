from everai.commands.command import ClientCommand, setup_subcommands
from argparse import _SubParsersAction

from everai.commands.image.build import ImageBuildCommand
from everai.constants import COMMAND_ENTRY


class ImageCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction) -> None:
        image_parser = parser.add_parser('image', aliases=['images', 'i'],
                                         help='Image management')
        image_subparsers = image_parser.add_subparsers(help=f'{COMMAND_ENTRY} image command helps')

        setup_subcommands(image_subparsers, [
            ImageBuildCommand,
        ])

        image_parser.set_defaults(func=ImageCommand)
        ImageCommand.parser = image_parser

    def run(self):
        ImageCommand.parser.print_help()
