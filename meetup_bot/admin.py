import requests
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect
from requests.exceptions import HTTPError, ConnectionError

from .models import Event, Client, Lecture, Donate, Block, Notification


class LectureInline(admin.TabularInline):
    model = Lecture
    raw_id_fields = ("speaker",)
    fields = ("title", "is_timeout", "speaker", "start", "end",)
    extra = 0


class BlockInline(admin.TabularInline):
    model = Block
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    search_fields = ["title", ]
    inlines = [BlockInline]


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    search_fields = ["title", ]
    list_filter = ("event",)
    inlines = [LectureInline]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    readonly_fields = ["current_state"]
    list_filter = ("event",)
    search_fields = ["tg_id", ]
    fields = ("tg_id", "is_speaker", "event", "first_name", "job_title")


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    search_fields = ["title", ]
    list_filter = ("block",)
    raw_id_fields = ("speaker",)


@admin.register(Donate)
class DonateAdmin(admin.ModelAdmin):
    list_filter = ("event",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
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
                    # логируем ошибку
                    pass
                except ConnectionError:
                    # логируем ошибку
                    pass
            self.message_user(request, "Уведомление отправлено")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)
