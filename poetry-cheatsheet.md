# Poetry — шпаргалка

> Менеджер зависимостей и упаковщик пакетов для Python.  
> Официальный сайт: https://python-poetry.org

---

## Установка

```bash
# macOS / Linux
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Проверить установку
poetry --version
```

---

## Создание нового проекта

```bash
# Создать проект с нуля (папка + pyproject.toml + структура)
poetry new sandbox-ideas

# Перейти в проект
cd sandbox-ideas
```

Структура после создания:

```
sandbox-ideas/
├── pyproject.toml       # главный конфиг проекта
├── README.md
├── sandbox_ideas/
│   └── __init__.py
└── tests/
    └── __init__.py
```

### Инициализация в существующей папке

```bash
mkdir my-project && cd my-project
poetry init        # интерактивный мастер настройки
```

---

## pyproject.toml — основной конфиг

```toml
[tool.poetry]
name = "sandbox-ideas"
version = "0.1.0"
description = "Площадка для экспериментов"
authors = ["Dmitrii Frolov <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
requests = "^2.31"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
black = "^23.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

---

## Виртуальное окружение

```bash
# Poetry создаёт venv автоматически при первой установке зависимостей
# По умолчанию хранится в ~/.cache/pypoetry/virtualenvs/

# Показать информацию об окружении
poetry env info

# Показать путь к Python
poetry run python --version

# Список всех venv для проекта
poetry env list

# Активировать оболочку внутри venv
poetry shell

# Выйти из оболочки venv
exit

# Запустить команду без активации venv
poetry run python script.py
poetry run pytest

# Удалить venv
poetry env remove python3.11

# Хранить venv внутри папки проекта (удобно для IDE)
poetry config virtualenvs.in-project true
```

---

## Управление зависимостями

### Добавление

```bash
# Добавить пакет (последняя совместимая версия)
poetry add requests

# Добавить конкретную версию
poetry add "requests==2.31.0"

# Добавить с ограничением версии
poetry add "fastapi>=0.100,<1.0"

# Добавить в группу dev
poetry add pytest --group dev

# Добавить в группу test
poetry add httpx --group test

# Добавить из git-репозитория
poetry add git+https://github.com/user/repo.git
```

### Удаление

```bash
poetry remove requests
poetry remove pytest --group dev
```

### Обновление

```bash
# Обновить все зависимости
poetry update

# Обновить конкретный пакет
poetry update requests

# Только проверить что можно обновить (без изменений)
poetry show --outdated
```

---

## Установка зависимостей

```bash
# Установить всё из pyproject.toml (создаёт/обновляет poetry.lock)
poetry install

# Установить без dev-зависимостей (продакшн)
poetry install --without dev

# Установить только конкретную группу
poetry install --only test

# Пересоздать окружение с нуля
poetry install --sync
```

---

## Просмотр зависимостей

```bash
# Список всех установленных пакетов
poetry show

# Только прямые зависимости (без транзитивных)
poetry show --only main

# Дерево зависимостей — видно кто от кого зависит
poetry show --tree

# Дерево для конкретного пакета
poetry show requests --tree

# Устаревшие пакеты
poetry show --outdated

# Подробная информация о пакете
poetry show requests
```

Пример вывода `poetry show --tree`:

```
requests 2.31.0 Python HTTP for Humans.
├── certifi >=2017.4.17
├── charset-normalizer >=2,<4
├── idna >=2.5,<4
└── urllib3 >=1.21.1,<3
pytest 7.4.3 pytest: simple powerful testing with Python
├── iniconfig *
├── packaging *
└── pluggy >=0.12,<2
```

---

## Версии Python

```bash
# Показать доступные версии Python в системе
poetry env use python3.11

# Переключить версию Python для проекта
poetry env use 3.10

# Использовать системный Python
poetry env use system
```

> Poetry не устанавливает Python сам — используй pyenv или системный пакетный менеджер.

---

## Публикация пакета

```bash
# Сбилдить пакет (wheel + sdist)
poetry build

# Опубликовать на PyPI
poetry publish

# Сбилдить и сразу опубликовать
poetry publish --build

# Опубликовать на тестовый PyPI
poetry publish -r testpypi
```

---

## Полезные команды

```bash
# Показать текущую конфигурацию Poetry
poetry config --list

# Проверить pyproject.toml на ошибки
poetry check

# Показать информацию об окружении
poetry env info

# Экспортировать зависимости в requirements.txt
poetry export -f requirements.txt --output requirements.txt

# Экспортировать без dev-зависимостей
poetry export -f requirements.txt --without dev --output requirements.txt

# Версия Poetry
poetry --version

# Обновить сам Poetry
poetry self update
```

---

## Шаблон .gitignore для Poetry

```gitignore
# venv внутри проекта (если virtualenvs.in-project = true)
.venv/

# Дистрибутив
dist/

# Кэш
__pycache__/
*.pyc
.pytest_cache/
```

> `poetry.lock` — **коммитить обязательно**.  
> Он фиксирует точные версии всех зависимостей для воспроизводимой сборки.

---

## Быстрый старт — от нуля до запуска

```bash
poetry new sandbox-ideas          # создать проект
cd sandbox-ideas                  # перейти в папку
poetry add requests fastapi       # добавить зависимости
poetry add pytest --group dev     # добавить dev-зависимость
poetry install                    # установить всё
poetry shell                      # активировать venv
poetry show --tree                # посмотреть дерево зависимостей
poetry run python sandbox_ideas/__init__.py  # запустить скрипт
```

---

## Таблица: Poetry vs pip

| Задача                    | pip                          | Poetry                        |
|---------------------------|------------------------------|-------------------------------|
| Установить пакет          | `pip install requests`       | `poetry add requests`         |
| Удалить пакет             | `pip uninstall requests`     | `poetry remove requests`      |
| Заморозить зависимости    | `pip freeze > requirements.txt` | `poetry.lock` (автоматически) |
| Dev-зависимости           | отдельный файл вручную       | `--group dev`                 |
| Создать venv              | `python -m venv .venv`       | автоматически                 |
| Дерево зависимостей       | `pipdeptree` (сторонний)     | `poetry show --tree`          |
| Публикация на PyPI        | `twine`                      | `poetry publish`              |
