from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import TgUser, Phone, Task


class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'user_username', 'user_first_name',)
    list_display_links = ('user_username',)
    search_fields = ('user_username',)


admin.site.register(TgUser, UserAdmin)


class PhoneAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number',)
    list_display_links = ('user',)


admin.site.register(Phone, PhoneAdmin)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'get_photo')

    def get_photo(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="75">')
        else:
            return "No photo"


admin.site.register(Task, TaskAdmin)
