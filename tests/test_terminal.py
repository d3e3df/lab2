import os

from pyfakefs.fake_filesystem import FakeFilesystem
from pytest import CaptureFixture, MonkeyPatch

from src.terminal import Terminal


class TestLS:
    """Тест ls"""

    def test_ls(
        self, terminal: Terminal, fake_fs: FakeFilesystem, capsys: CaptureFixture[str]
    ) -> None:
        """Тест ls"""
        terminal.ls([])
        output = capsys.readouterr().out.strip().split()

        assert output == ["test1.txt", "test2.txt", "documents"]

    def test_detailed_ls(
        self, terminal: Terminal, fake_fs: FakeFilesystem, capsys: CaptureFixture[str]
    ) -> None:
        """Тест detailed ls"""
        terminal.ls(["-l"])
        output = capsys.readouterr().out
        lines = output.strip().split("\n")

        assert len(lines) == 3
        # проверяем файл test1.txt
        assert lines[0].startswith("-rw-")  # права
        assert " 8 " in lines[0]  # размер
        assert lines[0].endswith(" test1.txt")
        # проверяем test2.txt
        assert lines[1].startswith("-rw-")  # права
        assert " 8 " in lines[1]  # размер
        assert lines[1].endswith(" test2.txt")
        # проверяем documents
        assert lines[2].startswith("drwx")  # права
        assert " 0 " in lines[2]  # размер
        assert lines[2].endswith(" documents")


class TestCD:
    """Тест cd"""

    def test_cd(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест cd"""
        terminal.cd([".."])
        assert os.getcwd() == "/home"
        terminal.cd(["~"])
        assert os.getcwd() == "/home/user"
        terminal.cd(["documents"])
        assert os.getcwd() == "/home/user/documents"
        terminal.cd([])
        assert os.getcwd() == "/home/user"
        terminal.cd(["../.."])
        assert os.getcwd() == "/"
        terminal.cd(["/home/user/documents"])
        assert os.getcwd() == "/home/user/documents"


class TestCAT:
    """Тест cat"""

    def test_cat(
        self, terminal: Terminal, fake_fs: FakeFilesystem, capsys: CaptureFixture[str]
    ) -> None:
        """Тест cat"""
        terminal.cat(["test1.txt"])
        output1 = capsys.readouterr().out.strip()
        terminal.cat(["test2.txt"])
        output2 = capsys.readouterr().out.strip()
        assert output1 == "content1"
        assert output2 == "content2"


class TestCP:
    """Тест cp"""

    def test_cp_file(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест cp с файлом"""
        terminal.cp(["test1.txt", "documents"])
        assert os.path.exists("/home/user/documents/test1.txt")

    def test_cp_dir(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест cp с директорией"""
        terminal.cp(["-r", "documents", "test_dir"])
        assert os.path.exists("/home/user/test_dir/doc1.txt")


class TestMV:
    """Тест mv"""

    def test_mv_rename(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест mv переименование"""
        terminal.mv(["test1.txt", "renamed.txt"])
        assert not os.path.exists("/home/user/test1.txt")
        assert os.path.exists("/home/user/renamed.txt")

    def test_mv_move_file_to_dir(
        self, terminal: Terminal, fake_fs: FakeFilesystem
    ) -> None:
        """Тест mv файл в директорию"""
        terminal.mv(["test1.txt", "documents"])
        assert not os.path.exists("/home/user/test1.txt")
        assert os.path.exists("/home/user/documents/test1.txt")

    def test_mv_move_dir(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест mv директория"""
        terminal.mv(["documents", "/home"])
        assert os.path.exists("/home/documents/doc1.txt")
        assert not os.path.exists("/home/user/documents")

    def test_mv_overwrite(
        self, terminal: Terminal, fake_fs: FakeFilesystem, monkeypatch: MonkeyPatch
    ) -> None:
        """Тест mv перезапись"""
        monkeypatch.setattr("builtins.input", lambda _: "y")
        terminal.mv(["test1.txt", "test2.txt"])
        with open("/home/user/test2.txt", "r") as f:
            content = f.read()
            assert content == "content1"


class TestRM:
    """Тест rm"""

    def test_rm_file(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест удаление файла"""
        terminal.rm(["test1.txt"])
        assert not os.path.exists("/home/user/test1.txt")
        assert os.path.exists("/home/user/test2.txt")

    def test_rm_files(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест удаления нескольких файлов"""
        terminal.rm(["test1.txt", "test2.txt"])
        assert not os.path.exists("/home/user/test1.txt")
        assert not os.path.exists("/home/user/test2.txt")

    def test_rm_dir(
        self, terminal: Terminal, fake_fs: FakeFilesystem, monkeypatch: MonkeyPatch
    ) -> None:
        """Тест удаления директории"""
        monkeypatch.setattr("builtins.input", lambda _: "y")
        terminal.rm(["-r", "documents"])
        assert not os.path.exists("/home/user/documents")
