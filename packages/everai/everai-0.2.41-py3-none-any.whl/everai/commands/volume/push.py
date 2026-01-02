from everai.commands.command import ClientCommand, command_error
from argparse import _SubParsersAction
from everai.volume.volume_manager import VolumeManager
from everai.constants import EVERAI_VOLUME_ROOT


class VolumePushCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        create_parser = parser.add_parser('push', help='Push volume')
        create_parser.add_argument('name', help='The volume name', type=str)
        create_parser.add_argument(
            '-u',
            '--update',
            default=False,
            action='store_true',
            help='specifies that volumes push files only when the destination objects do not exist '
                 'or when the size of the files is different from that of the destination objects'
        )

        create_parser.set_defaults(func=VolumePushCommand)

    @command_error
    def run(self):
        manager = VolumeManager(EVERAI_VOLUME_ROOT)
        volume = manager.push(self.args.name, self.args.update)
        print(volume)
