import pytest
from dvc.testing.test_api import TestAPI  # noqa, pylint: disable=unused-import
from dvc.testing.test_remote import (  # noqa, pylint: disable=unused-import
    TestRemote,
)


@pytest.fixture
def remote(make_remote):
    yield make_remote(name="upstream", typ="gdrive")
