from django.conf import settings
from django.core.management import BaseCommand

from meetup_bot.tg_bot import TgChatBot


class Command(BaseCommand):

    def handle(self, *args, **options):
        start_bot()


def start_bot():

    bot = TgChatBot(
        settings.TELEGRAM_ACCESS_TOKEN,
    )
    bot.updater.start_polling()
    bot.updater.idle()