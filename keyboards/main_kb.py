from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Отправить локацию', request_location=True)],
            [KeyboardButton(text='Мои уведомления'), KeyboardButton(text='Погода сейчас')],
            [KeyboardButton(text='Помощь')]
        ],
        resize_keyboard=True,
        input_field_placeholder='Выберите действие...'
    )


def get_notifications_keyboard():
    '''Клавиатура управления уведомлениями'''
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Добавить уведомление',  callback_data='add_notification')],
            [InlineKeyboardButton(text='Показать уведомления',  callback_data='show_notifications')],
            [InlineKeyboardButton(text='Удалить все уведомления',  callback_data='delete_all_notifications')],
            [InlineKeyboardButton(text='Назад',  callback_data='back_to_main')],
        ]
    )


def get_time_selection_keyboard():
    times = [
        ['07:00', '08:00', '09:00'],
        ['10:00', '12:00', '15:00'],
        ['18:00', '20:00', '22:00'],
        ['Назад']
    ]
    keyboard = []
    for row in times:
        keyboard_row = []
        for time in row:
            if time == 'Назад':
                keyboard_row.append(InlineKeyboardButton(text=time, callback_data='back_to_notifications'))
            else:
                keyboard_row.append(InlineKeyboardButton(text=time, callback_data=f'set_time_{time}'))
        keyboard.append(keyboard_row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirmation_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Да', callback_data='confirm_delete')],
            [InlineKeyboardButton(text='Нет', callback_data='cancel_delete')]
        ]
    )
