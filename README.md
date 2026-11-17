# QUIZ BOT — Telegram викторина на Python

## Возможности
- Информатика, география, математика, история
- 10 вопросов в каждой категории, 4 варианта ответа
- Автоматическая проверка и подсчёт баллов
- Рейтинг игроков на SQLite
- Команды `/start`, `/top`, `/help`

## Локальный запуск
Требуется Python 3.10+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Скопируй `.env.example` в `.env`, вставь токен от @BotFather в `BOT_TOKEN`,
затем запусти `python bot.py`.

## GitHub
Создай приватный репозиторий и загрузи файлы. Не загружай `.env`.

## Bothost
Подключи GitHub-репозиторий в панели Bothost, выбери Python,
стартовый файл `bot.py`, добавь переменную окружения `BOT_TOKEN`.
Зависимости устанавливаются из `requirements.txt`.

Важно: для сохранения рейтинга между перезапусками SQLite-файл должен
храниться на постоянном диске хостинга. При отсутствии persistent storage
используй внешнюю базу данных.
