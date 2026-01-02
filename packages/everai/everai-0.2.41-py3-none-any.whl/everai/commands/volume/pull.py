from everai.commands.command import ClientCommand, command_error
from argparse import _SubParsersAction
from everai.volume.volume_manager import VolumeManager
from everai.constants import EVERAI_VOLUME_ROOT


class VolumePullCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        pull_parser = parser.add_parser('pull', help='Pull volume')
        pull_parser.add_argument('name', help='The volume name', type=str)
        pull_parser.add_argument(
            '--force',
            default=False,
            action='store_true',
            help='Force pull remote volume file to local, if your volume local metadata revision equal '
                 'remote volume revision, '
                 'pull will stop, if add `--force`, pull will ignore revision compare')

        pull_parser.add_argument(
            '--sync',
            default=False,
            action='store_true',
            help='Sync file form remote, if this file local have, '
                 'but remote not exist, then this local file will be delete. '
                 'notice: only use argument `--force`, --sync will come into effect'
        )
        pull_parser.set_defaults(func=VolumePullCommand)

    @command_error
    def run(self):
        manager = VolumeManager(EVERAI_VOLUME_ROOT)
        volume = manager.pull(self.args.name, self.args.force, self.args.sync)
        print(volume)
