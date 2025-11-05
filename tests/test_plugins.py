import os

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest import CaptureFixture, MonkeyPatch

from src.plugins.archive import ArchivePlugin
from src.plugins.history import HistoryPlugin
from src.plugins.search import SearchPlugin
from src.terminal import Terminal


class TestArchivePlugin:
    """Тест плагина для работы с архивами"""

    def test_zip(self, archive: ArchivePlugin, fake_fs: FakeFilesystem) -> None:
        """Тест zip"""
        archive.zip(["documents", "archive"])
        assert os.path.exists("/home/user/archive.zip")
        archive.unzip(["archive.zip"])
        assert os.path.exists("/home/user/archive/doc1.txt")

    def test_zip_error(self, archive: ArchivePlugin, fake_fs: FakeFilesystem) -> None:
        """Тест ошибок zip"""
        with pytest.raises(Exception, match="Usage: zip <folder> <archive>"):
            archive.zip(["documents", "archive.zip", "abc"])

    def test_unzip_error(self, archive: ArchivePlugin, fake_fs: FakeFilesystem) -> None:
        """Тест ошибок unzip"""
        with pytest.raises(Exception, match="Usage: unzip <archive>"):
            archive.unzip(["archive.zip", "abc"])


class TestSearchPlugin:
    """Тест плагина для поиска файлов"""

    def test_grep_r(
        self, search: SearchPlugin, fake_fs: FakeFilesystem, capsys: CaptureFixture[str]
    ) -> None:
        """Тест grep"""
        search.grep([r"\w+", "/home", "-r"])
        output = capsys.readouterr().out.strip()
        assert "/home/user/test1.txt:1: content1" in output
        assert "/home/user/test2.txt:1: content2" in output
        assert "/home/user/documents/doc1.txt:1: content" in output

    def test_grep_i(
        self, search: SearchPlugin, fake_fs: FakeFilesystem, capsys: CaptureFixture[str]
    ) -> None:
        """Тест grep без учета регистра"""
        fake_fs.create_file("/home/user/documents/test3.txt", contents="CONTENT")
        search.grep(["content", "/home/user/documents"])
        output = capsys.readouterr().out.strip()
        assert "content" in output
        assert "CONTENT" not in output
        search.grep(["content", "/home/user/documents", "-i"])
        output = capsys.readouterr().out.strip()
        assert "content" in output
        assert "CONTENT" in output

    def test_grep_errors(self, search: SearchPlugin, fake_fs: FakeFilesystem) -> None:
        """Тест ошибок grep"""
        with pytest.raises(
            Exception, match=r"Usage: grep <pattern> <path> \[-r\] \[-i\]"
        ):
            search.grep(["abc"])


class TestHistoryPlugin:
    """Тест плагина для истории и отмены действий"""

    def test_undo_rm(
        self,
        terminal: Terminal,
        history: HistoryPlugin,
        fake_fs: FakeFilesystem,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Тест undo rm"""
        args = ["-r", "documents"]
        backup_info = history.create_backup(args)
        monkeypatch.setattr("builtins.input", lambda _: "y")
        terminal.rm(args)
        history.record_for_undo("rm", args, backup_info)
        assert not os.path.exists("/home/user/documents")
        history.undo(args)
        assert os.path.exists("/home/user/documents")

    def test_undo_cp(
        self, terminal: Terminal, history: HistoryPlugin, fake_fs: FakeFilesystem
    ) -> None:
        """Тест undo cp"""
        args = ["test1.txt", "documents"]
        backup_info = history.create_backup(args)
        terminal.cp(args)
        history.record_for_undo("cp", args, backup_info)
        assert os.path.exists("/home/user/test1.txt")
        assert os.path.exists("/home/user/documents/test1.txt")
        history.undo(args)
        assert os.path.exists("/home/user/test1.txt")
        assert not os.path.exists("/home/user/documents/test1.txt")

    def tests_undo_mv(
        self, terminal: Terminal, history: HistoryPlugin, fake_fs: FakeFilesystem
    ) -> None:
        """Тест undo mv"""
        args = ["test1.txt", "documents"]
        backup_info = history.create_backup(args)
        terminal.mv(args)
        history.record_for_undo("mv", args, backup_info)
        assert not os.path.exists("/home/user/test1.txt")
        assert os.path.exists("/home/user/documents/test1.txt")
        history.undo(args)
        assert os.path.exists("/home/user/test1.txt")
        assert not os.path.exists("/home/user/documents/test1.txt")
