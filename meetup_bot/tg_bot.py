from telegram import Update

from telegram.ext import (
    CallbackQueryHandler,
    PollAnswerHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
    )

class TgChatBot(object):

    def __init__(self, token):
        self.token = token 
        self.updater = Updater(token=token)
        self.updater.dispatcher.add_handler(CommandHandler('start', start))


def start(update: Update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Привет! Здесь будет чат-бот',
    )