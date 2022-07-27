from telegram import Update

from telegram.ext import (
    CallbackQueryHandler,
    PollAnswerHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
    Filters
    )

from .models import Client


class TgChatBot(object):

    def __init__(self, token, event, states_functions):
        self.event = event
        self.token = token 
        self.states_functions = states_functions
        self.updater = Updater(token=token)
        self.updater.dispatcher.add_handler(CommandHandler('start', self.handle_users_reply))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.handle_users_reply))

    def handle_users_reply(self, update: Update, context):
        user, created = Client.objects.get_or_create(
            tg_id=update.effective_chat.id,
        )
        if created:
            user.current_state = 'START'
            user.event.add(self.event)

        state_handler = self.states_functions[user.current_state]
        user, next_state = state_handler(update, context, user)
        user.current_state = next_state
        user.save()


def start(update: Update, context, user):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Привет! Здесь будет чат-бот',
    )
    return user, 'END'
