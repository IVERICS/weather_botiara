import asyncio
import logging
import sys
import requests
from os import getenv

from aiogram import Bot, Dispatcher, html, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


# Bot token can be obtained via https://t.me/BotFather
TOKEN = "7322887237:AAG5we_XpSZSz3Kw0jxhbF7yHKEV7Dh3iWM"

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()
location_button = KeyboardButton(text="Отправить локацию", request_location=True)
keyboard = ReplyKeyboardMarkup(
    keyboard=[[location_button]]
)
button_callback = InlineKeyboardButton(text="Нажми меня пж", callback_data="privet pypsik")
inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_callback]])


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(F.text.lower() == "hello")
async def hello_handler(message: Message) -> None:
    await message.answer("NU zDaRoVo")


@dp.message(F.text.lower() == "какая погода")
async def weather_handler(message: Message) -> None:
    await message.answer("poka ne znaйу")


@dp.message(F.location)
async def weather_handler(message: Message) -> None:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": message.location.latitude,
        "lon": message.location.longitude,
        "appid": "f9e52698bc0786930a5a7fc385762ba5",
        "lang": "ru",
        "units": "metric"
    }
    response = requests.get(url, params=params)
    weather = response.json()
    await message.answer(f"Ваше местоположение: {weather.get('name')}, {weather.get('sys').get('country')}\n"
                         f"Температура за бортом: {weather.get('main').get('temp')}C°\n"
                         f"Скорость ветра: {weather.get('wind').get('speed')}м/c\n"
                         f"Направление ветра: {response.json().get('wind').get('deg')}°\n"
                         f"{weather.get('weather')[0].get('description').capitalize()}")


@dp.message(Command("markup"))
async def get_markup(message:Message) -> None:
    await message.answer(reply_markup=inline_keyboard, text="Ds,thnb aeyrwb.")


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())