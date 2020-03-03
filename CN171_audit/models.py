from django.db import models


# Create your models here.
class staffInfo(models.Model):
    # 人员信息表
    staff_id = models.AutoField(u"id", primary_key=True)
    staff_name = models.CharField(u"姓名", max_length=32, unique=True)
    staff_4AAccount = models.CharField(u"4A主账号", max_length=64)
    staff_account = models.CharField(u"从账号", max_length=64)
    staff_group = models.CharField(u"所在组", max_length=64)
    staff_system = models.CharField(u"系统", max_length=64)
    staff_post = models.CharField(u"职责", max_length=32)
    staff_status = models.CharField(u"状态", max_length=32)

    def __unicode__(self):
        return self.staff_id

    class Meta:
        verbose_name = u"人员信息表"
        verbose_name_plural = verbose_name
        ordering = ['staff_id']
        db_table = 'staff_info'
