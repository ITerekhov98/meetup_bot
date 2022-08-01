import os
from contextvars import Context

from django.conf import settings
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, \
    LabeledPrice, error
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    Updater,
    Filters,
    CallbackContext, PreCheckoutQueryHandler
)

from .models import Client, Questionnaire, Question, Block, Lecture, Donate, \
    ProposedLecture
from .tg_bot_lib import \
    get_menu_keyboard, get_acquaintance_keyboard, \
    check_email, get_blocks_keyboard, get_lectures_keyboard, \
    back_to_menu_keyboard, get_speakers_keyboard, get_questions_keyboard, \
    get_text_notification, accept_acquaintance_keyboard, \
    RETURN_BUTTON_TEXT, GREETING_MSG, delete_callback_msg, delete_update_msg


class TgChatBot(object):

    def __init__(self, token, event, states_functions,
                 questions_for_questionnaire, readable_questions):
        self.event = event
        self.token = token
        self.states_functions = states_functions
        self.questions_for_questionnaire = questions_for_questionnaire
        self.readable_questions = readable_questions
        self.updater = Updater(token=token, use_context=True)
        self.updater.dispatcher.add_handler(
            CallbackQueryHandler(self.handle_users_reply))
        self.updater.dispatcher.add_handler(
            CommandHandler('start', self.handle_users_reply))
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.text, self.handle_users_reply))
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.document, get_resume))
        self.updater.dispatcher.add_handler(
            PreCheckoutQueryHandler(precheckout_callback))
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.successful_payment,
                           successful_payment_callback))

    def handle_users_reply(self, update: Update, context: CallbackContext):
        user, created = Client.objects.get_or_create(
            tg_id=update.effective_chat.id,
        )
        if not user.first_name:
            user.first_name = update.effective_chat.first_name
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
        context.bot_data[
            'questions_for_questionnaire'] = self.questions_for_questionnaire
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
        delete_callback_msg(update, context)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=greeting,
        reply_markup=reply_markup
    )
    return 'HANDLE_MENU'


def handle_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'program':
        return get_program_blocks(update, context)
    elif query.data == 'donate':
        return ask_donation_sum(update, context)
    elif query.data == 'ask_speaker':
        return ask_speaker(update, context)
    elif query.data == 'signup_speakers':
        return handle_signup_speakers(update, context)
    elif query.data == 'acquaint':
        if Questionnaire.objects.filter(
                client=context.user_data['user']).exists():
            return handle_acquaintance(update, context)
        return handle_questionnaire(update, context)
    elif query.data == 'respond_to_questions':
        return respond_to_questions(update, context)


def get_program_blocks(update: Update, context: CallbackContext):
    query = update.callback_query
    event = context.user_data['user'].event
    context.user_data['current_block'] = ''
    context.user_data['current_lecture'] = ''

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
        keyboard.append(
            [InlineKeyboardButton(block.title, callback_data=block.id)])

    keyboard.append(
        [InlineKeyboardButton(RETURN_BUTTON_TEXT, callback_data='return')]
    )

    delete_callback_msg(update, context)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=program_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return 'HANDLE_PROGRAM_BLOCKS'


def handle_program_blocks(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    keyboard = []
    if query.data == 'return':
        return start(update, context)
    elif query.data == 'return_to_blocks':
        return get_program_blocks(update, context)
    elif query.data != 'return_to_lectures':
        context.user_data['current_block'] = Block.objects.get(id=query.data)

    current_block = context.user_data['current_block']
    for lecture in current_block.lectures.all():
        button_text = f'{lecture.start.strftime("%H:%M")} {lecture.title}'
        keyboard.append(
            [InlineKeyboardButton(button_text, callback_data=lecture.id)])

    keyboard.append([InlineKeyboardButton('↩ Назад к блокам',
                                          callback_data='return_to_blocks')])
    keyboard.append(
        [InlineKeyboardButton(RETURN_BUTTON_TEXT, callback_data='return')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    delete_callback_msg(update, context)
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
    elif query.data == 'return_to_blocks':
        return get_program_blocks(update, context)
    elif query.data == 'return_to_lectures':
        return handle_program_blocks(update, context)

    context.user_data['current_lecture'] = Lecture.objects.get(id=query.data)
    current_lecture = context.user_data['current_lecture']
    time_from = current_lecture.start.strftime('%H:%M')
    time_to = current_lecture.end.strftime('%H:%M')

    lecture_speakers = current_lecture.speakers.all()

    if lecture_speakers:
        speaker_data = 'Спикер(ы):\n'
        for speaker in lecture_speakers:
            speaker_data += f'{speaker.first_name}, {speaker.job_title}\n'
    else:
        speaker_data = ''

    if current_lecture.is_timeout:
        msg_text = f'Перерыв с {time_from} до {time_to}'
    else:
        msg_text = f'Доклад: {current_lecture.title}\n\n' \
                   f'{time_from} – {time_to}\n\n' \
                   f'{speaker_data}\n' \
                   f'{current_lecture.description}'

    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('↩ Назад к списку',
                                  callback_data='return_to_lectures')],
            [InlineKeyboardButton(RETURN_BUTTON_TEXT, callback_data='return')],
        ]
    )

    delete_callback_msg(update, context)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg_text,
        reply_markup=reply_markup
    )
    return 'HANDLE_PROGRAM_LECTURES'


def ask_donation_sum(update: Update, context: CallbackContext):
    delete_callback_msg(update, context)

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(RETURN_BUTTON_TEXT, callback_data='return')]]
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Введите сумму доната в рублях числом не менее 10 :)',
        reply_markup=reply_markup
    )
    return 'HANDLE_DONATION'


def handle_donation(update: Update, context: CallbackContext):
    query = update.callback_query
    if query and query.data == 'return':
        return start(update, context)

    try:
        users_sum = int(update.message.text)
    except ValueError:
        delete_update_msg(update, context)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Введите сумму числом. Вы ввели «{update.message.text}»'
        )
        return 'HANDLE_DONATION'

    chat_id = update.effective_chat.id
    title = 'Задонатить'
    description = 'Организаторам на печеньки 🍪'
    payload = 'UserDonate'
    provider_token = settings.TG_MERCHANT_TOKEN
    start_parameter = 'test-payment'
    currency = 'RUB'
    sum_in_rub = users_sum
    prices = [LabeledPrice('Донат организаторам', sum_in_rub * 100)]

    delete_update_msg(update, context)
    try:
        context.bot.send_invoice(chat_id, title, description, payload,
                                 provider_token, start_parameter, currency,
                                 prices)
    except error.BadRequest:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Введена неверная сумма, попробуйте снова'
        )
        return 'HANDLE_DONATION'

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
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(RETURN_BUTTON_TEXT, callback_data='return')]])

    donated_sum = update.message.successful_payment.total_amount / 100

    Donate.objects.create(
        amount=donated_sum,
        client=context.user_data['user'],
        event=context.user_data['user'].event
    )

    update.message.reply_text(
        text='Спасибо за донат!',
        reply_markup=reply_markup
    )


def ask_speaker(update: Update, context: CallbackContext):
    if update.message:
        speaker = Client.objects.get(pk=context.user_data['speaker_pk'])
        text = get_text_notification(speaker)
        if text:
            context.bot.send_message(
                chat_id=speaker.tg_id,
                text=text,
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
        text = 'Выберите спикера, которому хотите задать вопрос'
        reply_markup = get_speakers_keyboard(lecture_pk)

    elif 'speaker' in query.data:
        speaker_pk = query.data.split()[-1]
        context.user_data['speaker_pk'] = speaker_pk
        text = 'Введите ваш вопрос'
        reply_markup = back_to_menu_keyboard()

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup
    )
    return 'HANDLE_ASKING_SPEAKER'


def handle_questionnaire(update: Update, context: CallbackContext):
    user = context.user_data['user']
    question_index = context.user_data.get('current_question', 0)
    questions_for_questionnaire = context.bot_data[
        'questions_for_questionnaire']
    readable_questions = context.bot_data['readable_questions']

    if question_index != 0:
        previous_question = questions_for_questionnaire[question_index - 1]
        if previous_question == 'email':
            is_valid_email = check_email(update, context)
            if not is_valid_email:
                return 'HANDLE_QUESTIONNAIRE'
        context.user_data[previous_question] = update.message.text

    if question_index < len(questions_for_questionnaire):
        question = readable_questions[
            questions_for_questionnaire[question_index]]
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
        defaults={
            'first_name': context.user_data['first_name'],
            'email': context.user_data['email'],
            'job_title': context.user_data['job_title'],
            'company': context.user_data['company']
        }
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Спасибо что прошли опрос! Подобрать вам собеседника?',
        reply_markup=get_acquaintance_keyboard()
    )
    return 'HANDLE_ACQUAINTANCE'


def handle_acquaintance(update, context: Context):
    user = context.user_data['user']
    query = update.callback_query
    query.answer()

    if query.data == 'acquaint':
        reply_markup = get_acquaintance_keyboard()
        text = 'Готовы с кем-нибудь познакомиться?'
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=reply_markup
        )
        return 'HANDLE_ACQUAINTANCE'

    if query.data == 'back_to_menu':
        return start(update, context)

    elif query.data == 'update_questionnaire':
        return handle_questionnaire(update, context)

    elif 'get_contact' in query.data:
        tg_id = query.data.split()[-1]
        text = f'[Приятного общения\!](tg://user?id={tg_id})'
        reply_markup = back_to_menu_keyboard()
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=reply_markup,
            parse_mode='MarkdownV2',
        )
        return 'HANDLE_ACQUAINTANCE'

    questionnaire = Questionnaire.objects \
        .exclude(client=user) \
        .select_related('client') \
        .order_by('?') \
        .first()

    if not questionnaire:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Ого, видимо вы первый зарегестрировались! Попробуйте чуть позже',
            reply_markup=back_to_menu_keyboard()
        )
        return 'HANDLE_ACQUAINTANCE'

    text = 'Анкета участника {}\r\nДолжность {}\r\nКомпания {}'.format(
        questionnaire.first_name,
        questionnaire.job_title,
        questionnaire.company
    )
    reply_markup = accept_acquaintance_keyboard(questionnaire.client.tg_id)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup
    )
    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=query.message.message_id
    )
    return 'HANDLE_ACQUAINTANCE'


