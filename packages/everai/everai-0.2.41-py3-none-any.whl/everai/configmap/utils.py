import typing
import yaml


def literals_to_dict(literals: typing.List[str]) -> typing.Dict[str, str]:
    data: typing.Dict[str, str] = {}
    for literal in literals:
        key_value = literal.split('=', 1)

        if len(key_value) == 2:
            data[key_value[0]] = key_value[1]
        else:
            data[key_value[0]] = ''
    return data


def stream_to_dict(stream: typing.IO[typing.Any]) -> typing.Dict[str, str]:
    loaded = yaml.safe_load(stream)
    assert isinstance(loaded, dict)
    assert all(isinstance(key, str) and isinstance(value, str) for key, value in loaded.items())
    return loaded


def file_to_dict(file: str) -> typing.Dict[str, str]:
    with open(file, "r") as f:
        return stream_to_dict(f)


def load_yaml_file(file: str) -> typing.Dict[str, str]:
    with open(file, "r") as f:
        return yaml.safe_load(f)
        # return stream_to_dict(f)
