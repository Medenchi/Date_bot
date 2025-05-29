import os
import asyncio
from datetime import datetime
from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
import requests

API_TOKEN = "7967235756:AAGBflfRWJNZzJ_hD1bArkOB-LxcgNA17dY"
ADMIN_ID = 6613852308

CHECKIDAY_API_URL = "https://checkiday.com/api/v1/dates/"

BASHKORTOSTAN_HOLIDAYS = {
    "01-21": "День родного языка башкир",
    "06-24": "Праздник Сабантуй",
    "05-09": "День Победы (в том числе отмечают в Башкортостане)",
    "04-15": "Ҡыуылт Январ (Ураза-байрам)",
    "05-23": "День Республики Башкортостан"
}

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
app = FastAPI()

def get_all_holidays(date_str):
    try:
        response = requests.get(f"{CHECKIDAY_API_URL}{date_str}")
        return [item['n'] for item in response.json()['holidays']]
    except Exception as e:
        return []

def get_bashkortostan_holidays(month_day):
    return [BASHKORTOSTAN_HOLIDAYS[day] for day in BASHKORTOSTAN_HOLIDAYS if day == month_day]

def generate_message(all_holidays, local_holidays):
    today = datetime.now().strftime("%d %B %Y")
    message = f"📅 Все праздники мира на {today}:\n\n"

    if all_holidays:
        message += "🌐 Абсолютно все найденные праздники:\n"
        for h in all_holidays:
            message += f"- {h}\n"
        message += "\n"

    if local_holidays:
        message += "🇧🇾 Республиканские праздники Башкортостана:\n"
        for h in local_holidays:
            message += f"- {h}\n"
    else:
        message += "🇧🇾 В Башкортостане сегодня нет особых праздников.\n"

    return message

async def send_holidays():
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    month_day = now.strftime("%m-%d")

    all_holidays = get_all_holidays(date_str)
    local_holidays = get_bashkortostan_holidays(month_day)

    message = generate_message(all_holidays, local_holidays)

    await bot.send_message(chat_id=ADMIN_ID, text=message, parse_mode=ParseMode.MARKDOWN)

@app.get("/send-holidays")
async def trigger_send():
    await send_holidays()
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot:app", host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
