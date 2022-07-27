from django.conf import settings
from django.core.management import BaseCommand

from meetup_bot.tg_bot import TgChatBot, handle_menu, start
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
            'HANDLE_MENU': handle_menu
        }
    )
    bot.updater.start_polling()
    bot.updater.idle()