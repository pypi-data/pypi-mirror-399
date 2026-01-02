from argparse import ArgumentParser

import argcomplete

from everai.commands.app import AppCommand
from everai.commands.command import setup_subcommands
from everai.commands.config import ConfigCommand
from everai.commands.auth import LoginCommand
from everai.commands.auth import LogoutCommand
from everai.commands.configmap import ConfigMapCommand
from everai.commands.run import RunCommand
from everai.commands.image import ImageCommand
from everai.commands.secret import SecretCommand
from everai.commands.version import VersionCommand
from everai.commands.volume import VolumeCommand
from everai.commands.autoscaler import AutoscalerCommand
from everai.commands.worker import WorkerCommand
from everai.commands.resources import ResourcesCommand
from everai.commands.namespace import NamespaceCommand
from everai.constants import COMMAND_ENTRY

import everai.utils.verbose as vb


def main():
    parser = ArgumentParser(
        COMMAND_ENTRY,
        description='EverAI Client for manage your EverAI application and other asserts'
    )

    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Verbose output',
    )
    commands_parser = parser.add_subparsers(help=f'Valid subcommands for {COMMAND_ENTRY}')

    setup_subcommands(commands_parser, [
        LoginCommand,
        LogoutCommand,
        WorkerCommand,
        ConfigCommand,
        ImageCommand,
        RunCommand,
        AppCommand,
        SecretCommand,
        VolumeCommand,
        AutoscalerCommand,
        ConfigMapCommand,
        ResourcesCommand,
        NamespaceCommand,
        VersionCommand,
    ])

    argcomplete.autocomplete(parser)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        exit(1)
    vb.is_verbose = args.verbose
    service = args.func(args)
    service.run()


if __name__ == "__main__":
    main()
