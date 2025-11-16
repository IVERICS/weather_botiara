from weather import Weather
from datetime import datetime
from aiogram import Bot
from models.user import User


async def check_notification(bot: Bot):
    '''
    Проверка и отправка уведомлений
    '''
    try:
        users_with_notification = User.get_users_with_notification()
        for user in users_with_notification:
            try:
                if not user.notification_time:
                    continue
                if datetime.now() >= user.notification_time:
                    await send_notification(bot, user)
            except Exception as e:
                print(f'❌ Ошибка обработки уведомления для пользователя {user.id}: {e}')
    except Exception as e:
        print(f'❌ Ошибка проверки уведомлений: {e}')


async def send_notification(bot, user):
    '''Отправка уведомления пользовавтелю'''
    try:
        weather = Weather(user.lat, user.lon)
        await weather.get_weather()
        message_text = (
            f"🧭Ваше местоположение: {weather.location}\n"
            f"🌡Температура за бортом: {weather.temp}C°\n"
            f"💨Скорость ветра: {weather.wind_speed}м/c\n"
            f"🪁Направление ветра: {weather.wind_direction})\n"
            f"📎Описание: {weather.description}\n"
            f"💧Влажность: {weather.humidity}%\n"
            f"💉Давление: {weather.pressure}мм рт.ст."
        )
        await bot.send_message(chat_id=user.telegram_id, text=weather.emoji)
        await bot.send_message(chat_id=user.telegram_id, text=message_text)
    except Exception as e:
        print(f'❌ Ошибка отправки уведомления: {e}')
