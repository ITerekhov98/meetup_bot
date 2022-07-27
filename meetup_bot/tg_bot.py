from telegram import Update

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
    Filters
    )

from .models import Client
from .tg_bot_lib import get_menu_keyboard


class TgChatBot(object):

    def __init__(self, token, event, states_functions):
        self.event = event
        self.token = token 
        self.states_functions = states_functions
        self.updater = Updater(token=token)
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.handle_users_reply))
        self.updater.dispatcher.add_handler(CommandHandler('start', self.handle_users_reply))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.handle_users_reply))

    def handle_users_reply(self, update: Update, context):
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
        user, next_state = state_handler(update, context, user)
        user.current_state = next_state
        user.save()


def start(update: Update, context, user):
    greeting = '/МЕСТО ДЛЯ ПРИВЕТСТВИЯ/'
    reply_markup = get_menu_keyboard(user.is_speaker)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=greeting,
        reply_markup=reply_markup
    )
    return user, 'HANDLE_MENU'


def handle_menu(update: Update, context, user):
    query = update.callback_query
    query.answer()

    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=query.message.message_id
    )
    if query.data == 'program':
        return get_program(update, context, user)
    elif query.data == 'donate':
        return handle_donation(update, context, user)
    elif query.data == 'ask_speaker':
        return ask_speaker(update, context, user)
    elif query.data == 'acquaint':
        return handle_questionnaire(update, context, user)
    elif query.data == 'respond_to_questions':
        return respond_to_questions(update, context, user)


def get_program(update: Update, context, user):
    # TODO functionality
    return user, 'START'


def handle_donation(update: Update, context, user):
    # TODO functionality
    return user, 'START'


def ask_speaker(update: Update, context, user):
    # TODO functionality
    return user, 'START'


def handle_questionnaire(update: Update, context, user):
    # TODO functionality
    return user, 'START'


def respond_to_questions(update: Update, context, user):
    # TODO functionality
    return user, 'START'