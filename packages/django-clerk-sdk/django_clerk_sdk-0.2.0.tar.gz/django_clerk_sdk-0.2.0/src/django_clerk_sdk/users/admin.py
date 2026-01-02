from django.contrib import admin

from django_clerk_sdk.core.compat import get_user_model

User = get_user_model()


class AccountAdmin(admin.ModelAdmin):
    class Meta:
        model = User


admin.site.register(User, AccountAdmin)