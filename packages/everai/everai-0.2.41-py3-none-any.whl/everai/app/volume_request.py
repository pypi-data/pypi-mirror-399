import typing


class VolumeRequest:
    # create_if_not_exists: bool
    name: str

    def __init__(self, name: str):
        self.name = name
        # self.create_if_not_exists = create_if_not_exists or False
