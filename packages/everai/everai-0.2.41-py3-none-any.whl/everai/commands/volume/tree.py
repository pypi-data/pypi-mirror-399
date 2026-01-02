from everai.commands.command import ClientCommand, command_error, ListDisplayer
from argparse import _SubParsersAction
from bigtree import list_to_tree, print_tree
from typing import List

from generated.volumes import V1File
from everai.volume.volume_manager import VolumeManager


class VolumeTreeCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        list_parser = parser.add_parser('tree', aliases=['tr'], help='Tree volume')
        list_parser.add_argument('name', help='Volume name')

        list_parser.set_defaults(func=VolumeTreeCommand)

    @command_error
    def run(self):
        files = VolumeManager().list_files(self.args.name)
        paths: List[str] = []
        for file in files:
            paths.append(f'/{self.args.name}{file.path}')
        root = list_to_tree(paths, sep='/')
        print_tree(root)
