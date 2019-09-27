from django.db import models

# Create your models here.


class BgTaskManagement(models.Model):
    # '''后台管理表'''
    bg_id = models.AutoField(primary_key=True)
    bg_module = models.CharField(max_length=56)
    bg_domain = models.CharField(max_length=56)
    bg_status = models.CharField(max_length=32,null=True, blank=True)
    bg_lastopr_user = models.CharField(max_length=56,null=True, blank=True)
    bg_lastopr_type = models.CharField(max_length=32,null=True, blank=True)
    bg_lastopr_time = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    bg_lastopr_result = models.CharField(max_length=32,null=True, blank=True)
    bg_task_start = models.TextField()
    bg_task_stop = models.TextField()
    bg_task_restart = models.TextField()
    bg_task_query = models.TextField()
    bg_insert_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.dis_name

    class Meta:
        verbose_name = u'后台管理表'
        verbose_name_plural = verbose_name
        ordering = ['bg_id']
        db_table = "bg_task_management"


class BgTaskLog(models.Model):
    # '''后台管理日志表'''
    bg_log_id = models.AutoField(primary_key=True)
    bg_id = models.IntegerField()
    bg_operation_user = models.CharField(max_length=56,null=True, blank=True)
    bg_operation = models.CharField(max_length=32,null=True, blank=True)
    bg_opr_result = models.CharField(max_length=32,null=True, blank=True)
    bg_operation_time = models.DateTimeField(auto_now_add=True)
    bg_log_dir = models.CharField(max_length=32,null=True, blank=True)

    def __unicode__(self):
        return self.dis_name

    class Meta:
        verbose_name = u'后台管理日志表'
        verbose_name_plural = verbose_name
        db_table = "bg_task_log"

class BgDomainStatusDict(models.Model):
    # '''中心状态字典表'''
    bg_domainstatus_id = models.AutoField(primary_key=True)
    bg_domainstatus = models.CharField(max_length=32, null=True, blank=True)

    def __unicode__(self):
        return self.dis_name

    class Meta:
        verbose_name = u'中心状态字典表'
        verbose_name_plural = verbose_name
        db_table = "bg_domainstatus_dict"