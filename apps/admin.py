from django.contrib import admin

from apps.models import Video


@admin.register(Video)
class VideoModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'duration']
    readonly_fields = ['duration']
