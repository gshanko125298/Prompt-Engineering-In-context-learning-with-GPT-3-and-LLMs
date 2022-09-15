import os

import pytest

from .cloud import HTTP
from .httpd import StaticFileServer


@pytest.fixture(scope="session")
def http_server(tmp_path_factory):
    directory = os.fspath(tmp_path_factory.mktemp("http"))
    with StaticFileServer(directory=directory) as httpd:
        yield httpd


@pytest.fixture
def make_http(http_server):
    def _make_http():
        return HTTP(HTTP.get_url(http_server.server_port))

    return _make_http


@pytest.fixture
def http(make_http):
    return make_http()
