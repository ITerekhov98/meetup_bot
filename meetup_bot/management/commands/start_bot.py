from django.conf import settings
from django.core.management import BaseCommand

from meetup_bot.tg_bot import TgChatBot, start, end
from meetup_bot.models import Event


class Command(BaseCommand):

    def handle(self, *args, **options):
        start_bot()


def start_bot():
    current_event = Event.objects.first()
    bot = TgChatBot(
        settings.TELEGRAM_ACCESS_TOKEN,
        current_event,
        {
            'START': start,
        }
    )
    bot.updater.start_polling()
    bot.updater.idle()