import os

from src.plugins.history import HistoryPlugin
from src.terminal import Terminal


def quotes(inp: str) -> list[str]:
    """Добавляет к именам с пробелами кавычки"""
    res = []
    curr = ""
    single = False
    double = False

    for char in inp:
        if char == "'" and not double:
            single = not single
        elif char == '"' and not single:
            double = not double
        elif char == " " and not single and not double:
            if curr:
                res.append(curr)
                curr = ""
        else:
            curr += char

    if curr:
        res.append(curr)

    return res


def main() -> None:
    """Запуск эмулятора терминала"""
    terminal = Terminal()
    history_plugin = HistoryPlugin(terminal.logger)

    while True:
        try:
            curr_dir = os.getcwd()
            home_dir = os.path.expanduser("~")
            if curr_dir.startswith(home_dir):
                curr_dir = "~" + curr_dir[len(home_dir) :]

            inp = input(f"{curr_dir} $ ").strip()

            if not inp:
                continue

            command = quotes(inp)

            if not command:
                continue

            command_name, args = command[0], command[1:]

            # добавляем команду в историю
            history_plugin.add_command(command_name, args)

            # выполняем команду
            match command_name:
                case "ls":
                    terminal.ls(args)
                case "cd":
                    terminal.cd(args)
                case "cat":
                    terminal.cat(args)
                case "cp":
                    terminal.cp(args)
                    history_plugin.record_for_undo(command_name, args)
                case "mv":
                    terminal.mv(args)
                    history_plugin.record_for_undo(command_name, args)
                case "rm":
                    backup_info = history_plugin.create_backup(args)
                    terminal.rm(args)
                    history_plugin.record_for_undo(command_name, args, backup_info)
                case "zip":
                    terminal.archive_plugin.zip(args)
                case "unzip":
                    terminal.archive_plugin.unzip(args)
                case "tar":
                    terminal.archive_plugin.tar(args)
                case "untar":
                    terminal.archive_plugin.untar(args)
                case "grep":
                    terminal.search_plugin.grep(args)
                case "history":
                    history_plugin.show_history(args)
                case "undo":
                    history_plugin.undo(args)
                case "exit":
                    break
                case _:
                    unknown_cmd = f"{command_name} {' '.join(args)}"
                    terminal.logger.error(f"ERROR: Unknown command: {unknown_cmd}")
                    print(f"ERROR: Unknown command: {unknown_cmd}")

        except Exception as e:
            error_msg = str(e)
            if error_msg.startswith("["):
                error_msg = error_msg.split("] ", 1)[1]
            print(f"ERROR: {error_msg}")


if __name__ == "__main__":
    main()
