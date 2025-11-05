import logging
import os
import shutil

from src.logger import log


class HistoryPlugin:
    """Плагин для истории команд и отмены действий"""

    def __init__(self, logger: logging.Logger) -> None:

        self.logger = logger
        self.history_file = os.path.join(os.path.dirname(__file__), ".history")
        self.trash_dir = os.path.join(os.path.dirname(__file__), ".trash")
        self.history: list[dict] = []
        self.undo_stack: list[dict] = []
        self.load_history()

        # создаем директорию для корзины
        os.makedirs(self.trash_dir, exist_ok=True)

    def load_history(self) -> None:
        """Загружает историю из файла"""
        self.history = []
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            history_item = {
                                "command": line,
                                "args": [],
                                "cwd": os.getcwd(),
                            }
                            self.history.append(history_item)
        except Exception:
            self.history = []

    def save_history(self) -> None:
        """Сохраняет историю в файл"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                for item in self.history:
                    command = item["command"]
                    f.write(f"{command}\n")
        except Exception:
            pass

    def add_command(self, command: str, args: list[str]) -> None:
        """Добавляет команду в историю"""
        history_item = {
            "command": f"{command} {' '.join(args)}".strip(),
            "args": args,
            "cwd": os.getcwd(),
        }
        self.history.append(history_item)
        self.save_history()

    def create_backup(self, args: list[str]) -> list[dict]:
        """Создает резервные копии файлов"""
        recursive = "-r" in args
        targets = [arg for arg in args if arg != "-r"]

        backup_info = []
        for target in targets:
            target_path = os.path.abspath(target)

            if os.path.exists(target_path):
                trash_name = os.path.basename(target_path)
                trash_path = os.path.join(self.trash_dir, trash_name)

                # если файл уже существует, добавляем номер
                counter = 1
                while os.path.exists(trash_path):
                    trash_name = f"{trash_name}({counter})"
                    trash_path = os.path.join(self.trash_dir, trash_name)
                    counter += 1

                try:
                    if os.path.isfile(target_path):
                        shutil.copy2(target_path, trash_path)
                        backup_info.append(
                            {"original_path": target_path, "trash_path": trash_path}
                        )
                    elif os.path.isdir(target_path) and recursive:
                        shutil.copytree(target_path, trash_path)
                        backup_info.append(
                            {"original_path": target_path, "trash_path": trash_path}
                        )
                except Exception as e:
                    print(f"Error creating backup: {e}")

        return backup_info

    def record_for_undo(
        self, command: str, args: list[str], backup_info: list[dict] | None = None
    ) -> None:
        """Записывает операцию для возможной отмены"""
        if command not in ["cp", "mv", "rm"]:
            return

        undo_info = {
            "command": command,
            "args": args.copy(),
            "cwd": os.getcwd(),
            "backup_info": backup_info,
        }
        self.undo_stack.append(undo_info)

    @log
    def show_history(self, args: list[str]) -> None:
        """Выводит историю команд"""
        if not self.history:
            print("No commands in history")
            return

        if args:
            try:
                n = int(args[0])
                if n <= 0:
                    raise ValueError("Number must be positive")
                start_idx = max(0, len(self.history) - n)
                history_to_show = self.history[start_idx:]
            except ValueError:
                raise Exception("History requires a positive number argument")
        else:
            history_to_show = self.history

        start_number = len(self.history) - len(history_to_show) + 1
        for i, item in enumerate(history_to_show, start=start_number):
            print(f"{i:4d}  {item['command']}")

    @log
    def undo(self, args: list[str]) -> None:
        """Отменяет последнюю операцию из списка cp, mv, rm"""
        if not self.undo_stack:
            print("No operations to undo")
            return

        last_op = self.undo_stack.pop()
        command = last_op["command"]

        try:
            old_cwd = os.getcwd()
            if last_op["cwd"] != old_cwd:
                os.chdir(last_op["cwd"])

            success = False
            if command == "cp":
                success = self.undo_cp(last_op)
            elif command == "mv":
                success = self.undo_mv(last_op)
            elif command == "rm":
                success = self.undo_rm(last_op)

            if success:
                print(f"Undo: {command} {' '.join(last_op['args'])}")
            else:
                print(f"Failed to undo {command}")
                self.undo_stack.append(last_op)

        except Exception as e:
            print(f"Failed to undo {command}: {e}")
            self.undo_stack.append(last_op)
        finally:
            if last_op["cwd"] != old_cwd:
                os.chdir(old_cwd)

    def undo_cp(self, operation: dict) -> bool:
        """Отмена cp"""
        args = operation["args"]
        recursive = "-r" in args

        source = None
        destination = None
        for arg in args:
            if arg == "-r":
                continue
            elif source is None:
                source = arg
            else:
                destination = arg

        if not source or not destination:
            return False

        source_path = os.path.abspath(source)
        dest_path = os.path.abspath(destination)

        if os.path.exists(dest_path) and os.path.isdir(dest_path):
            source_name = os.path.basename(source_path)
            target_path = os.path.join(dest_path, source_name)
        else:
            target_path = dest_path

        paths_to_try = [target_path, dest_path]

        for path in paths_to_try:
            if os.path.exists(path):
                try:
                    if os.path.isfile(path):
                        os.remove(path)
                        return True
                    elif os.path.isdir(path) and recursive:
                        shutil.rmtree(path)
                        return True
                except Exception:
                    continue

        return False

    def undo_mv(self, operation: dict) -> bool:
        """Отмена mv"""
        args = operation["args"]
        if len(args) != 2:
            return False

        source, destination = args[0], args[1]
        source_path = os.path.abspath(source)
        dest_path = os.path.abspath(destination)

        if os.path.isdir(dest_path):
            actual_dest = os.path.join(dest_path, os.path.basename(source_path))
        else:
            actual_dest = dest_path

        if os.path.exists(actual_dest):
            try:
                os.makedirs(os.path.dirname(source_path), exist_ok=True)
                shutil.move(actual_dest, source_path)
                return True
            except Exception:
                return False

        return False

    def undo_rm(self, operation: dict) -> bool:
        """Отмена rm"""
        backup_info = operation.get("backup_info", [])

        if not backup_info:
            print("No files to restore from trash")
            return False

        success_count = 0
        for file_info in backup_info:
            original_path = file_info.get("original_path")
            trash_path = file_info.get("trash_path")

            if trash_path and os.path.exists(trash_path):
                try:
                    shutil.move(trash_path, original_path)
                    success_count += 1
                except Exception as e:
                    print(f"Error restoring {trash_path}: {e}")

        return success_count > 0
