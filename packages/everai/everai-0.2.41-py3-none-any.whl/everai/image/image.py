from __future__ import annotations
from .auth import Auth
import typing


class Image:
    image: str
    auth: Auth
    repository: str
    tag: typing.Optional[str]
    digest: typing.Optional[str]

    @staticmethod
    def parse_image_name(image: str) -> tuple[str, typing.Optional[str], typing.Optional[str]]:
        digest = None
        tag = None

        digest_parts = image.rsplit('@', 1)
        if len(digest_parts) == 2:
            digest = digest_parts[1]

        tag_parts = digest_parts[0].rsplit(':', 1)
        if len(tag_parts) != 2:
            tag = None if digest is not None else 'latest'
        else:
            tag = tag_parts[1]

        return tag_parts[0], tag, digest

    def __init__(self, image: str, auth: typing.Optional[Auth] = None):
        self.image = image
        self.auth = auth

        self.repository, self.tag, self.digest = Image.parse_image_name(image)

    @staticmethod
    def from_registry(image: str, auth: typing.Optional[Auth] = None) -> Image:
        return Image(image, auth=auth)
