import argparse
import json
import sys
import typing
from datetime import datetime

import yaml
from tabulate import tabulate


class HasRequiredMethod(typing.Protocol):
    @classmethod
    def table_title(cls, wide: bool = False) -> typing.List[str]:
        ...

    def table_row(self, wide: bool = False) -> typing.List:
        ...

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        ...


T = typing.TypeVar("T", bound=HasRequiredMethod)


class NoAliasDumper(yaml.SafeDumper):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def ignore_aliases(self, data):
        return True


def yaml_output(items: typing.Union[T, typing.List[T]]):
    if isinstance(items, typing.List) and len(items) == 0:
        return
    sample = items[0] if isinstance(items, typing.List) else items
    dumper = getattr(sample, 'yaml_dumper', None) or NoAliasDumper

    if isinstance(items, typing.List):
        yaml.dump([item.to_dict() for item in items],
                  sys.stdout, default_flow_style=False, Dumper=dumper)
    else:
        yaml.dump(items.to_dict(),
                  sys.stdout, default_flow_style=False, sort_keys=False, Dumper=dumper)


def json_output(items: typing.Union[T, typing.List[T]]):
    def datatime_default(o: typing.Any):
        if isinstance(o, datetime):
            return o.isoformat()

    if isinstance(items, typing.List):
        data = json.dumps([item.to_dict() for item in items],
                          default=datatime_default,
                          indent=2,
                          )
    else:
        data = json.dumps(items.to_dict(),
                          default=datatime_default,
                          indent=2,
                          )
    print(data)


class ListDisplayer(typing.Generic[T]):
    items: typing.Union[T, typing.List[T]]

    def __init__(self, items: typing.Union[T, typing.List[T]]):
        if isinstance(items, typing.List):
            self.items = items
        else:
            self.items = items

    def table_title(self, wide: bool = False):
        assert hasattr(self, '__orig_class__')
        cls = getattr(self, '__orig_class__').__args__[0]
        return cls.table_title(wide=wide)

    def show_list(self, output: str = 'table'):
        match output:
            case 'wide':
                titles = self.table_title(wide=True)
                wide = True
            case 'yaml':
                return yaml_output(self.items)
            case 'json':
                return json_output(self.items)
            case _:
                titles = self.table_title()
                wide = False

        l = self.items if isinstance(self.items, typing.List) else [self.items]
        print(
            tabulate(
                [item.table_row(wide=wide) for item in l],
                headers=titles,
                tablefmt="simple",
            ),
        )

    @staticmethod
    def add_output_to_parser(parser: argparse.ArgumentParser):
        parser.add_argument("--output", "-o",
                            help="Output format, One of: (json, yaml, table, wide)",
                            nargs="?", default="table")
