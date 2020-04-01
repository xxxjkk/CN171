from django.contrib import admin

# Register your models here.
# 自定义类，类名自己定，但必须继承ModelAdmin
from CN171_account import models
from CN171_account.models import Permission


class PermissionConfig(admin.ModelAdmin):
    list_display = ['pk', 'title', 'url']
    ordering = ['pk']  # 按照主键从低到高

admin.site.register(Permission, PermissionConfig)
admin.site.register(models.User)