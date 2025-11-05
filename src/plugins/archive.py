import logging
import os
import shutil

from src.logger import log


class ArchivePlugin:
    """Плагин для работы с архивами"""

    def __init__(self, logger: logging.Logger) -> None:
        """Инициализация логгера"""
        self.logger = logger

    @log
    def zip(self, args: list[str]) -> None:
        """Создание zip архива"""
        if len(args) != 2:
            raise Exception("Usage: zip <folder> <archive>")

        folder, archive = args[0], args[1]
        if not archive.endswith(".zip"):
            archive += ".zip"

        shutil.make_archive(archive.replace(".zip", ""), "zip", folder)
        print(f"Created: {archive}")

    @log
    def unzip(self, args: list[str]) -> None:
        """Распаковка zip архива"""
        if len(args) != 1:
            raise Exception("Usage: unzip <archive>")

        archive = args[0]
        if not archive.endswith(".zip"):
            archive += ".zip"

        extract_dir = archive.replace(".zip", "")
        os.makedirs(extract_dir, exist_ok=True)

        shutil.unpack_archive(archive, extract_dir)
        print(f"Extracted: {archive} to {extract_dir}/")

    @log
    def tar(self, args: list[str]) -> None:
        """Создание tar.gz архива"""
        if len(args) != 2:
            raise Exception("Usage: tar <folder> <archive>")

        folder, archive = args[0], args[1]
        if not archive.endswith(".tar.gz"):
            archive += ".tar.gz"

        shutil.make_archive(archive.replace(".tar.gz", ""), "gztar", folder)
        print(f"Created: {archive}")

    @log
    def untar(self, args: list[str]) -> None:
        """Распаковка tar.gz архива"""
        if len(args) != 1:
            raise Exception("Usage: untar <archive>")

        archive = args[0]
        if not archive.endswith(".tar.gz"):
            archive += ".tar.gz"

        extract_dir = archive.replace(".tar.gz", "")
        os.makedirs(extract_dir, exist_ok=True)

        shutil.unpack_archive(archive, extract_dir)
        print(f"Extracted: {archive} to {extract_dir}/")
