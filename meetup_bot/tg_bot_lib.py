from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from email_validate import validate

def get_menu_keyboard(is_speaker):
    keyboard = [
        [InlineKeyboardButton('📋  Программа мероприятия', callback_data='program')],
        [InlineKeyboardButton('🗣  Задать вопрос спикеру', callback_data='ask_speaker')],
        [InlineKeyboardButton('🤝  Познакомиться', callback_data='acquaint')],
        [InlineKeyboardButton('💸  Донат', callback_data='donate')],
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


def check_email(update, context):
    is_valid_email = validate(
        update.message.text,
        check_blacklist=False,
        check_dns=False,
        check_smtp=False
    )
    if not is_valid_email:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Не могу распознать введённый email. Попробуйте ещё раз',
        )
    return is_valid_email