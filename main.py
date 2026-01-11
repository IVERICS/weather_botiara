import asyncio
import logging
import sys
import requests
from os import getenv

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from database.database import Database
from models.user import User
from utils.notifications import check_notification
from utils.weather import Weather
from keyboards.main_kb import (
    get_main_keyboard,
    get_notifications_keyboard,
    get_time_selection_keyboard,
    get_confirmation_keyboard
)


load_dotenv()


# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv('BOT_TOKEN')
KEY = getenv('WEATHER_KEY')

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()



@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f'Привет, {html.bold(message.from_user.full_name)}!\n\n'
        f'Я бот погоды! Вот что я умею:\n'
        f'Покажу погоду если дашь локацию\n'
        f'Пришлю сообщение о погоде на время которое ты укажешь\n'
        f'Для дай свою локацию\n',
        reply_markup=get_main_keyboard()
    )


@dp.message(F.text == "Погода сейчас")
async def current_weather_handler(message: Message) -> None:
    user = User.get_users_with_notification(user_id=message.from_user.id)
    if not user or not user[0].lat:
        await message.answer(
            'Сначала дай локацию чтобы я мог показать тебе ппогоду',
            reply_markup=get_main_keyboard()
        )
        return
    user = user[0]
    await send_weather_message(message, user.lon, user.lat)


@dp.message(F.text == "Мои уведомления")
async def notifications_handler(message: Message) -> None:
    await message.answer(
        'Управление уведомлениями:\n\n'
        'Здесь вы можете настроить автоматические уведомления о погоде',
        reply_markup=get_notifications_keyboard()
    )


@dp.message(F.text == 'Помощь')
async def help_handler(message: Message) -> None:
    await message.answer(
        'Справка по боту:\n\n'
        '<b>Отправить локацию</b> - Поделиться своим местоположением\n'
        '<b>Погода сейчас</b> - Получить текущую погоду\n'
        '<b>Мои уведомления</b> - Управление уведомлениями\n'
        '<b>Команды</b>\n'
        '/start - Начать работу\n'
        '/weather - Получить погоду\n'
        '/notification - Установить уведомления\n'
        '/help - Показать эту справку\n',
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_keyboard()
    )


@dp.message(F.location)
async def location_handler(message: Message) -> None:
    user = User.get_by_telegram_id(user_id=message.from_user.id)
    if not user:
        user = User(
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            lat=message.location.latitude,
            lon=message.location.longitude
        )
    if user.safe_to_db():
        await message.answer(
            text='Локация сохранена! Теперь вы можете получать погоду и настраивать уведомления',
            reply_markup=get_main_keyboard()
        )
        await send_weather_message(message, user.lat, user.lon)
    else:
        await message.answer('❌ Ошибка сохранения локации')


@dp.callback_query(F.data == 'add_notification')
async def add_notification_handler(callback: CallbackQuery):
    users = User.get_users_with_notification(user_id=callback.from_user.id)
    if not users or not users[0].lat:
        await callback.message.edit_text(
            'Сначала отправте свою лолкацию чтобы настроить уведомления',
            reply_markup=get_notifications_keyboard()
        )
        return None
    await callback.message.edit_text(
        'Выберете время для уведомления'
        'Я буду присылать погоду каждый день в выбранное время',
        reply_markup=get_time_selection_keyboard()
    )


@dp.callback_query(F.data.startwith('set_time_'))
async def set_time_handler(callback: CallbackQuery):
    time_str = callback.data.replace('set_time_', '')
    users = User.get_users_with_notification(user_id=callback.from_user.id)
    if users:
        user = users[0]
        from datetime import datetime
        try:
            hours, minutes = map(int, time_str.split(':'))
            notification_time = datetime.now().replace(
                hours=hours,
                minutes=minutes,
                seconds=0,
                microsecond=0
            )
            if user.set_notification(notification_time=notification_time):
                await callback.message.edit_text(
                    f'Уведомление настроено на {time_str}\n'
                    f'Каждый день в это время я буду присылать вам погоду',
                    reply_markup=get_notifications_keyboard()
                )
            else:
                await callback.message.edit_text(
                    '❌ Ошибка установки уведомления',
                    reply_markup=get_notifications_keyboard()
                )
        except ValueError:
            await callback.message.edit_text(
                '❌ Неверный формат времени',
                reply_markup=get_notifications_keyboard()
            )


@dp.callback_query(F.data == 'show_notifications')
async def show_notifications_handler(callback: CallbackQuery):
    '''Показать текущие уведомления'''
    users = User.get_users_with_notification(user_id=callback.from_user.id)
    if users and users[0].notification_time:
        user = users[0]
        time_str = user.notification_time.strftime('%H:%M')
        await callback.message.edit_text(
            f'Ваше текущее уведомление:\n\n'
            f'Время: {time_str}\n'
            f'Локация: {user.lat: .4f}, {user.lon: .4f}',
            reply_markup=get_notifications_keyboard()
        )
    else:
        await callback.message.edit_text(
            '❌ У вас нет установленных уведомлений',
            reply_markup=get_notifications_keyboard()
        )


@dp.callback_query(F.data == 'delete_all_notifications')
async def delete_notifications_handler(callback: CallbackQuery):
    '''Удалить все уведомления'''
    await callback.message.edit_text(
        '⚠️ Вы уверены, что хотите удалить все уведомления?',
        reply_markup=get_confirmation_keyboard()
    )


@dp.callback_query(F.data == 'confirm_delete')
async def confirm_delete_handler(callback: CallbackQuery):
    '''Подтверждение удаления уведомлений'''
    users = User.get_users_with_notification(user_id=callback.from_user.id)
    if users:
        user = users[0]
        user.notification_time = None
        if user.set_notification():
            await callback.message.edit_text(
                'Все уведомления удалены',
                reply_markup=get_notifications_keyboard()
            )
        else:
            await callback.message.edit_text(
                'Ошибка удаления уведомлений',
                reply_markup=get_notifications_keyboard()
            )


@dp.callback_query(F.data == 'cancel_delete')
async def cancel_delete_handler(callback: CallbackQuery):
    '''Отмена удаления уведомлений'''
    await callback.message.edit_text(
        'Управление уведомлениями',
        reply_markup=get_notifications_keyboard()
    )


@dp.callback_query(F.data == 'back_to_notifications')
async def back_to_notifications_handler(callback: CallbackQuery):
    '''Назад к управлению уведомлениями'''
    await callback.message.edit_text(
        'Управление уведомлениями',
        reply_markup=get_notifications_keyboard()
    )


@dp.callback_query(F.data == 'back_to_main')
async def back_to_main_handler(callback: CallbackQuery):
    '''Назад к главному меню'''
    await callback.message.edit_text(
        'Главное меню:',
        reply_markup=get_main_keyboard()
    )


@dp.message(Command('notification'))
async def notification_command_handler(message: Message):
    '''Команда для управления уведомлениями'''
    await notifications_handler(message)


@dp.message(Command('weather'))
async def weather_command_handler(message: Message):
    '''Команда для получения погоды'''
    await current_weather_handler(message)


@dp.message(Command('help'))
async def help_command_handler(message: Message):
    '''Команда помощи'''
    await help_handler(message)


async def send_weather_message(message: Message, lat: float, lon: float):
    '''Отправка сообщения с погодой'''
    try:
        weather = Weather(lat, lon)
        await weather.get_weather()
        message_text = (
            f'{weather.emoji} <b>Погода сейчас:</b>\n\n'
            f'<b>Местоположение:</b>{weather.location}\n'
            f'<b>Температура:</b>{weather.temp}°C\n'
            f'<b>Ветер:</b>{weather.wind_speed} м/с, {weather.wind_direction}\n'
            f'<b>Описание:</b>{weather.description}\n'
            f'<b>Влажность:</b>{weather.humidity}%\n'
            f'<b>Давление:</b>{weather.pressure:.1f} мм рт. ст.'
        )
        await message.answer(message_text, parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f'❌ Ошибка получения погоды : {e}')
        await message.answer('❌ Ошибка получения данных о погоде')


@dp.message()
async def echo_handler(message: Message):
    '''Обработка остальных сообщений'''
    await message.answer(
        'Используйте кнопки ниже или команды для взаимодействия с ботом',
        reply_markup=get_main_keyboard()
    )


async def scheduled_notifications(bot):
    '''Фоновая задача для проверки уведомдений'''
    while True:
        try:
            await check_notification(bot)
        except Exception as e:
            print(f'❌ Ошибка в фоновой задаче: {e}')
        await asyncio.sleep(60)


async def main() -> None:
    db = Database()
    db.create_tables()

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.delete_webhook()

    asyncio.create_task(scheduled_notifications(bot))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())