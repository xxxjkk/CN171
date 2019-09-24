from django.contrib import admin

# Register your models here.

# CN171_login/admin.py
from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.User)