from django.db import models

# Create your models here.
# CN171_login/models.py

from django.db import models


class User(models.Model):
    # '''用户表'''

    acc_user_id = models.AutoField(primary_key=True)

    acc_user_name = models.CharField(max_length=128, unique=True)
    acc_user_CNname = models.CharField(max_length=128, unique=True)

    acc_user_password = models.CharField(max_length=256)

    acc_role_name = models.CharField(max_length=30, null=True, blank=True)
    acc_user_status = models.CharField(max_length=30, null=True, blank=True)
    acc_user_createtime = models.DateTimeField(auto_now_add=True)

    acc_user_email = models.EmailField(null=True, blank=True)
    acc_user_mobile = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = "acc_user"
