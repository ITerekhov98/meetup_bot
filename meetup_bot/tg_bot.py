from datetime import datetime

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
    Filters,
    CallbackContext, PreCheckoutQueryHandler
)

from django.conf import settings

from .models import Client, Questionnaire, Question, Block, Lecture, Event
from .tg_bot_lib import \
    get_menu_keyboard, get_accept_questionnarie_keyboard, \
    check_email, get_blocks_keyboard, get_lectures_keyboard, \
    waiting_ask_keyboard, get_next_question


RETURN_BUTTON_TEXT = '↩ Назад в меню'
GREETING_MSG = 'Здравствуйте! Это официальный бот по поддержке участников 🤖'


class TgChatBot(object):

    def __init__(self, token, event, states_functions, questions_for_questionnaire, readable_questions):
        self.event = event
        self.token = token 
        self.states_functions = states_functions
        self.questions_for_questionnaire = questions_for_questionnaire
        self.readable_questions = readable_questions
        self.updater = Updater(token=token, use_context=True)
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.handle_users_reply))
        self.updater.dispatcher.add_handler(CommandHandler('start', self.handle_users_reply))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.handle_users_reply))
        self.updater.dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))

    def handle_users_reply(self, update: Update, context: CallbackContext):
        user, created = Client.objects.get_or_create(
            tg_id=update.effective_chat.id,
        )
        if created:
            user.current_state = 'START'
        user.event = self.event

        if update.message:
            user_reply = update.message.text
        elif update.callback_query:
            user_reply = update.callback_query.data

        if user_reply == '/start':
            user.current_state = 'START'

        context.user_data['user'] = user
        context.bot_data['questions_for_questionnaire'] = self.questions_for_questionnaire
        context.bot_data['readable_questions'] = self.readable_questions
        state_handler = self.states_functions[user.current_state]
        next_state = state_handler(update, context)
        context.user_data['user'].current_state = next_state
        context.user_data['user'].save()


def start(update: Update, context: CallbackContext):
    greeting = GREETING_MSG
    reply_markup = get_menu_keyboard(context.user_data['user'].is_speaker)

    query = update.callback_query
    if query:
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=query.message.message_id
        )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=greeting,
        reply_markup=reply_markup
    )
    return 'HANDLE_MENU'


def handle_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=query.message.message_id
    )
    if query.data == 'program':
        return get_program_blocks(update, context)
    elif query.data == 'donate':
        return ask_donation_sum(update, context)
        return handle_donation(update, context)
    elif query.data == 'ask_speaker':
        return ask_speaker(update, context)
    elif query.data == 'acquaint':
        context.user_data['current_question'] = 0
        if Questionnaire.objects.filter(client=context.user_data['user']).exists():
            return accept_questionnarie_renewal(update, context)
        return handle_questionnaire(update, context)
    elif query.data == 'respond_to_questions':
        return respond_to_questions(update, context)


def get_program_blocks(update: Update, context: CallbackContext):
    event = context.user_data['user'].event
    # TODO get current event, load blocks only for the event
    event_blocks = Block.objects.all()

    event_from = event.start.strftime('%d.%m %Yг.')
    event_to = event.end.strftime('%d.%m %Yг.')
    event_dates = event_from if event_from == event_to else f'{event_from} - {event_to}'
    program_text = f'ПРОГРАММА МЕРОПРИЯТИЯ\n' \
                   f'«{event.title}»\n\n' \
                   f'{event_dates}\n\n' \
                   f'{event.description}'
    keyboard = []
    for block in event_blocks:
        keyboard.append([InlineKeyboardButton(block.title, callback_data=block.id)])

    keyboard.append(
        [InlineKeyboardButton(RETURN_BUTTON_TEXT, callback_data='return')]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=program_text,
        reply_markup=reply_markup
    )
    return 'HANDLE_PROGRAM_BLOCKS'


def handle_program_blocks(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    keyboard = []
    if query.data == 'return':
        return start(update, context)

    current_block = Block.objects.get(id=query.data)
    for lecture in current_block.lectures.all():
        keyboard.append([InlineKeyboardButton(lecture.title, callback_data=lecture.id)])

    keyboard.append(
        [InlineKeyboardButton(RETURN_BUTTON_TEXT, callback_data='return')]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=query.message.message_id
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Доклады блока: {current_block.title}',
        reply_markup=reply_markup
    )
    return 'HANDLE_PROGRAM_LECTURES'


def handle_program_lectures(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'return':
        return start(update, context)

    current_lecture = Lecture.objects.get(id=query.data)

    time_from = current_lecture.start.strftime('%H:%M')
    time_to = current_lecture.end.strftime('%H:%M')

    lecture_speakers = current_lecture.speakers.all()

    if lecture_speakers:
        speaker_data = 'Спикер(ы):\n'
        for speaker in lecture_speakers:
            speaker_data += f'{speaker.first_name}, {speaker.job_title}\n'
    else:
        speaker_data = ''

    msg_text = f'Доклад: {current_lecture.title}\n\n' \
               f'С {time_from} до {time_to}\n\n' \
               f'{speaker_data}\n' \
               f'{current_lecture.description}'

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(RETURN_BUTTON_TEXT, callback_data='return')]]
    )

    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=query.message.message_id
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg_text,
        reply_markup=reply_markup
    )
    return 'START'


def ask_donation_sum(update: Update, context: CallbackContext):
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(RETURN_BUTTON_TEXT, callback_data='return')]]
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Введите сумму доната в рублях числом (не менее 60)',
        reply_markup=reply_markup
    )
    return 'HANDLE_DONATION'


