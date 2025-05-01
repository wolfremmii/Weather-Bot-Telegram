import logging
import requests
import asyncio
import nest_asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

nest_asyncio.apply()

logging.basicConfig(level=logging.INFO)

# Enter your token(Use BotFather and OpenWeatherMap API) / Введите сюда свой токен бота и API c сайта OpenWeatherMap
BOT_TOKEN = 'Your Token'
OWM_API_KEY = 'Your API'

user_lang = {}

# Getting weather info / Получаем информацию о погоде с сайта
def get_weather(city: str, lang: str) -> str:
    city = city.strip().title()  # Remove spaces and capitalize letters / Удаляем лишние пробелы и делаем заглавные буквы
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric&lang={lang}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            name = data['name']
            temp = data['main']['temp']
            weather = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind = data['wind']['speed']

            if lang == "ru":
                return (f"🌍 Город: {name}\n"
                        f"🌡 Температура: {temp}°C\n"
                        f"🌤 Погода: {weather}\n"
                        f"💧 Влажность: {humidity}%\n"
                        f"💨 Ветер: {wind} м/с")
            else:
                return (f"🌍 City: {name}\n"
                        f"🌡 Temperature: {temp}°C\n"
                        f"🌤 Weather: {weather}\n"
                        f"💧 Humidity: {humidity}%\n"
                        f"💨 Wind speed: {wind} m/s")
        elif response.status_code == 404:
            return "❌ Город не найден." if lang == "ru" else "❌ City not found."
        else:
            return "⚠️ Ошибка при получении погоды." if lang == "ru" else "⚠️ Error retrieving weather."
    except Exception as e:
        return f"⚠️ Произошла ошибка: {str(e)}" if lang == "ru" else f"⚠️ An error occurred: {str(e)}"


# Language choice upon /start command
# Делаем выбор языка при команде /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Русский 🇷🇺", "English 🇬🇧"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "Выберите язык / Choose your language:",
        reply_markup=markup
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.lower()

    # Choose language / Выбор языка
    if "рус" in text:
        user_lang[user_id] = "ru"
        await update.message.reply_text("Язык установлен: русский 🇷🇺\nВведите город для получения погоды.")
    elif "engl" in text:
        user_lang[user_id] = "en"
        await update.message.reply_text("Language set: English 🇬🇧\nType a city name to get weather.")
    else:
        # Weather Request / Запрос погоды
        lang = user_lang.get(user_id, "ru")  # По умолчанию русский
        city = update.message.text
        result = get_weather(city, lang)
        await update.message.reply_text(result)

# Main function on startup / Главная функция запуска
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ Бот запущен.")
    await app.run_polling()

# Run code / Запуск кода
if __name__ == '__main__':
    asyncio.run(main())
