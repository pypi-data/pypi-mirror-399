import os.path
from os import path, walk, stat
import typing
import hashlib
import requests
from tenacity import retry, wait_fixed, stop_after_attempt
from datetime import datetime
from tqdm.utils import CallbackIOWrapper

from everai.constants import *
from math import ceil
from typing import BinaryIO, Optional, Callable
from everai.logger import logger
from everai.utils.verbose import verbose_print


class _UniqueStr(str):
    _lower = None

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other

    def lower(self):
        if self._lower is None:
            lower = str.lower(self)
            if str.__eq__(lower, self):
                self._lower = self
            else:
                self._lower = _UniqueStr(lower)
        return self._lower


def convert_headers(headers: typing.Dict[str, typing.List[str]]) -> typing.Dict[_UniqueStr, str]:
    result: typing.Dict[_UniqueStr, str] = {}
    for key, values in headers.items():
        for value in values:
            result[_UniqueStr(key)] = value
    return result


class DirUtils:
    def __init__(self, dir_name: str):
        self.dir = dir_name

    def get_all_files_in_dir(self, delete_prefix: str = None, trans_linux_path: bool = False) -> typing.List[str]:
        file_list = []
        for root, dirs, files in walk(self.dir):
            for file in files:
                file_path = path.join(root, file)
                if delete_prefix:
                    file_path = os.path.relpath(file_path, delete_prefix)
                    file_path = file_path.startswith('/') or os.path.join('/', file_path)
                if trans_linux_path:
                    file_path = file_path.replace('\\', '/')
                file_list.append(file_path)
        return file_list


http_retry_wrapper = retry(wait=wait_fixed(6), stop=stop_after_attempt(10), reraise=True)


class FileUtils:
    def __init__(self, file: str):
        self.file = file
        self.sha256 = None

    def get_sha256(self) -> str:
        if self.sha256 is not None:
            return self.sha256

        with open(self.file, 'rb') as f:
            sha256obj = hashlib.sha256()
            sha256obj.update(f.read())
            self.sha256 = sha256obj.hexdigest()
            return self.sha256

    def get_size(self) -> int:
        file_info = stat(self.file)
        return file_info.st_size

    def file_exists(self) -> bool:
        return path.exists(self.file)

    def delete(self):
        if self.file_exists():
            os.remove(self.file)

    def compare_size(self, size: int):
        if self.get_size() > size:
            return True
        return False

    def get_file_create_time(self) -> datetime:
        c_time = os.path.getctime(self.file)
        return datetime.fromtimestamp(c_time)

    def get_file_create_time_str(self) -> str:
        return self.get_file_create_time().strftime(TIME_FORMAT)

    def get_file_modify_time_str(self) -> str:
        return self.get_file_modify_time().strftime(TIME_FORMAT)

    def get_file_modify_time(self) -> datetime:
        m_time = os.path.getmtime(self.file)
        return datetime.fromtimestamp(m_time)

    def split_number(self, split_size: int) -> int:
        return ceil(self.get_size() / split_size)

    def download_file(self, method: str, url: str, headers: typing.Dict[str, typing.List[str]] = None, use_stream: bool = False) -> requests.Response:
        verbose_print(f'method: {method}, url: {url}')

        resp = requests.request(method=method, url=url, headers=convert_headers(headers), stream=use_stream)
        if resp.status_code != 200:
            raise Exception(f'download file({self.file}) failed; status code: {resp.status_code}, '
                            f'resp body: {resp.text}')

        dir_name = os.path.dirname(self.file)
        os.makedirs(dir_name, exist_ok=True)
        with open(self.file, 'w+b') as file:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

        return resp

    def upload_file(self, method: str, url: str, headers: typing.Dict[str, typing.List[str]] = None,
                    stream: bool = False,
                    progress_updator: Optional[Callable[[int], None]] = None) -> requests.Response:
        with open(self.file, 'rb') as file:
            data = file
            if progress_updator is not None:
                data = CallbackIOWrapper(progress_updator, file, "read")

            # http_retry_wrapper = retry(wait=wait_fixed(6), stop=stop_after_attempt(10), reraise=True)
            x_request = http_retry_wrapper(requests.request)

            resp = x_request(method=method, url=url, data=data,
                             headers=convert_headers(headers), stream=stream)

            # resp = requests.request(method=method, url=url, data=data,
            #                         headers=convert_headers(headers), stream=stream)
            if resp.status_code != 200:
                raise Exception(f'upload file({self.file}) failed; status code: {resp.status_code}, '
                                f'resp body: {resp.text}')
        return resp

    def upload_file_part(self, method: str, url: str, headers: typing.Dict[str, typing.List[str]],
                         range_begin: int, range_end: int, stream: bool = False, file: Optional[BinaryIO] = None,
                         progress_updator: Optional[Callable[[int], None]] = None) -> requests.Response:
        def _upload_part(_file: BinaryIO):
            file_size = _file.seek(0, os.SEEK_END)
            assert range_end > range_begin
            assert file_size >= range_end

            _file.seek(range_begin, os.SEEK_SET)
            data = _file.read(range_end - range_begin)

            x_request = http_retry_wrapper(requests.request)

            resp = x_request(method=method, url=url, data=data, headers=convert_headers(headers), stream=stream)

            # resp = requests.request(method=method, url=url, data=data, headers=convert_headers(headers), stream=stream)
            if resp.status_code != 200:
                raise Exception(f'upload file({self.file}) failed; status code: {resp.status_code}, '
                                f'resp body: {resp.text}')
            if progress_updator is not None:
                progress_updator(len(data))
            return resp

        if file is not None:
            return _upload_part(file)

        with open(self.file, 'rb') as file:
            return _upload_part(file)
