from argparse import _SubParsersAction

from everai.commands.command import ClientCommand, command_error
from everai.runner import must_find_target
from everai.image.builder import Builder


class ImageBuildCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction) -> None:
        image_build_parser = parser.add_parser('build', help='Image build')
        image_build_parser.set_defaults(func=ImageBuildCommand)

    @command_error
    def run(self):
        print('Start compiling the image ...')
        builder = must_find_target(search_files=['image.py', 'image_builder.py'], target_type=Builder, target_name='image_builder')
        builder.run()