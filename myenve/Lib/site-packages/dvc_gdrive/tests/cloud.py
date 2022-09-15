import json
import os
import uuid
from functools import partialmethod
from urllib.parse import urlparse

import pytest
from dvc.testing.cloud import Cloud
from dvc.testing.path_info import CloudURLInfo
from funcy import cached_property, retry

from dvc_gdrive import GDriveFileSystem


class GDriveURLInfo(CloudURLInfo):
    def __init__(self, url):
        super().__init__(url)

        # GDrive URL host part is case sensitive,
        # we are restoring it here.
        p = urlparse(url)
        self.host = p.netloc
        assert self.netloc == self.host

        # Normalize path. Important since we have a cache (path to ID)
        # and don't want to deal with different variations of path in it.
        import re

        self._spath = re.sub("/{2,}", "/", self._spath.rstrip("/"))


def _gdrive_retry(func):
    def should_retry(exc):
        from googleapiclient.errors import HttpError

        if not isinstance(exc, HttpError):
            return False

        if 500 <= exc.resp.status < 600:
            return True

        if exc.resp.status == 403:
            try:
                reason = json.loads(exc.content)["error"]["errors"][0][
                    "reason"
                ]
            except (ValueError, LookupError):
                return False

            return reason in ["userRateLimitExceeded", "rateLimitExceeded"]

    # 16 tries, start at 0.5s, multiply by golden ratio, cap at 20s
    return retry(
        16,
        timeout=lambda a: min(0.5 * 1.618**a, 20),
        filter_errors=should_retry,
    )(func)


class GDrive(Cloud, GDriveURLInfo):
    @cached_property
    def _creds(self):
        return os.environ[GDriveFileSystem.GDRIVE_CREDENTIALS_DATA]

    @property
    def config(self):
        credentials = json.loads(self._creds)
        use_service_account = credentials.get("type") == "service_account"

        return {
            "url": self.url,
            "gdrive_use_service_account": use_service_account,
        }

    @staticmethod
    def _get_storagepath():
        return f"root/dvc-test/{str(uuid.uuid4())}"

    @staticmethod
    def get_url():
        # NOTE: `get_url` should always return new random url
        return "gdrive://" + GDrive._get_storagepath()

    @cached_property
    def client(self):
        try:
            from gdrivefs import GoogleDriveFileSystem
        except ImportError:
            pytest.skip("gdrivefs is not installed")

        return GoogleDriveFileSystem(
            token="cache",
            token_json=self._creds,
            service_account=self.config["gdrive_use_service_account"],
        )

    def is_file(self):
        raise NotImplementedError

    def is_dir(self):
        raise NotImplementedError

    def exists(self):
        raise NotImplementedError

    @_gdrive_retry
    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        try:
            self.client.info(self.path)
        except FileNotFoundError:
            self.client.mkdir(self.path, parents=parents)
        else:
            if not exist_ok:
                raise FileExistsError(self.path)

    @_gdrive_retry
    def write_bytes(self, contents):
        with self.client.open(self.path, mode="wb") as stream:
            stream.write(contents)

    @_gdrive_retry
    def _read(self, mode):
        with self.client.open(self.path, mode=mode) as stream:
            return stream.read()

    read_bytes = partialmethod(_read, mode="rb")
