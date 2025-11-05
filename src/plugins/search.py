import logging
import os
import re

from src.logger import log


class SearchPlugin:
    """Плагин для поиска по содержимому файлов"""

    def __init__(self, logger: logging.Logger) -> None:
        """Инициализация логгера"""
        self.logger = logger

    @log
    def grep(self, args: list[str]) -> None:
        """Поиск по содержимому файлов"""
        if len(args) < 2:
            raise Exception("Usage: grep <pattern> <path> [-r] [-i]")

        # парсим аргументы
        pattern = args[0]
        path = args[1]
        recursive = "-r" in args
        ignore_case = "-i" in args

        # настраиваем регулярное выражение
        flags = re.IGNORECASE if ignore_case else 0
        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            raise Exception(f"Invalid pattern: {e}")

        # выполняем поиск
        if os.path.isfile(path):
            self.search_in_file(path, regex)
        elif os.path.isdir(path):
            if recursive:
                self.search_in_directory_recursive(path, regex)
            else:
                self.search_in_directory(path, regex)
        else:
            raise Exception(f"Path not found: {path}")

    def search_in_file(self, file_path: str, regex: re.Pattern) -> None:
        """Поиск в одном файле"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, 1):
                    if regex.search(line):
                        print(f"{file_path}:{line_num}: {line.rstrip()}")
        except Exception:
            pass

    def search_in_directory(self, directory: str, regex: re.Pattern) -> None:
        """Поиск в директории"""
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    self.search_in_file(item_path, regex)
        except Exception:
            pass

    def search_in_directory_recursive(self, directory: str, regex: re.Pattern) -> None:
        """Рекурсивный поиск в директории и поддиректориях"""
        try:
            for path, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(path, file)
                    self.search_in_file(file_path, regex)
        except Exception:
            pass
