from everai.commands.command import ClientCommand, command_error, ListDisplayer
from argparse import _SubParsersAction

from everai.volume import Volume
from everai.volume.volume_manager import VolumeManager


class VolumeListCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        list_parser = parser.add_parser('list', aliases=['ls'], help='List volume')
        ListDisplayer.add_output_to_parser(list_parser)

        list_parser.set_defaults(func=VolumeListCommand)

    @command_error
    def run(self):
        volumes = VolumeManager().list_volumes()
        ListDisplayer[Volume](volumes).show_list(self.args.output)



