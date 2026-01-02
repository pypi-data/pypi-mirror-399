import datetime
import glob
import shutil

import jsonpickle

from everai.utils.size import human_size, human_size_tuple
from everai.volume import Volume
from everai.api import API
from typing import Callable, Dict, List, Optional, Tuple
from everai.utils.file import FileUtils, DirUtils
from everai.constants import *
from everai.utils.list import ListUtils
from everai.volume.name_helper import myself_volume_name, regular_volume_name
from generated.volumes import V1File, V1Part
from tqdm import tqdm

UpdateFileFunction = Callable[[str, str, Dict, bool], None]
GetUpdateFileUrlFunction = Callable[[str, str], tuple[str, str, Dict]]

INITIAL_REVISION = '000000-000'


class VolumeFileDescribe:
    _path: str
    _size: int
    _sha256: str
    _modified_at: datetime.datetime

    def __init__(self, path: str, size: int, sha256: str, modified_at: datetime.datetime):
        self._path = path
        self._size = size
        self._sha256 = sha256
        self._modified_at = modified_at

    def path(self) -> str:
        return self._path

    def size(self) -> int:
        return self._size

    def sha256(self) -> str:
        return self._sha256

    def modified_at(self) -> datetime.datetime:
        return self._modified_at


class VolumeManager:
    def __init__(self, volume_root: str = None):
        volume_root = volume_root or EVERAI_VOLUME_ROOT
        self.api = API()
        self.volume_root = volume_root
        os.makedirs(self.volume_root, exist_ok=True)

    class CompareResult:
        local_only_files: List[str]
        cloud_only_files: List[V1File]
        consistent_files: List[V1File]
        # tuple.0 is local data, tuple.1 is cloud data
        inconsistent_files: List[Tuple[V1File, V1File]]

        def __init__(self, local_only_files: Optional[List[str]] = None,
                     cloud_only_files: Optional[List[V1File]] = None,
                     consistent_files: Optional[List[V1File]] = None,
                     inconsistent_files: Optional[List[tuple[V1File, V1File]]] = None):
            self.local_only_files = local_only_files or []
            self.cloud_only_files = cloud_only_files or []
            self.consistent_files = consistent_files or []
            self.inconsistent_files = inconsistent_files or []

    @regular_volume_name
    def compare_files(self, volume_name: str, volume_path: str, update=False) -> CompareResult:
        """
        return a tuple of:
        the first element is the files only in cloud
        the second element is the files only in local
        the third element is both in cloud and local, and both size and sha256 equal each other
        the fourth element is both in cloud and local, and size or sha256 not match tuple[Local, Cloud]
        """
        result = VolumeManager.CompareResult()

        # list remote files
        list_cloud_files = self.api.list_volume_files(name=volume_name)
        # list local files
        list_local_files = DirUtils(volume_path).get_all_files_in_dir(delete_prefix=volume_path,
                                                                      trans_linux_path=True)

        list_local_files = [x for x in list_local_files if x != '/.metadata']

        cloud_files_name = [x.path for x in list_cloud_files]

        in_src, in_both, in_dst = ListUtils.diff(list_local_files, cloud_files_name)
        result.local_only_files = in_src
        result.cloud_only_files = [x for x in list_cloud_files if x.path in in_dst]

        for file_name in in_both:
            # remove first / and joint to volume_path
            full_file_name = self.join(volume_path, file_name)
            file_utils = FileUtils(full_file_name)
            cloud_file = next((x for x in list_cloud_files if x.path == file_name), None)
            assert cloud_file is not None
            size = file_utils.get_size()
            # sha256 = file_utils.get_sha256()

            if update:
                if str(size) != cloud_file.size:
                    sha256 = file_utils.get_sha256()
                    result.inconsistent_files.append((V1File(
                        path=file_name,
                        size=str(size),
                        sha256=sha256,
                    ), cloud_file))
                else:
                    result.consistent_files.append(cloud_file)
            else:
                sha256 = file_utils.get_sha256()
                if str(size) != cloud_file.size or sha256 != cloud_file.sha256:
                    # if size not equal to remote, pull it
                    result.inconsistent_files.append((V1File(
                        path=file_name,
                        size=str(size),
                        sha256=sha256,
                    ), cloud_file))
                else:
                    result.consistent_files.append(cloud_file)

            # if str(size) != cloud_file.size or sha256 != cloud_file.sha256:
            #     # if size not equal to remote, pull it
            #     result.inconsistent_files.append((V1File(
            #         path=file_name,
            #         size=str(size),
            #         sha256=sha256,
            #     ), cloud_file))
            # else:
            #     result.consistent_files.append(cloud_file)
        return result

    @regular_volume_name
    def pull(self, name: str, is_force: bool = False, is_sync: bool = False) -> Volume:
        """
        is_force: false means if the revision in local cache, the pull will be ignored,
            otherwise always download files

        is_sync: true means local files which is not in cloud will be deleted,
            otherwise only download missed files
        """
        volume = self.get(name)
        local_volume = Volume.from_path(self.volume_path(volume.id))

        volume_path = self.volume_path(volume.id)
        volume.set_path(volume_path)
        os.makedirs(volume_path, exist_ok=True)
        volume.write_metadata()

        should_download = (is_force or local_volume is None or
                           (volume.revision != INITIAL_REVISION and local_volume.revision != volume.revision))

        if not should_download and not is_sync:
            return volume

        compare_result = self.compare_files(name, volume_path)

        # pickup file metadata in cloud
        inconsistent_files = [x[1] for x in compare_result.inconsistent_files]

        for should_pull_file in compare_result.cloud_only_files + inconsistent_files:
            download_method, download_url, download_headers = self.api.sign_download(
                name, should_pull_file.path)

            FileUtils(self.join(volume_path, should_pull_file.path)).download_file(
                download_method, download_url, download_headers, True)

        # if is_sync be set, remote local extra files
        if is_sync:
            for delete_file in compare_result.local_only_files:
                FileUtils(self.join(volume_path, delete_file)).delete()
        return volume

    @myself_volume_name
    def upload_single_file(self, volume_name: str, revision_name: str, file: V1File,
                           file_utils: FileUtils,
                           progress_updator: Optional[Callable[[int], None]] = None
                           ) -> tuple[bool, V1File]:
        should_upload, method, url, headers = self.api.sign_upload(volume_name, revision_name, file.path, file.size,
                                                                   file.sha256)
        if should_upload:
            file_utils.upload_file(method, url, headers, progress_updator=progress_updator)
        else:
            progress_updator(int(file.size))
        return should_upload, file

    @myself_volume_name
    def upload_multipart_file(self, volume_name: str, revision_name: str, file: V1File,
                              file_utils: FileUtils,
                              progress_updator: Optional[Callable[[int], None]] = None
                              ) -> tuple[bool, V1File]:
        should_upload, upload_id = self.api.init_multipart_upload(volume_name, revision_name, file.path, int(file.size),
                                                                  file.sha256)
        if not should_upload:
            progress_updator(int(file.size))
            return should_upload, file

        parts = self.api.list_multipart_upload_parts(volume_name, revision_name, upload_id)
        range_begin = 0
        next_part_number = 1
        for part in parts:
            range_begin += int(part.size)
            if progress_updator is not None:
                progress_updator(int(part.size))

            if part.part_number + 1 > next_part_number:
                next_part_number = part.part_number + 1

        while range_begin < int(file.size):
            method, url, headers = self.api.sign_multipart_upload(volume_name, revision_name, upload_id,
                                                                  next_part_number)
            range_end = range_begin + int(DEFAULT_PART_SIZE)
            if range_end > int(file.size):
                range_end = int(file.size)

            resp = file_utils.upload_file_part(method, url, headers, range_begin, range_end, progress_updator=progress_updator)
            # get etag
            # resp.headers
            etag = resp.headers.get('ETag')
            assert etag is not None

            parts.append(V1Part(part_number=next_part_number, etag=etag, size=str(range_end - range_begin)))

            next_part_number += 1
            range_begin = range_end

        self.api.complete_multipart_upload(volume_name, revision_name, upload_id, parts)
        return True, file

    # noinspection PyMethodMayBeStatic
    def join(self, *args: str) -> str:
        assert len(args) > 0

        parts = [x.removeprefix('/').removesuffix('/') for x in args[1:]]
        return str(os.path.join(args[0], *parts))

    def file_path(self, volume_id: str, file_path: str) -> str:
        return self.join(self.volume_path(volume_id), file_path)

    @myself_volume_name
    def upload_file(self, volume_name: str, revision_name: str, volume_path: str,
                    file: str or V1File) -> V1File:
        upload_file_metadata: V1File
        file_utils: FileUtils
        if isinstance(file, str):
            file_path = self.join(volume_path, file)
            file_utils = FileUtils(file_path)
            size = file_utils.get_size()
            sha256 = file_utils.get_sha256()
            upload_file_metadata = V1File(path=file, size=str(size), sha256=sha256)
        else:
            upload_file_metadata = file
            file_path = self.join(volume_path, file.path)
            file_utils = FileUtils(file_path)

        human_readable_size, unit = human_size_tuple(int(upload_file_metadata.size), )
        filename = upload_file_metadata.path
        if len(filename) > 48:
            filename = f'...{filename[len(filename) - 64 + 3:]}'
        else:
            filename = filename.rjust(48)

        with tqdm(unit=unit, desc=f'Uploading {filename}', total=human_readable_size) as t:
            def updator(n: int) -> None:
                updator_readable_size, _ = human_size_tuple(int(n), )
                t.update(updator_readable_size)

            if int(upload_file_metadata.size) > MAX_SINGLE_FILE_SIZE:
                should_commit, result = self.upload_multipart_file(
                    volume_name, revision_name, upload_file_metadata, file_utils,
                    progress_updator=updator,
                )
            else:
                should_commit, result = self.upload_single_file(
                    volume_name, revision_name, upload_file_metadata, file_utils,
                    progress_updator=updator)

        if should_commit:
            self.api.commit_file(volume_name, revision_name, result)
        return result

    @myself_volume_name
    def push(self, name: str, update=False) -> Volume:
        volume = self.get(name)
        volume_path = self.volume_path(volume.id)
        volume.set_path(volume_path)

        compare_result = self.compare_files(name, volume_path, update)
        """
        compare_result.cloud_only_files should be delete from this revision
        compare_result.local_only_files should be upload and commit to revision
        compare_result.consistent_files should be commit to revision
        compare_result.inconsistent_files should be upload and commit to revision
        """
        if (len(compare_result.cloud_only_files) == 0 and
                len(compare_result.local_only_files) == 0 and
                len(compare_result.inconsistent_files) == 0):
            # nothing to do
            return volume

        # create new revision
        revision = self.api.create_revision(name)

        commit_files: List[V1File] = compare_result.consistent_files

        # upload files, missed file
        upload_files: List[V1File] = compare_result.local_only_files
        # append inconsistent files
        for local, cloud in compare_result.inconsistent_files:
            upload_files.append(local)

        # upload missed file
        with tqdm(unit='file', desc=f'Uploading {"files".rjust(48)}', total=len(upload_files)) as t:
            t.reset(len(upload_files))
            for file in upload_files:
                f = self.upload_file(name, revision.name, volume_path, file)
                commit_files.append(f)
                t.update(1)

        # commit revision
        self.api.commit_revision(name, revision.name, commit_files)

        # change local path to correct revision
        volume.revision = revision.name
        volume.write_metadata()

        return volume

    # use volume id to avoid volume name conflict if more than one user use this machine
    def volume_path(self, volume_id: str) -> str:
        return os.path.join(self.volume_root, volume_id)

    @myself_volume_name
    def create_volume(self, name: str) -> Volume:
        v1_volume = self.api.create_volume(name)

        volume = Volume.from_proto(v1_volume)
        assert volume.revision is not None
        volume_path = self.volume_path(volume.id)
        volume.set_path(volume_path)
        os.makedirs(volume_path, exist_ok=True)
        volume.write_metadata()

        return volume

    @regular_volume_name
    def from_name(self, name: str) -> Optional[Volume]:
        metadata_files = glob.glob(f'{self.volume_root}/*/.metadata', recursive=True)
        return_value = None

        for metadata_file in metadata_files:
            with open(metadata_file, 'r') as f:
                data = f.read()
                v = jsonpickle.loads(data, classes=Volume)
                if v.name == name and (return_value is None or return_value.revision < v.revision):
                    return_value = v
        return return_value

    @myself_volume_name
    def delete_cloud_volume(self, volume_name: str):
        self.api.delete_volume(volume_name)

    @regular_volume_name
    def delete_local_volume(self, volume_name: str):
        volume = self.from_name(volume_name)
        if volume is None:
            raise ValueError('Volume not found in local')
        volume_path = self.volume_path(volume.id)
        shutil.rmtree(volume_path, ignore_errors=True)

    @myself_volume_name
    def delete_volume(self, volume_name: str, local: bool = False, cloud: bool = False) -> None:
        if not local and not cloud:
            raise ValueError('need one of local and cloud or both them to delete volume')

        if local:
            self.delete_local_volume(volume_name)

        if cloud:
            self.delete_cloud_volume(volume_name)
        return

    @regular_volume_name
    def get(self, volume_name: str) -> Volume:
        volume = self.api.get_volume(volume_name)
        return Volume.from_proto(volume)

    @regular_volume_name
    def list_files(self, volume_name: str) -> List[V1File]:
        return self.api.list_volume_files(volume_name)

    def list_local_volumes(self) -> List[Volume]:
        metadata_files = glob.glob(f'{self.volume_root}/*/.metadata', recursive=True)
        volumes: Dict[str, Volume] = {}

        for metadata_file in metadata_files:
            with open(metadata_file, 'r') as f:
                data = f.read()
                v: Volume = jsonpickle.loads(data, classes=Volume)

                if v.id in volumes:
                    # update to latest revision
                    if v.revision > volumes[v.id].revision:
                        volumes[v.id] = v

                else:
                    volumes[v.id] = v
        return list(volumes.values())

    def list_cloud_volumes(self) -> List[Volume]:
        resp = self.api.list_volumes()
        volumes: List[Volume] = []
        for volume_info in resp:
            volumes.append(Volume.from_proto(volume_info))

        return volumes

    def list_volumes(self, local: bool = False) -> List[Volume]:
        """
        list volumes
        argument local means list local cache of volumes
        the opposite means list all the volumes in cloud
        """
        return self.list_local_volumes() if local else self.list_cloud_volumes()

    @myself_volume_name
    def publish_volume(self, name: str):
        self.api.publish_volume(name)
