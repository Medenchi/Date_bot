import os
import random
import requests
from datetime import datetime
from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message, Update

API_TOKEN = "7967235756:AAE4_T3cqfpBiddBzSlLvq0UCGjlPr7Oc_M"
ADMIN_ID = 6613852308

# Источники праздников
CHECKIDAY_API_URL = "https://checkiday.com/api/v1/dates/"
CALENDAR_API_URL = "https://date.nager.at/api/v2/PublicHolidays/{year}/RU"

# Республиканские праздники Башкортостана
BASHKORTOSTAN_HOLIDAYS = {
    "01-21": "День родного языка башкир",
    "06-24": "Праздник Сабантуй",
    "05-09": "День Победы",
    "04-15": "Ҡыуылт Январ (Ураза-байрам)",
    "05-23": "День Республики Башкортостан"
}

# Команды /sorry и /comfort
SORRIES = [
    "Прости меня, это была моя ошибка.",
    "Мне очень жаль, что так получилось.",
    "Прошу прощения за доставленные неудобства.",
    "Не хотел тебя обидеть, прости.",
    "Сожалею, что не оправдал твои ожидания.",
    "Извини, я должен был поступить иначе.",
    "Пожалуйста, прости меня за глупость.",
    "Я понимаю, что натворил, извиняйся.",
    "Мне стыдно, что так вышло. Прости.",
    "Я не хотел(а) этого, честно.",
    "Извини, мне нужно было подумать перед тем, как говорить.",
    "Это моя вина. Прими мои извинения.",
    "Я знаю, что подвел(а) тебя. Извини.",
    "Пожалуйста, дай мне шанс всё исправить.",
    "Мое поведение было недопустимым. Прости."
]

COMFORTS = [
    "Всё будет хорошо.",
    "Ты справишься, я в тебя верю.",
    "Не переживай, всё наладится.",
    "Это лишь временные трудности.",
    "Ты сделал(а) всё, что мог(ла).",
    "Не переживай, ты сильнее, чем ты думаешь.",
    "Всё когда-нибудь наладится.",
    "Ты не один(а), я рядом.",
    "Не принимай это близко к сердцу.",
    "Ты достоин(а) лучшего.",
    "Все будет хорошо, просто дай себе время.",
    "Ты молодец, что не сдаешься.",
    "Любая ситуация изменится — даже эта.",
    "Ты хороший человек. Не сомневайся в себе.",
    "Всё пройдет, и ты станешь сильнее."
]

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

app = FastAPI()

def get_all_holidays(date_str):
    try:
        response = requests.get(f"{CHECKIDAY_API_URL}{date_str}", timeout=10)
        if response.status_code == 200:
            return [item['name'] for item in response.json().get("holidays", [])]
        else:
            return []
    except Exception as e:
        return []

def get_russian_holidays(year):
    try:
        response = requests.get(CALENDAR_API_URL.format(year=year), timeout=10)
        if response.status_code == 200:
            return [f"{item['name']} ({item['date']})" for item in response.json()]
        else:
            return []
    except Exception as e:
        return []

def get_bashkortostan_holidays(month_day):
    return [BASHKORTOSTAN_HOLIDAYS[day] for day in BASHKORTOSTAN_HOLIDAYS if day == month_day]

def generate_message(world_holidays, ru_holidays, local_holidays):
    today = datetime.now().strftime("%d %B %Y")
    message = f"📅 Все праздники мира на {today}:\n\n"

    if world_holidays:
        message += "🌐 Абсолютно все найденные праздники:\n"
        for h in world_holidays:
            message += f"- {h}\n"
        message += "\n"
    else:
        message += "❌ Сегодня нет международных праздников.\n\n"

    if ru_holidays:
        message += "🇷🇺 Государственные праздники России:\n"
        for h in ru_holidays:
            message += f"- {h}\n"
        message += "\n"
    else:
        message += "🇷🇺 В России сегодня нет праздников.\n\n"

    if local_holidays:
        message += "🇧🇾 Республиканские праздники Башкортостана:\n"
        for h in local_holidays:
            message += f"- {h}\n"
    else:
        message += "🇧🇾 В Башкортостане сегодня нет особых праздников."

    return message

async def send_holidays(chat_id):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    month_day = now.strftime("%m-%d")
    year = now.year

    world = get_all_holidays(date_str)
    russia = get_russian_holidays(year)
    bashkir = get_bashkortostan_holidays(month_day)

    message = generate_message(world, russia, bashkir)
    await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)

@dp.message(lambda message: message.text == "/start")
async def cmd_start(message: Message):
    await send_holidays(message.from_user.id)

@dp.message(lambda message: message.text == "/sorry")
async def cmd_sorry(message: Message):
    await message.answer(random.choice(SORRIES))

@dp.message(lambda message: message.text in ["/comfort", "/pg"])
async def cmd_comfort(message: Message):
    await message.answer(random.choice(COMFORTS))

@app.get("/send-holidays")
async def trigger_send():
    await send_holidays(ADMIN_ID)
    return {"status": "ok"}

@app.post("/")
async def webhook(update: dict):
    await dp._process_update(bot, Update(**update))

@app.on_event("startup")
async def on_startup():
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/"
    await bot.set_webhook(webhook_url)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot:app", host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
