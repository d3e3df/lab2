import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from src.terminal import Terminal


class TestLSErrors:
    """Тест ошибок ls"""

    def test_ls_too_many_args(
        self, terminal: Terminal, fake_fs: FakeFilesystem
    ) -> None:
        """Тест много аргументов ls"""
        with pytest.raises(Exception, match="Too many arguments"):
            terminal.ls(["/home", "/home/user"])

    def test_ls_invalid_path(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест неверный путь ls"""
        with pytest.raises(Exception, match="No such file or directory"):
            terminal.ls(["/home/user/dir"])


class TestCDErrors:
    """Тест ошибок cd"""

    def test_cd_too_many_args(
        self, terminal: Terminal, fake_fs: FakeFilesystem
    ) -> None:
        """Тест много аргументов cd"""
        with pytest.raises(Exception, match="Too many arguments"):
            terminal.cd(["documents", "/home/user"])

    def test_cd_bad_dir(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест отсутствие директории"""
        with pytest.raises(Exception, match="No such file or directory"):
            terminal.cd(["dir"])


class TestCATErrors:
    """Тест ошибок cat"""

    def test_cat_no_args(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест нет аргументов"""
        with pytest.raises(Exception, match="cat requires exactly one argument"):
            terminal.cat([])

    def test_cat_too_many_args(
        self, terminal: Terminal, fake_fs: FakeFilesystem
    ) -> None:
        """Тест много аргументов"""
        with pytest.raises(Exception, match="cat requires exactly one argument"):
            terminal.cat(["test1", "test2"])

    def test_cat_bad_file(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест нет файла"""
        with pytest.raises(Exception, match="No such file or directory"):
            terminal.cat(["test3.txt"])

    def test_cat_directory(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест директория вместо файла"""
        with pytest.raises(Exception, match="Is a directory"):
            terminal.cat(["documents"])


class TestCPErrors:
    """Тест ошибок cp"""

    def test_cp_no_args(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест нет аргументов"""
        with pytest.raises(
            Exception, match="cp requires source and destination arguments"
        ):
            terminal.cp([])

    def test_cp_one_arg(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест один аргумент"""
        with pytest.raises(
            Exception, match="cp requires source and destination arguments"
        ):
            terminal.cp(["test1.txt"])

    def test_cp_too_many_args(
        self, terminal: Terminal, fake_fs: FakeFilesystem
    ) -> None:
        """Тест много аргументов"""
        with pytest.raises(
            Exception, match="cp requires source and destination arguments"
        ):
            terminal.cp(["-r", "documents", "/home", "/home/user"])

    def test_cp_bad_source(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест нет директории"""
        with pytest.raises(Exception, match="No such file or directory"):
            terminal.cp(["test3.txt", "/home/user/documents"])


class TestMVErrors:
    """Тест ошибок mv"""

    def test_mv_no_args(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест нет аргументов"""
        with pytest.raises(
            Exception, match="mv requires source and destination arguments"
        ):
            terminal.mv([])

    def test_mv_one_arg(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест один аргумент"""
        with pytest.raises(
            Exception, match="mv requires source and destination arguments"
        ):
            terminal.mv(["test1.txt"])

    def test_mv_too_many_args(
        self, terminal: Terminal, fake_fs: FakeFilesystem
    ) -> None:
        """Тест много аргументов"""
        with pytest.raises(
            Exception, match="mv requires source and destination arguments"
        ):
            terminal.mv(["-r", "documents", "/home", "/home/user"])

    def test_mv_bad_source(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест нет директории"""
        with pytest.raises(Exception, match="No such file or directory"):
            terminal.mv(["test3.txt", "/home/user/documents"])


class TestRMErrors:
    """Тест ошибок rm"""

    def test_rm_no_args(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест нет аргументов"""
        with pytest.raises(Exception, match="rm requires at least one argument"):
            terminal.rm([])

    def test_rm_one_arg(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест один аргумент"""
        with pytest.raises(Exception, match="rm requires at least one target"):
            terminal.rm(["-r"])

    def test_rm_bad_file(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест нет файла"""
        with pytest.raises(Exception, match="No such file or directory"):
            terminal.rm(["test3.txt"])

    def test_rm_protection(self, terminal: Terminal, fake_fs: FakeFilesystem) -> None:
        """Тест защита путей"""
        with pytest.raises(Exception, match="Refusing to remove"):
            terminal.rm(["/"])
        with pytest.raises(Exception, match="Refusing to remove"):
            terminal.rm([".."])
