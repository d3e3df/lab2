import os

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from src.plugins.archive import ArchivePlugin
from src.plugins.history import HistoryPlugin
from src.plugins.search import SearchPlugin
from src.terminal import Terminal


@pytest.fixture
def terminal() -> Terminal:
    """Терминал"""
    return Terminal()


@pytest.fixture
def archive(terminal):
    """Архивы"""
    return ArchivePlugin(terminal.logger)


@pytest.fixture
def search(terminal):
    """Поиск"""
    return SearchPlugin(terminal.logger)


@pytest.fixture
def history(terminal):
    """История"""
    return HistoryPlugin(terminal.logger)


@pytest.fixture
def fake_fs(fs: FakeFilesystem) -> FakeFilesystem:
    """Фейковая файловая система для всех тестов"""
    fs.create_dir("/home/user")
    fs.create_file("/home/user/test1.txt", contents="content1")
    fs.create_file("/home/user/test2.txt", contents="content2")
    fs.create_dir("/home/user/documents")
    fs.create_file("/home/user/documents/doc1.txt", contents="content")

    def fake_expanduser(path):
        if path == "~":
            return "/home/user"
        return path

    os.path.expanduser = fake_expanduser
    os.chdir("/home/user")
    return fs