def handle_donation(update: Update, context: CallbackContext):
    query = update.callback_query
    if query and query.data == 'return':
        return start(update, context)

    users_sum = int(update.message.text)

    chat_id = update.effective_chat.id
    title = 'Задонатить'
    description = 'Организаторам на печеньки 🍪'
    payload = 'UserDonate'
    provider_token = settings.TG_MERCHANT_TOKEN
    start_parameter = 'test-payment'
    currency = 'RUB'
    sum_in_rub = users_sum
    prices = [LabeledPrice('Донат организаторам', sum_in_rub * 100)]

    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.message.message_id
    )
    context.bot.send_invoice(chat_id, title, description, payload,
                             provider_token, start_parameter, currency, prices)
    return 'START'


def precheckout_callback(update, context):
    query = update.pre_checkout_query
    if query.invoice_payload != 'UserDonate':
        context.bot.answer_pre_checkout_query(
            pre_checkout_query_id=query.id,
            ok=False,
            error_message='Что-то пошло не так и не туда...'
        )
    else:
        context.bot.answer_pre_checkout_query(
            pre_checkout_query_id=query.id,
            ok=True
        )


def successful_payment_callback(update, context):
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(RETURN_BUTTON_TEXT, callback_data='return')]])

    update.message.reply_text(
        text='Спасибо за донат!',
        reply_markup=reply_markup
    )


def ask_speaker(update: Update, context: CallbackContext):
    if update.message:
        speaker = Client.objects.get(lectures__pk=context.user_data['lecture_pk'])
        if not speaker.incoming_questions.exists():
            context.bot.send_message(
                chat_id=speaker.tg_id,
                text='Вам поступили вопросы по докладу! Не забудьте ответить',
            )
        Question.objects.create(
            question=update.message.text,
            from_user=context.user_data['user'],
            to_user=speaker
        )
        text = 'Ваш вопрос отправлен!'
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
        )
        return start(update, context)
    
    query = update.callback_query
    query.answer()
    if query.data == 'back_to_menu':
        return start(update, context)

    if query.data == 'ask_speaker':
        reply_markup = get_blocks_keyboard()
        text = 'Выберите интересующий блок мероприятия'
    elif 'block' in query.data:
        block_pk = query.data.split()[-1]
        reply_markup = get_lectures_keyboard(block_pk)
        text = 'Выберите интересующий доклад'
    elif 'lecture' in query.data:
        lecture_pk = query.data.split()[-1]
        context.user_data['lecture_pk'] = lecture_pk
        text = 'Введите ваш вопрос'
        reply_markup = waiting_ask_keyboard()

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup
    )
    return 'HANDLE_ASKING_SPEAKER'


def handle_questionnaire(update: Update, context: CallbackContext):
    question_index = context.user_data.get('current_question')
    user = context.user_data['user']
    questions_for_questionnaire = context.bot_data['questions_for_questionnaire']
    readable_questions = context.bot_data['readable_questions']

    if question_index != 0:
        previous_question = questions_for_questionnaire[question_index-1]
        if previous_question == 'email':
            is_valid_email = check_email(update, context)
            if not is_valid_email:
                return 'HANDLE_QUESTIONNAIRE'
        context.user_data[previous_question] = update.message.text

    if question_index < len(questions_for_questionnaire):
        question = readable_questions[questions_for_questionnaire[question_index]]
        context.user_data['current_question'] = question_index + 1
        if question_index == 0:
            with open('meetup_bot/questionnaire_intro.txt', 'r') as f:
                intro = f.read()
            question = f'{intro}\r\n\r\n{question}'
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=question,
        )
        return 'HANDLE_QUESTIONNAIRE'


    Questionnaire.objects.update_or_create(
        client=user,
        defaults= {
            'first_name': context.user_data['first_name'],
            'email': context.user_data['email'],
            'job_title': context.user_data['job_title'],
            'company': context.user_data['company']
        }
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Спасибо что прошли опрос',
    )
    return 'START'


def accept_questionnarie_renewal(update, context):
    if update.callback_query:
        query = update.callback_query
        query.answer()
        if query.data == 'back_to_menu':
            return start(update, context)
        elif query.data == 'accept':
            return handle_questionnaire(update, context)

    reply_markup = get_accept_questionnarie_keyboard()
    text = 'Вы уже заполняли анкету. Хотите изменить данные?'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup
    )
    return 'ACCEPT_QUESTIONNARIE_RENEWAL'



def respond_to_questions(update: Update, context: CallbackContext):
    if update.callback_query:
        query = update.callback_query
        query.answer()
        if query.data == 'back_to_menu':
            return start(update, context)

    respond_index = context.user_data.get('current_respond', 0)
    user = context.user_data['user']
    if respond_index == 0:
        questions = [ question.question for question in user.incoming_questions.all()]
        context.user_data['questions'] = questions
    else:
        questions = context.user_data['questions']
    
    if respond_index == len(questions):
        check_for_new_questions = user.incoming_questions.all()
        if check_for_new_questions.count() == len(questions):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Вопросов больше нет!'
            )
            return 'START'
        questions = [question.question for question in check_for_new_questions]
        context.user_data['questions'] = questions

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=questions[respond_index],
        reply_markup=get_next_question()
    )    
    context.user_data['current_respond'] = respond_index+1
    return 'HANDLE_RESPOND'
