"""
Django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from . import models


class UserAdmin(BaseUserAdmin):
    """Defines the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'username']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('username',)}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'username',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )


class MessageToStaffAdmin(admin.ModelAdmin):
    """Defines the admin pages for MessageToStaff model,
       so for messages from users to staff."""
    list_display = ('email', 'subject')


admin.site.register(models.User, UserAdmin)
admin.site.register(models.UserProfile)
admin.site.register(models.Subscriber)
admin.site.register(models.NewsletterEmail)
admin.site.register(models.MessageToStaff, MessageToStaffAdmin)
