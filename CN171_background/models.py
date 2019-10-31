from django.db import models

# Create your models here.


class BgTaskManagement(models.Model):
    # '''后台管理表'''
    bg_id = models.AutoField(u"后台id", primary_key=True)
    bg_module = models.CharField(u"模块", max_length=56)
    bg_domain = models.CharField(u"中心", max_length=56)
    bg_status = models.CharField(u"状态", max_length=32, null=True, blank=True)
    bg_lastopr_user = models.CharField(u"最后一次操作人员", max_length=56,null=True, blank=True)
    bg_lastopr_type = models.CharField(u"最后一次操作类型", max_length=32,null=True, blank=True)
    bg_lastopr_time = models.DateTimeField(u"最后一次操作时间", null=True, blank=True)
    bg_lastopr_result = models.CharField(u"最后一次操作结果", max_length=32,null=True, blank=True)
    bg_task_start = models.TextField(u"启动脚本" )
    bg_task_stop = models.TextField(u"停止脚本" )
    bg_task_restart = models.TextField(u"重启脚本" )
    bg_task_query = models.TextField(u"查询脚本" )
    bg_insert_time = models.DateTimeField(u"录入时间", auto_now_add=True)

    def __str__(self):
        return "模块:"+self.bg_module + " 中心:" + self.bg_domain

    class Meta:
        verbose_name = u'后台管理表'
        verbose_name_plural = verbose_name
        ordering = ['bg_id']
        db_table = "bg_task_management"


class BgTaskLog(models.Model):
    # '''后台管理日志表'''
    bg_log_id = models.AutoField(u"日志id", primary_key=True)
    bg_id = models.IntegerField(u"后台id" )
    bg_operation_user = models.CharField(u"操作人员", max_length=56,null=True, blank=True)
    bg_operation = models.CharField(u"操作类型", max_length=32,null=True, blank=True)
    bg_opr_result = models.CharField(u"操作结果", max_length=32,null=True, blank=True)
    bg_operation_time = models.DateTimeField(u"操作时间")
    bg_log_dir = models.CharField(u"详细日志", max_length=256,null=True, blank=True)

    def __str__(self):
        return self.dis_name

    class Meta:
        verbose_name = u'后台管理日志表'
        verbose_name_plural = verbose_name
        db_table = "bg_task_log"

class BgDomainStatusDict(models.Model):
    # '''中心状态字典表'''
    bg_domainstatus_id = models.AutoField(primary_key=True)
    bg_domainstatus = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return self.dis_name

    class Meta:
        verbose_name = u'中心状态字典表'
        verbose_name_plural = verbose_name
        db_table = "bg_domainstatus_dict"