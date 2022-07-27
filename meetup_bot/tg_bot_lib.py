from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_menu_keyboard(is_speaker):
    keyboard = [
        [InlineKeyboardButton('Программа', callback_data='program')],
        [InlineKeyboardButton('Задонатить', callback_data='donate')],
        [InlineKeyboardButton('Задать вопрос спикеру', callback_data='ask_speaker')],
        [InlineKeyboardButton('Познакомиться', callback_data='acquaint')],
    ]
    if is_speaker:
        keyboard.append(
            [InlineKeyboardButton('Ответить на вопросы', callback_data='respond_to_questions')],
        )
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_accept_questionnarie_keyboard():
    keyboard = [
        [InlineKeyboardButton('Подтвердить', callback_data='accept')],
        [InlineKeyboardButton('Назад в меню', callback_data='back_to_menu')],  
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup