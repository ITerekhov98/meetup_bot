from telegram import Update

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
    Filters,
    CallbackContext
    )

from .models import Client, Questionnaire
from .tg_bot_lib import get_menu_keyboard


class TgChatBot(object):

    def __init__(self, token, event, states_functions, questions_for_questionnaire):
        self.event = event
        self.token = token 
        self.states_functions = states_functions
        self.questions_for_questionnaire = questions_for_questionnaire
        self.updater = Updater(token=token, use_context=True)
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.handle_users_reply))
        self.updater.dispatcher.add_handler(CommandHandler('start', self.handle_users_reply))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.handle_users_reply))

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

        state_handler = self.states_functions[user.current_state]
        user, next_state = state_handler(update, context, user, self)
        user.current_state = next_state
        user.save()


def start(update: Update, context: CallbackContext, user, bot_details):
    greeting = '/МЕСТО ДЛЯ ПРИВЕТСТВИЯ/'
    reply_markup = get_menu_keyboard(user.is_speaker)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=greeting,
        reply_markup=reply_markup
    )
    return user, 'HANDLE_MENU'


def handle_menu(update: Update, context: CallbackContext, user, bot_details):
    query = update.callback_query
    query.answer()

    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=query.message.message_id
    )
    if query.data == 'program':
        return get_program(update, context, user, bot_details)
    elif query.data == 'donate':
        return handle_donation(update, context, user, bot_details)
    elif query.data == 'ask_speaker':
        return ask_speaker(update, context, user, bot_details)
    elif query.data == 'acquaint':
        context.user_data['current_question'] = 0
        return handle_questionnaire(update, context, user, bot_details)
    elif query.data == 'respond_to_questions':
        return respond_to_questions(update, context, user, bot_details)


def get_program(update: Update, context: CallbackContext, user, bot_details):
    # TODO functionality
    return user, 'START'


def handle_donation(update: Update, context: CallbackContext, user, bot_details):
    # TODO functionality
    return user, 'START'


def ask_speaker(update: Update, context: CallbackContext, user, bot_details):
    # TODO functionality
    return user, 'START'


def handle_questionnaire(update: Update, context: CallbackContext, user, bot_details):
    question_index = context.user_data.get('current_question')

    if question_index < len(bot_details.questions_for_questionnaire):
        question = bot_details.questions_for_questionnaire[question_index]
        context.user_data['current_question'] = question_index + 1
        if question_index != 0:
            previous_question = bot_details.questions_for_questionnaire[question_index-1]
            context.user_data[previous_question] = update.message.text
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=question,
        )
        return user, 'HANDLE_QUESTIONNAIRE'

    user_reply = update.message.text
    previous_question = bot_details.questions_for_questionnaire[question_index-1]
    context.user_data[previous_question] = user_reply
    Questionnaire.objects.create(
        client=user,
        first_name=context.user_data['first_name'],
        email = context.user_data['email'],
        job_title = context.user_data['job_title'],
        company = context.user_data['company']
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='thank you!',
    )
    return user, 'START'


def respond_to_questions(update: Update, context: CallbackContext, user, bot_details):
    # TODO functionality
    return user, 'START'