from everai.configmap import literals_to_dict, file_to_dict
from everai.secret import Secret
import typing
from everai.api import API


class SecretManager:
    def __init__(self):
        self.api = API()

    def create_from_object(self, secret: Secret) -> Secret:
        v1secret = secret.to_proto()
        resp = self.api.create_secret(v1secret)
        return Secret.from_proto(resp)

    def create(self, name: str, data: typing.Dict[str, str]) -> Secret:
        secret = Secret(name=name, data=data)
        return self.create_from_object(secret)

    def update_from_object(self, secret: Secret) -> Secret:
        v1secret = secret.to_proto()
        resp = self.api.update_secret(v1secret)
        return Secret.from_proto(resp)

    def update(self, name: str, data: typing.Dict[str, str]) -> Secret:
        secret = Secret(name=name, data=data)
        return self.update_from_object(secret)

    def create_from_literal(self, name: str, literals: typing.List[str]) -> Secret:
        data = literals_to_dict(literals=literals)
        return self.create(name, data)

    def update_from_literal(self, name: str, literals: typing.List[str]) -> Secret:
        data = literals_to_dict(literals=literals)
        return self.update(name, data)

    def create_from_file(self, file: str) -> Secret:
        secret = Secret.from_yaml_file(file)
        return self.create_from_object(secret)

    def update_from_file(self, file: str) -> Secret:
        secret = Secret.from_yaml_file(file)
        return self.update_from_object(secret)

    def delete(self, name: str):
        self.api.delete_secret(name)

    def list(self) -> typing.List[Secret]:
        resp = self.api.list_secrets()

        list_secrets: typing.List[Secret] = []
        for v1secret in resp:
            list_secrets.append(Secret.from_proto(v1secret))

        return list_secrets

    def get(self, name: str) -> Secret:
        resp = self.api.get_secret(name)
        return Secret.from_proto(resp)
