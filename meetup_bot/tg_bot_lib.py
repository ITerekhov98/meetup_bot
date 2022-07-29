from datetime import datetime
from django.utils import timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from email_validate import validate

from .models import Block, Lecture


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


def get_acquaintance_keyboard():
    keyboard = [
        [InlineKeyboardButton('Да', callback_data='accept')],
        [InlineKeyboardButton('Внести изменения в анкету', callback_data='update_questionnaire')],
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

def get_blocks_keyboard():
    blocks = Block.objects.filter(end__gte=timezone.now())
    keyboard = [
        [InlineKeyboardButton(block.title, callback_data=f'block {block.pk}')] for block in blocks
    ]
    keyboard.append(
        [InlineKeyboardButton('Назад в меню', callback_data='back_to_menu')]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

def get_lectures_keyboard(block_pk):
    lectures = Lecture.objects.filter(block__pk=block_pk).filter(end__gte=timezone.now())
    keyboard = []
    for lecture in lectures:
        if lecture.title != 'Обед':
            keyboard.append(
                [InlineKeyboardButton(lecture.title, callback_data=f'lecture {lecture.pk}')]
            )
    keyboard.append(
        [InlineKeyboardButton('Назад в меню', callback_data='back_to_menu')]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

def back_to_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton('Назад в меню', callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

def get_next_question():
    keyboard = [
        [InlineKeyboardButton('Ответить в чат', callback_data='reply')],
        [InlineKeyboardButton('Следующий вопрос', callback_data='next')],
        [InlineKeyboardButton('Предыдущий вопрос', callback_data='previous')],
        [InlineKeyboardButton('Назад в меню', callback_data='back_to_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

def get_speakers_keyboard(lecture_pk):
    lecture = Lecture.objects.get(pk=lecture_pk)
    speakers = lecture.speakers.all()
    keyboard = [
        [InlineKeyboardButton(
            speaker.first_name,
            callback_data=f'speaker {speaker.pk}'
        )
        for speaker in speakers]]
    keyboard.append(
        [InlineKeyboardButton('Назад в меню', callback_data='back_to_menu')]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

def get_text_notification(user):
    incoming_questions_count = user.incoming_questions.count()
    if incoming_questions_count == 0:
        text = 'Вам поступил вопрос по докладу! Не забудьте ответить'
    elif incoming_questions_count == 2:
        text = 'Для вас уже есть 3 вопроса!'
    elif incoming_questions_count in (4, 9):
        text = f'Для вас уже есть {incoming_questions_count + 1} вопросов!'
    else:
        text = ''
    return text

def accept_acquaintance_keyboard(user_tg_id):
    keyboard = [
        [InlineKeyboardButton('Подходит!', callback_data=f'get_contact {user_tg_id}')],
        [InlineKeyboardButton('Можно ещё посмотреть?', callback_data='next')],
        [InlineKeyboardButton('Назад в меню', callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup