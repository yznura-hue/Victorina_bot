import logging
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = Path(os.getenv("DB_PATH", "quiz.sqlite3"))

QUIZZES = {
    "informatics": ("💻 Информатика", [
        ("Что означает CPU?", ["Центральный процессор", "Оперативная память", "Жёсткий диск", "Видеокарта"], 0),
        ("Какая система счисления лежит в основе работы компьютера?", ["Десятичная", "Двоичная", "Римская", "Шестнадцатеричная"], 1),
        ("Что из перечисленного является языком программирования?", ["HTML", "Python", "HTTP", "Wi-Fi"], 1),
        ("Какое устройство выводит изображение?", ["Клавиатура", "Монитор", "Мышь", "Микрофон"], 1),
        ("Что такое RAM?", ["Оперативная память", "Процессор", "Браузер", "Принтер"], 0),
        ("Какое расширение обычно имеет Python-файл?", [".docx", ".jpg", ".py", ".mp3"], 2),
        ("Что такое URL?", ["Адрес веб-ресурса", "Тип процессора", "Имя файла", "Антивирус"], 0),
        ("Какая клавиша удаляет символ слева от курсора?", ["Shift", "Ctrl", "Backspace", "Alt"], 2),
        ("Что такое браузер?", ["Программа для просмотра сайтов", "Операционная система", "Язык", "Мышь"], 0),
        ("Что из этого является операционной системой?", ["Windows", "Google", "Telegram", "Python"], 0),
    ]),
    "geography": ("🌍 География", [
        ("Какой океан самый большой?", ["Атлантический", "Индийский", "Тихий", "Северный Ледовитый"], 2),
        ("Столица Таджикистана?", ["Худжанд", "Душанбе", "Бохтар", "Куляб"], 1),
        ("На каком континенте находится Египет?", ["Африка", "Европа", "Австралия", "Южная Америка"], 0),
        ("Какая гора самая высокая в мире?", ["Эльбрус", "Килиманджаро", "Эверест", "Монблан"], 2),
        ("Самая большая жаркая пустыня?", ["Гоби", "Сахара", "Калахари", "Атакама"], 1),
        ("Какой материк самый маленький?", ["Африка", "Антарктида", "Австралия", "Евразия"], 2),
        ("Какая река протекает через Египет?", ["Амазонка", "Нил", "Дунай", "Волга"], 1),
        ("Сколько континентов в модели семи континентов?", ["5", "6", "7", "8"], 2),
        ("Столица Японии?", ["Пекин", "Сеул", "Токио", "Бангкок"], 2),
        ("Какое море находится между Европой и Африкой?", ["Каспийское", "Чёрное", "Красное", "Средиземное"], 3),
    ]),
    "math": ("🔢 Математика", [
        ("Сколько будет 7 × 8?", ["54", "56", "64", "48"], 1),
        ("Сколько градусов в прямом угле?", ["45", "90", "180", "360"], 1),
        ("Чему равен квадрат числа 9?", ["18", "72", "81", "99"], 2),
        ("Сколько будет 100 ÷ 4?", ["20", "25", "40", "50"], 1),
        ("Какое число простое?", ["9", "15", "17", "21"], 2),
        ("Периметр квадрата со стороной 5 см?", ["10 см", "15 см", "20 см", "25 см"], 2),
        ("Сколько будет 12 + 19?", ["29", "30", "31", "32"], 2),
        ("Сколько минут в 2 часах?", ["60", "90", "120", "180"], 2),
        ("Половина от 50?", ["20", "25", "30", "35"], 1),
        ("Сколько будет 3³?", ["9", "18", "27", "36"], 2),
    ]),
    "history": ("📚 История", [
        ("В каком году закончилась Вторая мировая война?", ["1941", "1943", "1945", "1950"], 2),
        ("Как назывался древний торговый путь между Востоком и Западом?", ["Янтарный", "Шёлковый", "Соляной", "Северный"], 1),
        ("В какой стране находятся пирамиды Гизы?", ["Греция", "Египет", "Италия", "Индия"], 1),
        ("Кто был первым человеком в космосе?", ["Нил Армстронг", "Юрий Гагарин", "Алексей Леонов", "Герман Титов"], 1),
        ("В каком году Таджикистан провозгласил независимость?", ["1990", "1991", "1992", "1995"], 1),
        ("Какой город Центральной Азии был известным центром науки?", ["Самарканд", "Лондон", "Париж", "Рим"], 0),
        ("Кто написал «Илиаду»?", ["Гомер", "Платон", "Сократ", "Геродот"], 0),
        ("Как называется эпоха возрождения искусства и науки в Европе?", ["Античность", "Ренессанс", "Средневековье", "Индустриализация"], 1),
        ("В каком году началась Первая мировая война?", ["1905", "1914", "1918", "1939"], 1),
        ("Какой древний народ построил Персеполь?", ["Римляне", "Персы", "Викинги", "Майя"], 1),
    ]),
}

