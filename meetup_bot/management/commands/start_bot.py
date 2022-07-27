from django.conf import settings
from django.core.management import BaseCommand

from meetup_bot.tg_bot import TgChatBot, handle_menu, start
from meetup_bot.models import Event, Questionnaire


class Command(BaseCommand):

    def handle(self, *args, **options):
        start_bot()


def start_bot():
    current_event = Event.objects.first()
    questions_for_questionnaire = [
        field.name for field in Questionnaire._meta.get_fields()[1:]
    ]
    bot = TgChatBot(
        settings.TELEGRAM_ACCESS_TOKEN,
        current_event,
        {
            'START': start,
            'HANDLE_MENU': handle_menu
        },
        questions_for_questionnaire
    )
    bot.updater.start_polling()
    bot.updater.idle()