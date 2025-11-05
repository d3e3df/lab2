import logging
import os
import shutil
import stat
from datetime import datetime

from src.logger import log
from src.plugins.archive import ArchivePlugin
from src.plugins.search import SearchPlugin

# настройка логирования
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), "shell.log"),
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class Terminal:
    """Эмулятор терминала с основными командами"""

    def __init__(self) -> None:
        """Инициализация логгера"""
        self.logger = logging.getLogger()

        self.archive_plugin = ArchivePlugin(self.logger)
        self.search_plugin = SearchPlugin(self.logger)

    @log
    def ls(self, args: list[str]) -> None:
        """Выводит содержимое директории"""
        path = "."
        detailed = False

        # парсим аргументы
        for arg in args:
            if arg == "-l":
                detailed = True
            else:
                path = arg

        # проверка на валидность
        if len(args) > 2 or (len(args) == 2 and not detailed):
            raise Exception("Too many arguments")

        # исполнение команды ls
        files = os.listdir(path)
        files = [i for i in files if i[0] != "."]

        # если директория пустая - выходим
        if not files:
            return

        if detailed:
            # находим максимальную длину размера файла
            max_size_len = 0
            for file in files:
                file_path = os.path.join(path, file)
                info = os.stat(file_path)
                max_size_len = max(max_size_len, len(str(info.st_size)))

            # вывод -l
            for file in files:
                file_path = os.path.join(path, file)
                info = os.stat(file_path)
                size = info.st_size
                date = datetime.fromtimestamp(info.st_mtime).strftime("%b %d %H:%M")
                permissions = stat.filemode(info.st_mode)
                print(f"{permissions} {size:>{max_size_len}} {date} {file}")
        else:
            # ширина терминала
            try:
                width = os.get_terminal_size().columns
            except OSError:
                width = 100

            # для файлов с пробелами добавляем кавычки при выводе
            formatted_files = []
            for file in files:
                if " " in file or "'" in file or '"' in file:
                    # если есть одинарные кавычки, используем двойные и наоборот
                    if "'" in file:
                        formatted_files.append(f'"{file}"')
                    else:
                        formatted_files.append(f"'{file}'")
                else:
                    formatted_files.append(file)

            max_name_length = max(len(name) for name in formatted_files) + 3
            columns_count = max(1, width // max_name_length)
            rows_count = (len(formatted_files) + columns_count - 1) // columns_count

            # вывод
            for row in range(rows_count):
                line = ""
                for col in range(columns_count):
                    # вычисляем индекс файла в массиве
                    index = row + col * rows_count
                    if index < len(formatted_files):
                        # добавляем файл с выравниванием
                        line += f"{formatted_files[index]:<{max_name_length}}"
                print(line)

    @log
    def cd(self, args: list[str]) -> None:
        """Меняет текущую директорию"""
        if len(args) == 0:
            # cd без аргументов - переходим в домашнюю директорию
            new_path = os.path.expanduser("~")
        elif len(args) == 1:
            path = args[0]

            # обработка аргументов
            if path == "~":
                new_path = os.path.expanduser("~")
            elif path == "..":
                new_path = os.path.dirname(os.getcwd())
            else:
                new_path = os.path.abspath(path)
        else:
            raise Exception("Too many arguments")

        # меняем директорию
        os.chdir(new_path)

    @log
    def cat(self, args: list[str]) -> None:
        """Выводит содержимое файла"""
        if len(args) != 1:
            raise Exception("cat requires exactly one argument")

        filename = args[0]

        # читаем и выводим содержимое
        with open(filename, "r", encoding="utf-8") as file:
            print(file.read(), end="")

    @log
    def cp(self, args: list[str]) -> None:
        """Копирует файл или директорию"""
        if len(args) < 2 or len(args) > 3:
            raise Exception("cp requires source and destination arguments")

        recursive = False
        source = None
        destination = None

        # парсим аргументы
        for arg in args:
            if arg == "-r":
                recursive = True
            elif source is None:
                source = arg
            else:
                destination = arg

        if not source or not destination:
            raise Exception("cp requires source and destination arguments")

        # раскрываем тильду в путях
        source = os.path.expanduser(source)
        destination = os.path.expanduser(destination)

        # проверяем существование источника
        if not os.path.exists(source):
            raise Exception(f"No such file or directory: {source}")

        try:
            if os.path.isfile(source):
                # копируем файл
                shutil.copy2(source, destination)

            elif os.path.isdir(source):
                if recursive:
                    # для директорий используем copytree
                    shutil.copytree(source, destination)
                else:
                    raise Exception(f"Is a directory (use -r for recursive): {source}")
            else:
                raise Exception(f"Unknown file type: {source}")

        except Exception as e:
            raise Exception(f"Cannot copy {source} to {destination}: {str(e)}")

    @log
    def mv(self, args: list[str]) -> None:
        """Перемещает или переименовывает файлы и директории"""
        if len(args) != 2:
            raise Exception("mv requires source and destination arguments")

        source, destination = args[0], args[1]

        # проверяем существование источника
        if not os.path.exists(source):
            raise Exception(f"No such file or directory: {source}")

        # определяем конечный путь
        if os.path.isdir(destination):
            dest_path = os.path.join(destination, os.path.basename(source))
        else:
            dest_path = destination

        # подтверждение перезаписи от пользователя
        if os.path.exists(dest_path):
            response = input(f"Overwrite '{dest_path}'? (y/n): ")
            if response.lower() != "y":
                return

        # выполняем перемещение
        try:
            shutil.move(source, dest_path)
        except Exception as e:
            raise Exception(f"Cannot move {source} to {destination}: {str(e)}")

    @log
    def rm(self, args: list[str]) -> None:
        """Удаляет файлы и директории"""
        if len(args) == 0:
            raise Exception("rm requires at least one argument")

        recursive = False
        targets = []

        # парсим аргументы
        for arg in args:
            if arg == "-r":
                recursive = True
            else:
                targets.append(arg)

        if not targets:
            raise Exception("rm requires at least one target")

        for target in targets:
            self.remove_target(target, recursive)

    def remove_target(self, target: str, recursive: bool) -> None:
        """Удаляет файлы и директории"""
        # проверяем существование
        if not os.path.exists(target):
            raise Exception(f"No such file or directory: {target}")

        # защита от удаления корневой и родительских директорий
        abs_path = os.path.abspath(target)
        if abs_path == "/" or abs_path == os.path.abspath(".."):
            raise Exception(f"Refusing to remove '{target}' - system protection")

        if os.path.isfile(target):
            # удаление файла
            try:
                os.remove(target)
            except Exception as e:
                raise Exception(f"Cannot remove '{target}': {str(e)}")

        elif os.path.isdir(target):
            # удаление директории
            if not recursive:
                raise Exception(f"Is a directory (use -r for recursive): {target}")

            # запрашиваем подтверждение для директории
            response = input(f"Remove directory '{target}' recursively? (y/n): ")
            if response.lower() != "y":
                return

            try:
                shutil.rmtree(target)
            except Exception as e:
                raise Exception(f"Cannot remove directory '{target}': {str(e)}")

        else:
            raise Exception(f"Unknown file type: {target}")
