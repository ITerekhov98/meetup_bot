from django.conf import settings
from django.core.management import BaseCommand

from meetup_bot.tg_bot import TgChatBot, accept_questionnarie_renewal, handle_menu, handle_questionnaire, start
from meetup_bot.models import Event, Questionnaire


class Command(BaseCommand):

    def handle(self, *args, **options):
        start_bot()


def start_bot():
    current_event = Event.objects.first()
    questions_for_questionnaire = [
        field.name for field in Questionnaire._meta.get_fields()[1:]
    ]
    readable_questions = {
        'first_name': 'Как вас зовут?',
        'email': 'Напишите ваш email',
        'job_title': 'Кем вы работаете?',
        'company': 'В какой компании?',
    }
    bot = TgChatBot(
        settings.TELEGRAM_ACCESS_TOKEN,
        current_event,
        {
            'START': start,
            'HANDLE_MENU': handle_menu,
            'HANDLE_QUESTIONNAIRE': handle_questionnaire,
            'ACCEPT_QUESTIONNARIE_RENEWAL': accept_questionnarie_renewal
        },
        questions_for_questionnaire,
        readable_questions
    )
    bot.updater.start_polling()
    bot.updater.idle()