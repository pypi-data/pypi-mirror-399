from everai.commands.command import ClientCommand, command_error
from argparse import _SubParsersAction
from everai.volume.volume_manager import VolumeManager
from everai.constants import EVERAI_VOLUME_ROOT


class VolumeCreateCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        create_parser = parser.add_parser('create', help='Create volume')
        create_parser.add_argument('name', help='The volume name', type=str)

        create_parser.set_defaults(func=VolumeCreateCommand)

    @command_error
    def run(self):
        manager = VolumeManager(EVERAI_VOLUME_ROOT)
        volume = manager.create_volume(self.args.name)
        print("create volume successful")
        print(volume)
