from everai.commands.command import ClientCommand, setup_subcommands
from argparse import _SubParsersAction
from everai.commands.volume.create import VolumeCreateCommand
from everai.commands.volume.delete import VolumeDeleteCommand
from everai.commands.volume.list import VolumeListCommand
from everai.commands.volume.get import VolumeGetCommand
from everai.commands.volume.publish import VolumePublishCommand
from everai.commands.volume.pull import VolumePullCommand
from everai.commands.volume.push import VolumePushCommand
from everai.commands.volume.tree import VolumeTreeCommand


class VolumeCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction) -> None:
        volume_parser = parser.add_parser('volume',
                                          aliases=['volumes', 'vol'],
                                          help='Manage volume')
        volume_subparser = volume_parser.add_subparsers(help='Volume command help')

        setup_subcommands(volume_subparser, [
            VolumeCreateCommand,
            VolumeListCommand,
            VolumeDeleteCommand,
            VolumeGetCommand,
            VolumePullCommand,
            VolumePushCommand,
            VolumePublishCommand,
            VolumeTreeCommand,
        ])

        volume_parser.set_defaults(func=VolumeCommand)
        VolumeCommand.parser = volume_parser

    def run(self):
        VolumeCommand.parser.print_help()
        return
