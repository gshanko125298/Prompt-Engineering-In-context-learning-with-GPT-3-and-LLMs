import pytest
from dvc.testing.test_api import TestAPI  # noqa, pylint: disable=unused-import
from dvc.testing.test_remote import (  # noqa, pylint: disable=unused-import
    TestRemote,
)
from dvc.testing.test_workspace import TestImport as _TestImport


@pytest.fixture
def remote(make_remote):
    yield make_remote(name="upstream", typ="http")


@pytest.fixture
def workspace(make_workspace):
    yield make_workspace(name="workspace", typ="http")


class TestImport(_TestImport):
    @pytest.fixture
    def stage_md5(self):
        return "2aa17f8daa26996b3f7a4cf8888ac9ac"

    @pytest.fixture
    def is_object_storage(self):
        pytest.skip("broken")

    @pytest.fixture
    def dir_md5(self):
        pytest.skip("broken")
