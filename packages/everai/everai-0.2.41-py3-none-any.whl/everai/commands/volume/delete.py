from everai.commands.command import ClientCommand, command_error
from argparse import _SubParsersAction
from everai.volume.volume_manager import VolumeManager
from everai.constants import EVERAI_VOLUME_ROOT


class VolumeDeleteCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        delete_parser = parser.add_parser('delete', help='Delete volume')
        delete_parser.add_argument('name', help='The volume name')
        delete_parser.add_argument('--local', action='store_true', help='Delete the local cache of volume only')
        delete_parser.add_argument('--cloud', action='store_true',
                                   help='Delete the volume in cloud, and reserve local cache')
        delete_parser.add_argument('--all', action='store_true', help='Delete volume both cache and in-cloud')

        delete_parser.set_defaults(func=VolumeDeleteCommand)

    @command_error
    def run(self):
        manager = VolumeManager(EVERAI_VOLUME_ROOT)
        if self.args.local and self.args.cloud:
            print('You cannot use both --local and --cloud, please use --all instead')
            exit(-1)

        local = False
        cloud = False
        if self.args.all:
            local = True
            cloud = True
        elif self.args.local:
            local = True
        elif self.args.cloud:
            cloud = True
        else:
            print('You must specify one of --local, --cloud or --all')

        manager.delete_volume(self.args.name, local=local, cloud=cloud)
        print('Volume deleted successfully')
