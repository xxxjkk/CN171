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
