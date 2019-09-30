from django.db import models

# Create your models here.


class BgTaskManagement(models.Model):
    # '''后台管理表'''
    bg_id = models.AutoField(primary_key=True, verbose_name=u"任务管理id")
    bg_module = models.CharField(max_length=56, verbose_name=u"归属模块")
    bg_domain = models.CharField(max_length=56, verbose_name=u"归属中心")
    bg_status = models.CharField(max_length=32, verbose_name=u"状态", null=True, blank=True)
    bg_lastopr_user = models.CharField(max_length=56, verbose_name=u"最后一次操作人员", null=True, blank=True)
    bg_lastopr_type = models.CharField(max_length=32, verbose_name=u"最后一次操作类型", null=True, blank=True)
    bg_lastopr_time = models.DateTimeField(auto_now_add=True,verbose_name=u"最后一次操作时间", null=True, blank=True)
    bg_lastopr_result = models.CharField(max_length=32,verbose_name=u"操作结果", null=True, blank=True)
    bg_task_start = models.TextField(verbose_name=u"任务启动脚本")
    bg_task_stop = models.TextField(verbose_name=u"任务暂停脚本")
    bg_task_restart = models.TextField(verbose_name=u"任务重启脚本")
    bg_task_query = models.TextField(verbose_name=u"任务查询脚本")
    bg_insert_time = models.DateTimeField(auto_now_add=True, verbose_name=u"插入时间")

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
