from django.db import models

# Create your models here.
#角色model
class AccRole(models.Model):
    acc_role_id = models.AutoField(u"角色id", primary_key=True)

    acc_role_name = models.CharField(u"角色名", max_length=128, unique=True)
    acc_role_right_name = models.CharField(u"角色权限名", max_length=56, unique=True)

#角色权限model
class AccReight(models.Model):
    acc_role_right_id = models.AutoField(u"角色id", primary_key=True)

    acc_role_right_name = models.CharField(u"角色权限名", max_length=56, unique=True)
    acc_role_right1 = models.CharField(u"角色权限1", max_length=128, unique=True)
    acc_role_right2 = models.CharField(u"角色权限2", max_length=128, unique=True)
    acc_role_right3 = models.CharField(u"角色权限3", max_length=128, unique=True)
    acc_role_right4 = models.CharField(u"角色权限3", max_length=128, unique=True)

