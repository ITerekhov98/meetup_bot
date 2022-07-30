import requests
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect
from requests.exceptions import HTTPError, ConnectionError

from .models import Event, Client, Lecture, Donate, Block, Notification, \
    Questionnaire, ProposedLecture


class LectureInline(admin.TabularInline):
    model = Lecture
    raw_id_fields = ("speakers",)
    fields = ("title", "is_timeout", "speakers", "start", "end",)
    extra = 0


class BlockInline(admin.TabularInline):
    model = Block
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start", "end")
    search_fields = ["title", ]
    inlines = [BlockInline]


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("title", "start", "end")
    search_fields = ["title", ]
    list_filter = ("event",)
    inlines = [LectureInline]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("tg_id", "first_name", "job_title", "is_speaker")
    list_editable = ["job_title"]
    readonly_fields = ["current_state"]
    list_filter = ("event", "is_speaker")
    search_fields = ["tg_id", "first_name"]
    fields = ("tg_id", "is_speaker", "event", "first_name", "job_title")


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ("title", "start", "end", "get_speakers")
    search_fields = ["title", ]
    list_filter = ("block",)
    raw_id_fields = ("speakers",)

    def save_model(self, request, obj, form, change):
        obj.save()
        for client_object in form.cleaned_data['speakers']:
            client = Client.objects.get(pk=client_object.id)
            client.is_speaker = True
            client.save()

    def get_speakers(self, obj):
        return obj.get_speakers()

    get_speakers.short_description = 'Спикеры'


@admin.register(Donate)
class DonateAdmin(admin.ModelAdmin):
    list_display = ("client", "amount")


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ("client", "first_name", "job_title", "company", "email")
    search_fields = ["client", "first_name", "company"]


@admin.register(ProposedLecture)
class ProposedLectureAdmin(admin.ModelAdmin):
    search_fields = ["lecture_title", ]
    list_filter = ("user",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "message")
    search_fields = ["title", ]

    change_form_template = "admin/model_notification.html"

    def response_change(self, request, obj):
        if "_send-notification" in request.POST:
            token = settings.TELEGRAM_ACCESS_TOKEN
            clients = Client.objects.all()
            for client in clients:
                chat_id = client.tg_id
                url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={obj.message}"
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                except HTTPError:
                    # TODO логируем ошибку
                    pass
                except ConnectionError:
                    # TODO логируем ошибку
                    pass
            self.message_user(request, "Уведомление отправлено")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)