def connect_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS scores(
        user_id INTEGER PRIMARY KEY, name TEXT NOT NULL,
        points INTEGER NOT NULL DEFAULT 0, games INTEGER NOT NULL DEFAULT 0)""")
    con.commit()
    return con

def save_score(user, score):
    with connect_db() as con:
        con.execute("""
            INSERT INTO scores(user_id,name,points,games) VALUES(?,?,?,1)
            ON CONFLICT(user_id) DO UPDATE SET
            name=excluded.name, points=points+excluded.points, games=games+1
        """, (user.id, user.full_name, score))

def menu():
    buttons = [[InlineKeyboardButton(title, callback_data=f"category:{key}")]
               for key, (title, _) in QUIZZES.items()]
    buttons.append([InlineKeyboardButton("🏆 Рейтинг", callback_data="top")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("game", None)
    await update.message.reply_text(
        "👋 Добро пожаловать в QUIZ BOT!\n\n"
        "Выбирай тему. В каждой викторине 10 вопросов. "
        "За каждый правильный ответ — 1 балл.",
        reply_markup=menu()
    )

async def show_question(query, context):
    game = context.user_data["game"]
    title, questions = QUIZZES[game["category"]]
    question, options, _ = questions[game["index"]]
    keyboard = [[InlineKeyboardButton(f"{i+1}. {opt}", callback_data=f"answer:{i}")]
                for i, opt in enumerate(options)]
    keyboard.append([InlineKeyboardButton("✖ Завершить", callback_data="quit")])
    await query.edit_message_text(
        f"{title}\nВопрос {game['index']+1}/{len(questions)}\n\n{question}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def top_text():
    with connect_db() as con:
        rows = con.execute("SELECT name,points,games FROM scores ORDER BY points DESC,games ASC LIMIT 10").fetchall()
    if not rows:
        return "🏆 Рейтинг пока пуст. Сыграй первым!"
    return "🏆 ТОП-10 ИГРОКОВ\n\n" + "\n".join(
        f"{i}. {name} — {points} баллов · игр: {games}"
        for i, (name, points, games) in enumerate(rows, 1)
    )

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "top":
        await q.edit_message_text(await top_text(), reply_markup=menu())
        return
    if data.startswith("category:"):
        key = data.split(":", 1)[1]
        context.user_data["game"] = {"category": key, "index": 0, "score": 0}
        await show_question(q, context)
        return
    if data == "quit":
        context.user_data.pop("game", None)
        await q.edit_message_text("Игра завершена. Напиши /start, чтобы начать снова.")
        return
    if data.startswith("answer:"):
        game = context.user_data.get("game")
        if not game:
            await q.edit_message_text("Игра не найдена. Напиши /start.")
            return
        _, questions = QUIZZES[game["category"]]
        _, options, correct = questions[game["index"]]
        chosen = int(data.split(":")[1])
        if chosen == correct:
            game["score"] += 1
            feedback = "✅ Правильно!"
        else:
            feedback = f"❌ Неверно. Правильный ответ: {options[correct]}"

        game["index"] += 1
        if game["index"] == len(questions):
            score = game["score"]
            save_score(q.from_user, score)
            context.user_data.pop("game", None)
            await q.edit_message_text(
                f"{feedback}\n\n🎉 Викторина завершена!\n"
                f"Твой результат: {score}/{len(questions)}\n\n"
                "Напиши /start, чтобы сыграть ещё раз."
            )
        else:
            await q.edit_message_text(feedback)
            await show_question(q, context)

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(await top_text(), reply_markup=menu())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start — начать игру\n/top — рейтинг игроков\n/help — помощь")

def main():
    if not TOKEN:
        raise RuntimeError("Не задан BOT_TOKEN в переменных окружения.")
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.run_polling()

if __name__ == "__main__":
    main()
