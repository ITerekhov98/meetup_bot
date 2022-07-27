from django.contrib import admin

from .models import Event, Client, Lecture, Donate, Block


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
    fields = ("tg_id", "is_speaker", "event",)


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    search_fields = ["title", ]
    list_filter = ("block",)
    raw_id_fields = ("speaker",)


@admin.register(Donate)
class DonateAdmin(admin.ModelAdmin):
    list_filter = ("event",)

