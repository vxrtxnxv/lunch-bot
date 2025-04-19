import json
import random
import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext

TOKEN = os.getenv("TOKEN")

DATA_FILE = "dishes.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"all": [], "used": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_next_dish(data):
    available = list(set(data["all"]) - set(data["used"]))
    if not available:
        data["used"] = []
        available = data["all"][:]
    dish = random.choice(available)
    data["used"].append(dish)
    save_data(data)
    return dish

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Что приготовить сегодня"], ["Добавить блюдо"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    await update.message.reply_text("🍽 Что сегодня на обед?", reply_markup=markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    data = load_data()

    if user_input == "Что приготовить сегодня":
        if not data["all"]:
            await update.message.reply_text("Список блюд пуст. Сначала добавь что-нибудь.")
            return
        dish = get_next_dish(data)
        await update.message.reply_text(f"Сегодняшнее предложение:\n**{dish}**", parse_mode="Markdown")
    elif user_input == "Добавить блюдо":
        await update.message.reply_text("Напиши название блюда, которое хочешь добавить:")
        context.user_data["adding"] = True
    elif context.user_data.get("adding"):
        context.user_data["adding"] = False
        new_dish = user_input.strip()
        if new_dish and new_dish not in data["all"]:
            data["all"].append(new_dish)
            save_data(data)
            await update.message.reply_text(f"✅ Добавлено: {new_dish}")
        else:
            await update.message.reply_text("Такое блюдо уже есть или пустое название.")
    else:
        await update.message.reply_text("Нажми на кнопку или используй команды.")

def main():
    data = load_data()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
