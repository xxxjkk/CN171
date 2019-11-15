from django.db import models

# Create your models here.
# CN171_login/models.py

from django.db import models


class User(models.Model):
    # '''用户表'''

    acc_user_id = models.AutoField(u"用户id",primary_key=True)

    acc_user_name = models.CharField(u"用户名",max_length=128, unique=True)
    acc_user_CNname = models.CharField(u"用户中文名",max_length=128, unique=True)

    acc_user_password = models.CharField(u"密码",max_length=256)

    acc_role_name = models.CharField(u"角色名",max_length=30, null=True, blank=True)
    acc_user_status = models.CharField(u"用户状态",max_length=30, null=True, blank=True)
    acc_user_createtime = models.DateTimeField(u"用户创建时间",auto_now_add=True)

    acc_user_email = models.EmailField(u"邮箱",null=True, blank=True)
    acc_user_mobile = models.CharField(u"电话",max_length=30, null=True, blank=True)
    acc_last_log_time = models.DateTimeField(u"最后登录时间",null=True, blank=True)
    acc_user_operation = models.CharField(u"用户最近操作",max_length=128,null=True, blank=True)
    def __str__(self):
        return self.acc_user_name

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = "acc_user"
