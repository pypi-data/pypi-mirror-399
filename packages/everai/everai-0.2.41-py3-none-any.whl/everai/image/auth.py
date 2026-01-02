import typing
from abc import ABC, abstractmethod

from everai.placeholder import PlaceholderValue, Placeholder


class Auth(ABC):
    @abstractmethod
    def authenticate(self):
        raise NotImplementedError


class BasicAuth(Auth):
    username: PlaceholderValue
    password: PlaceholderValue

    def __init__(
            self,
            username: typing.Optional[str | Placeholder],
            password: typing.Optional[str | Placeholder],
    ):
        _username = PlaceholderValue(value=username) \
            if isinstance(username, str) else PlaceholderValue(placeholder=username)

        _password = PlaceholderValue(value=password) \
            if isinstance(password, str) else PlaceholderValue(placeholder=password)

        self.username = _username
        self.password = _password

    def authenticate(self):
        return self.username, self.password
