import typing


def remove_empty_key(input_data: typing.Dict[typing.Any, typing.Any]) -> typing.Dict[typing.Any, typing.Any]:
    empty_keys = []
    for key in input_data.keys():
        if input_data[key] is None:
            empty_keys.append(key)

    output = input_data.copy()
    for key in empty_keys:
        output.pop(key)
    return output
