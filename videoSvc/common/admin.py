from django.contrib import admin
from .models import *

@admin.register(VideoFomats)
class AuthorAdmin(admin.ModelAdmin):
    pass

@admin.register(Accounts)
class AuthorAdmin1(admin.ModelAdmin):
    pass


@admin.register(AccountTokens)
class AuthorAdmi21(admin.ModelAdmin):
    pass