# Assistant bot


## Содержание

- [Описание](#описание)
- [Запуск](#запуск)
- [Технологии](#технологии)
- [Автор](#автор)

## Описание

Assistant bot - опрашивает за вас интересующий API и уведомляет при изменении полученного статуса.


## Запуск

1. Клонирование репозитория:

```bash
git clone https://github.com/KlochkovAV/assistant_bot.git
```

2. Переход в рабочую директорию:

```bash
cd assistant_bot
```

3. Создание виртуального окружения:

```bash
python -m venv venv
```

4. Активация виртуального окружения:

Для Windows

```bash
source venv/Scripts/activate
```

Для Linux или MacOS

```bash
source venv/bin/activate
```

5. Обновление установщика pip:

```bash
python -m pip install --upgrade pip
```

6. Установка зависимостей:

```bash
pip install -r requirements.txt
```

7. Запуск бота:

```bash
python assistant.py
```

## Технологии
- [Python](https://www.python.org/)
- [PyTelegramBotApi](https://pypi.org/project/pyTelegramBotAPI/)


## Автор
Автор проекта: Клочков Артем (https://github.com/KlochkovAV)