from django.db import models


# Create your models here.

# 表空间字典表
class TableSpaceDict(models.Model):
    id = models.AutoField(u"id", primary_key=True)
    tablespace_name = models.CharField(max_length=64, verbose_name='表空间名')
    DB_Name = models.CharField(max_length=32, verbose_name='所属数据库名', null=True, blank=True)


    class Meta:
        verbose_name = '表空间表'
        verbose_name_plural = '表空间字典表'
        db_table = "ai_tablespacedict"


# 表空间字典表
class AiopsDetectLog(models.Model):
    id = models.AutoField(u"id", primary_key=True)
    ai_tablespacedict = models.ForeignKey('TableSpaceDict', null=True, blank=True, verbose_name="关联表空间表",
                                          on_delete=models.CASCADE)
    create_time = models.DateTimeField(u"生成时间", auto_now_add=True)
    capacity_total = models.CharField(max_length=128, verbose_name='容量总量', null=True, blank=True)
    alarm_threshold = models.CharField(max_length=128, verbose_name='告警阈值', null=True, blank=True)
    start_time = models.DateTimeField(u"预测开始时间", null=True, blank=True)
    end_time = models.DateTimeField(u"预测结束时间", null=True, blank=True)
    result = models.CharField(max_length=256, verbose_name='预测结果', null=True, blank=True)
    status = models.CharField(max_length=32, verbose_name='生成状态', null=True, blank=True)


    class Meta:
        verbose_name = '容量预测表'
        verbose_name_plural = '容量预测表'
        db_table = "ai_detect_log"


# 预测结果表
class DetectResult(models.Model):
    id = models.AutoField(u"id", primary_key=True)
    detect_time = models.DateField(u"预测时间", null=True, blank=True)
    origin = models.CharField(max_length=56, verbose_name='原始值')
    predict = models.CharField(max_length=56, verbose_name='预测值', null=True, blank=True)
    ai_tablespacedict = models.ForeignKey('TableSpaceDict', null=True, blank=True, verbose_name="关联表空间表",
                                          on_delete=models.CASCADE)
    create_time = models.DateTimeField(u"生成时间", null=True, blank=True)
    def __str__(self):
        return self.predict

    class Meta:
        verbose_name = '预测结果数据表'
        verbose_name_plural = '预测结果数据表'
        db_table = "ai_detect_result"


# 智能告警分析表（PBOSS）
class PbossWarningAnalysis(models.Model):
    warning_id = models.AutoField(u"告警id", primary_key=True)
    warning_message = models.CharField(u"告警内容", max_length=2048)
    warning_type = models.CharField(u"告警类别", max_length=128)
    warning_number = models.IntegerField(u"告警数量")
    warning_arisingtime = models.DateTimeField(u"告警发生时间")
    # warning_updatingtime = models.DateTimeField(u"告警更新时间", auto_now=True)
    warning_updatingtime = models.DateTimeField(u"告警更新时间")
    warning_pre_solvedtime = models.DateTimeField(u"告警预计解决时间")
    warning_starttime = models.DateTimeField(u"统计开始时间")
    warning_status = models.CharField(u"告警状态", max_length=20)
    warning_reason1 = models.CharField(u"告警原因1", max_length=1024)
    warning_reason2 = models.CharField(u"告警原因2", max_length=1024)
    warning_reason3 = models.CharField(u"告警原因3", max_length=1024)
    extend1 = models.CharField(u"扩展字段1", max_length=256)
    extend2 = models.CharField(u"扩展字段2", max_length=256)
    extend3 = models.CharField(u"扩展字段3", max_length=256)

    def __unicode__(self):
        return self.warning_id

    class Meta:
        verbose_name = u"智能告警分析表（PBOSS）"
        verbose_name_plural = verbose_name
        ordering = ['warning_arisingtime']
        db_table = 'warning_pboss_analysis'


# 各类告警数量表（PBOSS）
class PbossWarningNum(models.Model):
    # warning_runtime = models.DateTimeField(u"统计时间", primary_key=True, auto_now=True)
    warning_runtime = models.DateTimeField(u"统计时间", primary_key=True)
    warning_backlog_solving = models.IntegerField(u"环节积压（解决中）")
    warning_backlog_pre_solved = models.IntegerField(u"环节积压（预解决）")
    warning_orderfailed_solving = models.IntegerField(u"环节异常（解决中）")
    warning_orderfailed_pre_solved = models.IntegerField(u"环节异常（预解决）")
    warning_appfailed_solving = models.IntegerField(u"集群/应用异常（解决中）")
    warning_appfailed_pre_solved = models.IntegerField(u"集群/应用异常（预解决）")
    warning_disk_solving = models.IntegerField(u"磁盘/表空间告警（解决中）")
    warning_disk_pre_solved = models.IntegerField(u"磁盘/表空间告警（预解决）")
    warning_whole_solving = models.IntegerField(u"全网监控预警（解决中）")
    warning_whole_pre_solved = models.IntegerField(u"全网监控预警（预解决）")
    warning_other_solving = models.IntegerField(u"其它（解决中）")
    warning_other_pre_solved = models.IntegerField(u"其它（预解决）")

    def __unicode__(self):
        return self.warning_runtime

    class Meta:
        verbose_name = u"各类告警数量（PBOSS）"
        verbose_name_plural = verbose_name
        ordering = ['warning_runtime']
        db_table = 'warning_pboss_num'

# KPI指标表（PBOSS）
class PbossWarningKPI(models.Model):
    # warning_runtime = models.DateTimeField(u"统计时间", primary_key=True, auto_now=True)
    warning_runtime = models.DateTimeField(u"统计时间", primary_key=True)
    warning_interface_success1 = models.DecimalField(u"接口调用成功率", max_digits=5, decimal_places=2)
    warning_interface_success2 = models.DecimalField(u"接口被调用成功率", max_digits=5, decimal_places=2)
    warning_service_success = models.DecimalField(u"业务处理成功率", max_digits=5, decimal_places=2)
    warning_query_success = models.DecimalField(u"业务查询成功率", max_digits=5, decimal_places=2)

    def __unicode__(self):
        return self.warning_runtime

    class Meta:
        verbose_name = u"KPI指标（PBOSS）"
        verbose_name_plural = verbose_name
        ordering = ['warning_runtime']
        db_table = 'warning_pboss_kpi'