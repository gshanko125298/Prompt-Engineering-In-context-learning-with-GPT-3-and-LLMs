import pytest

from .cloud import GDrive


@pytest.fixture
def make_gdrive():
    def _make_gdrive():
        ret = GDrive(GDrive.get_url())
        ret.mkdir(ret.url)
        return ret

    return _make_gdrive


@pytest.fixture
def gdrive(make_gdrive):
    return make_gdrive()