def handle_questionnaire_for_signup(update: Update, context: CallbackContext):
    user = context.user_data['user']
    question_index = context.user_data.get('current_question', 0)
    questions_for_questionnaire = context.bot_data[
        'questions_for_questionnaire']
    readable_questions = context.bot_data['readable_questions']

    if question_index != 0:
        previous_question = questions_for_questionnaire[question_index - 1]
        if previous_question == 'email':
            is_valid_email = check_email(update, context)
            if not is_valid_email:
                return 'HANDLE_QUESTIONNAIRE_FOR_SIGNUP'
        context.user_data[previous_question] = update.message.text

    if question_index < len(questions_for_questionnaire):
        question = readable_questions[
            questions_for_questionnaire[question_index]]
        context.user_data['current_question'] = question_index + 1
        if question_index == 0:
            with open('meetup_bot/questionnaire_intro_signup.txt', 'r') as f:
                intro = f.read()
            question = f'{intro}\r\n\r\n{question}'
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=question,
        )
        return 'HANDLE_QUESTIONNAIRE_FOR_SIGNUP'

    Questionnaire.objects.update_or_create(
        client=user,
        defaults={
            'first_name': context.user_data['first_name'],
            'email': context.user_data['email'],
            'job_title': context.user_data['job_title'],
            'company': context.user_data['company']
        }
    )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Загрузите ваше резюме в формате PDF',
    )

    return 'HANDLE_SIGNUP_SPEAKERS'


def get_resume(update, context):
    resume = context.bot.get_file(update.message.document).download(
        custom_path=f'{settings.MEDIA_ROOT}{update.message.document.file_name}')
    questionnaire = Questionnaire.objects.filter(
        client=context.user_data['user'])[0]
    questionnaire.resume = os.path.basename(resume)
    questionnaire.save()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Введите вашу тему',
    )
    return 'HANDLE_SIGNUP_SPEAKERS'


def handle_signup_speakers(update, context: Context):
    user = context.user_data['user']
    questionnaire_bool = Questionnaire.objects.filter(
        client=context.user_data['user']).exists()

    if not questionnaire_bool:
        return handle_questionnaire_for_signup(update, context)
    questionnaire = Questionnaire.objects.filter(
        client=context.user_data['user'])[0]
    if not questionnaire.resume:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Загрузите ваше резюме в формате PDF',
        )
        return 'HANDLE_SIGNUP_SPEAKERS'
    if update.message:
        ProposedLecture.objects.create(user=user,
                                       lecture_title=update.message.text,
                                       questionnaire=questionnaire)
        reply_markup = get_menu_keyboard(context.user_data['user'].is_speaker)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Ваша заявка отправлена',
            reply_markup=reply_markup
        )
        return 'HANDLE_MENU'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Введите вашу тему',
    )
    return 'HANDLE_SIGNUP_SPEAKERS'


def respond_to_questions(update: Update, context: CallbackContext):
    respond_index = context.user_data.get('current_respond', 0)
    user = context.user_data['user']

    if update.callback_query:
        query = update.callback_query
        query.answer()
        if query.data == 'back_to_menu':
            return start(update, context)

        if query.data == 'reply':
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Введите ваш ответ',
            )
            return 'HANDLE_RESPOND'

        if query.data == 'next':
            respond_index += 1
        if query.data == 'previous':
            respond_index -= 1 if respond_index > 0 else 0

    if update.message:
        speaker_reply = update.message.text
        question = context.user_data['questions'][respond_index]
        text = 'Ответ на вопрос {} от {}: \r\n{}'.format(
            question.question,
            user.first_name,
            speaker_reply
        )
        context.bot.send_message(
            chat_id=question.from_user.tg_id,
            text=text
        )
        respond_index += 1
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Ваш ответ отправлен!'
        )

    if respond_index == 0:
        questions = user.incoming_questions.all().select_related('from_user')
        context.user_data['questions'] = questions
    else:
        questions = context.user_data['questions']

    questions_count = questions.count()
    if respond_index >= questions_count:
        check_for_new_questions = user.incoming_questions.all().select_related(
            'from_user')
        if check_for_new_questions.count() == questions_count:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Вопросов больше нет!',
                reply_markup=get_questions_keyboard()
            )
            return 'HANDLE_RESPOND'
        questions = check_for_new_questions
        context.user_data['questions'] = questions

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=questions[respond_index].question,
        reply_markup=get_questions_keyboard()
    )
    context.user_data['current_respond'] = respond_index
    return 'HANDLE_RESPOND'
