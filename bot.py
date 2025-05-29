import asyncio
import requests
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode

API_TOKEN = "7967235756:AAGBflfRWJNZzJ_hD1bArkOB-LxcgNA17dY"
ADMIN_ID = 6613852308  # Твой Telegram ID для получения сообщений

# Источник всех возможных праздников
CHECKIDAY_API_URL = "https://checkiday.com/api/v1/dates/"

# Дополнительно: праздники России и Башкортостана (можно расширять под другие республики)
RU_HOLIDAYS_API = "https://date.nager.at/api/v2/PublicHolidays/{year}/RU"

def get_all_holidays(date_str):
    try:
        response = requests.get(f"{CHECKIDAY_API_URL}{date_str}")
        return [item['n'] for item in response.json()['holidays']]
    except Exception as e:
        return []

def get_russian_holidays(year):
    try:
        response = requests.get(f"{RU_HOLIDAYS_API.format(year=year)}")
        return [f"{item['name']} ({item['date']})" for item in response.json()]
    except Exception as e:
        return []

def get_bashkortostan_holidays(month_day):
    BASHKORTOSTAN_HOLIDAYS = {
        "01-21": "День родного языка башкир",
        "06-24": "Праздник Сабантуй",
        "04-15": "Ҡыуылт Январ (Ураза-байрам)",
        "05-23": "День Республики Башкортостан"
    }
    return [BASHKORTOSTAN_HOLIDAYS[day] for day in BASHKORTOSTAN_HOLIDAYS if day == month_day]

def generate_message(all_holidays, ru_holidays, local_holidays):
    today = datetime.now().strftime("%d %B %Y")
    message = f"📅 Все праздники мира на {today}:\n\n"

    if all_holidays:
        message += "🌐 Абсолютно все найденные праздники:\n"
        for h in all_holidays:
            message += f"- {h}\n"
        message += "\n"

    if ru_holidays:
        message += "🇷🇺 Государственные праздники России:\n"
        for h in ru_holidays:
            message += f"- {h}\n"
        message += "\n"

    if local_holidays:
        message += "🇧🇾 Республиканские праздники Башкортостана:\n"
        for h in local_holidays:
            message += f"- {h}\n"
    else:
        message += "🇧🇾 В Башкортостане сегодня нет особых праздников.\n"

    return message

async def send_holidays(bot):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    month_day = now.strftime("%m-%d")

    all_holidays = get_all_holidays(date_str)
    ru_holidays = get_russian_holidays(now.year)
    local_holidays = get_bashkortostan_holidays(month_day)

    message = generate_message(all_holidays, ru_holidays, local_holidays)

    await bot.send_message(chat_id=ADMIN_ID, text=message, parse_mode=ParseMode.MARKDOWN)

async def main():
    bot = Bot(token=API_TOKEN)
    try:
        await send_holidays(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
