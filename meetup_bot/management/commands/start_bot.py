from django.conf import settings
from django.core.management import BaseCommand

from meetup_bot.models import Event, Questionnaire
from meetup_bot.tg_bot import TgChatBot, handle_acquaintance, ask_speaker, \
    handle_menu, handle_questionnaire, start, respond_to_questions, \
    handle_program_blocks, handle_program_lectures, handle_donation, \
    handle_signup_speakers, handle_questionnaire_for_signup, get_resume


class Command(BaseCommand):

    def handle(self, *args, **options):
        start_bot()


def start_bot():
    current_event = Event.objects.first()
    questions_for_questionnaire = [
        field.name for field in Questionnaire._meta.get_fields()[2:-1]
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
            'ACCEPT_QUESTIONNARIE_RENEWAL': handle_acquaintance,
            'HANDLE_ASKING_SPEAKER': ask_speaker,
            'HANDLE_RESPOND': respond_to_questions,
            'HANDLE_PROGRAM_BLOCKS': handle_program_blocks,
            'HANDLE_PROGRAM_LECTURES': handle_program_lectures,
            'HANDLE_DONATION': handle_donation,
            'HANDLE_ACQUAINTANCE': handle_acquaintance,
            'HANDLE_SIGNUP_SPEAKERS': handle_signup_speakers,
            'HANDLE_QUESTIONNAIRE_FOR_SIGNUP': handle_questionnaire_for_signup,
            'GET_RESUME': get_resume
        },
        questions_for_questionnaire,
        readable_questions
    )
    bot.updater.start_polling()
    bot.updater.idle()
