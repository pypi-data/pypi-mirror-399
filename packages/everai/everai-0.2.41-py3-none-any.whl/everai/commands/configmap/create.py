from everai.commands.command import ClientCommand, command_error
from argparse import _SubParsersAction

from everai.configmap import ConfigMapManager
from everai.secret.secret_manager import SecretManager


class CreateCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        create_parser = parser.add_parser('create', help='Create ConfigMap from file or literal string')

        file_group = create_parser.add_argument_group('create from file')
        file_group.add_argument(
            '-f',
            '--from-file',
            type=str,
            help='Create configmap from file, for example: --from-file filename'
        )

        literal_group = create_parser.add_argument_group('create from literal')
        literal_group.add_argument(
            '-l',
            '--from-literal',
            action='append',
            type=str,
            help='Create configmap from literal, for example: --from-literal name=user'
        )

        literal_group.add_argument(
            'name',
            type=str,
            nargs='?',
            help='The configmap name'
        )

        create_parser.set_defaults(func=CreateCommand)

        CreateCommand.parser = create_parser

    @command_error
    def run(self):
        if self.args.from_literal is None and self.args.from_file is None:
            CreateCommand.parser.error('please specify either --from-literal, or --from-file arguments')

        if self.args.from_literal is not None and self.args.from_file is not None:
            CreateCommand.parser.error('cannot support both --from-literal and --from-file')

        if self.args.from_literal is not None and len(self.args.from_literal) > 0:
            if self.args.name is None:
                CreateCommand.parser.error('the following arguments are required: name')

            configmap = ConfigMapManager().create_from_literal(name=self.args.name, literals=self.args.from_literal)
        elif self.args.from_file is not None and len(self.args.from_file) > 0:
            configmap = ConfigMapManager().create_from_file(file=self.args.from_file)
        else:
            raise RuntimeError('Never been here')

        print(f"Configmap `{configmap.name}` created successfully")
