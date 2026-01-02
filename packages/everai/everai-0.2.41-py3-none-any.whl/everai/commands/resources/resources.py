import sys

import yaml

from everai.api import API
from everai.commands.command import ClientCommand, setup_subcommands, command_error
from argparse import _SubParsersAction
from everai.commands.configmap.create import CreateCommand
from everai.commands.configmap.delete import DeleteCommand
from everai.commands.configmap.list import ListCommand
from everai.commands.configmap.get import GetCommand
from everai.commands.configmap.update import UpdateCommand


class ResourcesCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        resources_parser = parser.add_parser('resources',
                                             aliases=['res', 'resource'],
                                             help='Show available resources')
        resources_parser.add_argument('-g', '--gpus', action='store_true', help='show available gpus')
        resources_parser.add_argument('-c', '--cpus', action='store_true', help='show available cpus')
        resources_parser.add_argument('-r', '--regions', action='store_true', help='show available regions')
        resources_parser.add_argument('-a', '--all', action='store_true', help='show all available resources')

        resources_parser.set_defaults(func=ResourcesCommand)
        ResourcesCommand.parser = resources_parser

    @command_error
    def run(self):
        affected_number = 0
        output_dict = dict()
        if self.args.all or self.args.regions:
            regions = API().list_regions()
            output_dict.update(dict(regions=regions))
            affected_number += 1

        if self.args.all or self.args.cpus:
            cpus = API().list_cpus()
            output_dict.update(dict(cpus=cpus))
            affected_number += 1

        if self.args.all or self.args.gpus:
            gpus = API().list_gpus()
            output_dict.update(dict(gpus=gpus))
            affected_number += 1

        if affected_number == 0:
            ResourcesCommand.parser.print_help()
        else:
            yaml.dump(output_dict, sys.stdout, default_flow_style=False)
