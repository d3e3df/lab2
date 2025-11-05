# Эмулятор терминала Linux
## Структура проекта
```
lab2/
├── src/
│   ├── plugins/
│   │   ├── __init__.py
│   │   ├── archive.py
│   │   ├── history.py
│   │   ├── search.py
│   │   ├── .trash
│   │   └── .history
│   ├── __init__.py
│   ├── logger.py
│   ├── main.py
│   ├── terminal.py
│   └── shell.log
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_plugins.py
│   ├── test_terminal.py
│   └── test_terminal_errors.py
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── uv.lock
└── README.md
```
## Основные команды
- Выполнено в соответствии с требованиями лабораторной работы
## Плагины
- Выполнено в соответствии с требованиями лабораторной работы
## Запуск программы
```bash
python -m src.main
```
## Запуск тестов
```bash
pytest tests/
```
