from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio
import os

# Берем токен из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN не встановлено в змінних середовища. Додай його на Railway як BOT_TOKEN.")

# Шаблоны опросов
TEMPLATES = {
    "alco": {
        "question": "Алкоголь. Я буду (можна обрати декілька варіантів):",
        "options": [
            "Вино біле",
            "Вино червоне",
            "Сидр",
            "Пиво",
            "Джин",
            "Віскі",
            "Пиво б/а",
            "Вино б/а",
            "Нічого з вище переліченого"
        ]
    },
    "food": {
        "question": "Що ти будеш їсти?",
        "options": [
            "М’ясо",
            "Суші",
            "Закуски",
            "Щось вегетаріанське"
        ]
    }
}



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Привіт! Я бот для створення опитувань.\n\n"
        "Як можна працювати зі мною:\n"
        "1) Надішли текст у форматі:\n"
        "   Питання\n"
        "   Варіант 1\n"
        "   Варіант 2\n"
        "   ...\n\n"
        "2) Використовуй шаблони:\n"
        "   /alco – опитування по алкоголю\n"
        "   /food – опитування по їжі\n\n"
        "Я створю опитування і надішлю тобі. Далі ти пересилаєш його в потрібний чат."
    )
    await update.message.reply_text(text)


async def send_template_poll(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str):
    template = TEMPLATES.get(key)
    if not template:
        await update.message.reply_text("Шаблон не знайдено.")
        return

    question = template["question"]
    options = template["options"]

    if not (2 <= len(options) <= 10):
        await update.message.reply_text(
            f"У шаблоні {len(options)} варіант(ів), а Телеграм дозволяє від 2 до 10."
        )
        return

    await context.bot.send_poll(
        chat_id=update.message.chat_id,
        question=question,
        options=options,
        is_anonymous=False,
        allows_multiple_answers=True
    )

    await update.message.reply_text(
        "Готово ✅\nОпрос створено за шаблоном. Перешли його в потрібний чат."
    )


async def alco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_template_poll(update, context, "alco")


async def food(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_template_poll(update, context, "food")


async def handle_poll_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text:
        return

    if text.startswith("/"):
        return

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if len(lines) < 3:
        await update.message.reply_text(
            "Потрібно мінімум 1 питання + 2 варіанти відповіді.\n"
            "Формат:\n"
            "Питання\nВаріант 1\nВаріант 2\n..."
        )
        return

    question = lines[0]
    options = lines[1:]

    if not (2 <= len(options) <= 10):
        await update.message.reply_text(
            f"Зараз {len(options)} варіант(ів).\n"
            "Телеграм дозволяє від 2 до 10 варіантів відповіді."
        )
        return

    await context.bot.send_poll(
        chat_id=update.message.chat_id,
        question=question,
        options=options,
        is_anonymous=False,
        allows_multiple_answers=True
    )

    await update.message.reply_text(
        "Готово ✅\nОпрос створено з тексту. Перешли його в потрібний чат."
    )


if __name__ == "__main__":
    # Для новых версий Python явно создаем event loop
    asyncio.set_event_loop(asyncio.new_event_loop())

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("alco", alco))
    app.add_handler(CommandHandler("food", food))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_poll_text))

    print("Бот запущен. Натисни Ctrl+C для зупинки.")
    app.run_polling()
