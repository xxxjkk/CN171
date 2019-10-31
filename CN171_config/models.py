from django.db import models

# Create your models here.

class CN171ModelStatus(models.Model):
    # '''CN171系统状态表'''
    id = models.AutoField(u"CN171模型状态id", primary_key=True)
    status_name = models.CharField(u"状态的name", max_length=20)
    model_flag = models.CharField(u"归属的model标志", max_length=20)

    def __unicode__(self):
        return self.status_name + "  " + self.model_flag

    class Meta:
        verbose_name = u'CN171系统状态表'
        verbose_name_plural = verbose_name
        ordering = ['id']
        db_table = "cn171_model_status"