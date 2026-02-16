from django.contrib import admin
from .models import Profile, ImagesProfile

class ImagesProfileInline(admin.StackedInline):
    model = ImagesProfile
    can_delete = False
    verbose_name_plural = 'Avatar'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    inlines = [ImagesProfileInline]
    list_display = ('user', 'full_name', 'phone', 'has_avatar')
    search_fields = ('user__username', 'user__email', 'phone')  # удобно искать по юзеру и телефону

    def full_name(self, obj):
        """Показывает полное имя пользователя"""
        return obj.user.get_full_name()
    full_name.short_description = 'Full Name'

    def has_avatar(self, obj):
        """Показывает есть ли аватар"""
        return bool(obj.images and obj.images.src)
    has_avatar.boolean = True
    has_avatar.short_description = 'Avatar'