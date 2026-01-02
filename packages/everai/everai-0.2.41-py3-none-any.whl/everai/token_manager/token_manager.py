from pathlib import Path
from everai import constants
from typing import Optional
from everai.constants import *


class TokenManager:
    @staticmethod
    def set_token(token: str):
        path = Path(constants.EVERAI_TOKEN_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(token)

    @staticmethod
    def delete_token() -> None:
        if TokenManager.get_token() is None:
            print('No login')
            return

        # Delete file
        try:
            Path(constants.EVERAI_TOKEN_PATH).unlink()
        except FileNotFoundError:
            pass

        if TokenManager.__get_token_from_environment() is not None:
            raise EnvironmentError(
                f"Please delete environment `{EVERAI_TOKEN}`"
            )
        return

    @staticmethod
    def get_token() -> Optional[str]:
        return TokenManager.__get_token_from_environment() or TokenManager.__get_token_from_file()

    @staticmethod
    def __get_token_from_file() -> Optional[str]:
        try:
            return TokenManager.__clean_token_blank(Path(constants.EVERAI_TOKEN_PATH).read_text())
        except FileNotFoundError:
            return None

    @staticmethod
    def __get_token_from_environment() -> Optional[str]:
        return TokenManager.__clean_token_blank(os.environ.get(EVERAI_TOKEN))

    @staticmethod
    def __clean_token_blank(token) -> Optional[str]:
        if token is None:
            return None

        return token.replace('\r', '').replace('\n', '').strip() or None
