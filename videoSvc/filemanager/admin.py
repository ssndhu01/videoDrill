from django.contrib import admin

from .models import *

@admin.register(AccountFiles)
class FilesAdmin(admin.ModelAdmin):
    pass

@admin.register(Files)
class FilesAdmin1(admin.ModelAdmin):
    pass
