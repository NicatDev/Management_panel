from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import AccountCreateForm
from .models import Account, Instagram, SocialPlatform


@admin.register(Account)
class AccountAdmin(UserAdmin):
    add_form = AccountCreateForm
    list_display = ['first_name', 'last_name', 'email']
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", 'description', 'company', "profile_picture")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_superuser",
                    "is_staff",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None, {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", 'description', 'company', "profile_picture", "password1", "password2",)
            }
        ),
    )


@admin.register(SocialPlatform)
class SocialPlatformAdmin(admin.ModelAdmin):
    list_display = ['account']


@admin.register(Instagram)
class InstagramAdmin(admin.ModelAdmin):
    list_display = ['username', 'twoFA']