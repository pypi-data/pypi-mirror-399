from everai.commands.command import ClientCommand, command_error
from argparse import _SubParsersAction
from everai.volume.volume_manager import VolumeManager


class VolumePublishCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        delete_parser = parser.add_parser('publish', help='Publish volume to everyone')
        delete_parser.add_argument('name', help='The volume name')

        delete_parser.set_defaults(func=VolumePublishCommand)

    @command_error
    def run(self):
        volume_manager = VolumeManager()
        volume_manager.publish_volume(self.args.name)
