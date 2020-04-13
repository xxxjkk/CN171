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


class systemList(models.Model):
    # 系统列表
    system_id = models.AutoField(u"系统id", primary_key=True)
    system_name = models.CharField(u"系统名称", max_length=64, unique=True, null=False)

    def __unicode__(self):
        return self.system_id

    class Meta:
        verbose_name = u"系统列表"
        verbose_name_plural = verbose_name
        ordering = ['system_id']
        db_table = 'system_list'


class privilegedAccountRecord(models.Model):
    # 特权/程序账号备案记录表
    record_id = models.AutoField(u"记录id", primary_key=True)
    system_name = models.CharField(u"系统名称", max_length=64)
    resource_ip = models.CharField(u"资源ip", max_length=4096)
    resource_name = models.CharField(u"资源名称", max_length=4096)
    resource_type = models.CharField(u"资源类型", max_length=64)
    personal_account = models.CharField(u"操作账号（个人）", max_length=64)
    privileged_account = models.CharField(u"操作账号（特权/程序）", max_length=256)
    start_time = models.IntegerField(u"申请开始时间")
    end_time = models.IntegerField(u"申请结束时间")

    def __unicode__(self):
        return self.record_id

    class Meta:
        verbose_name = u"特权/程序账号备案记录表"
        verbose_name_plural = verbose_name
        ordering = ['record_id']
        db_table = 'privileged_account_record'


class privilegedAccountWithoutRecord(models.Model):
    # 使用特权/程序账号未备案记录表
    record_id = models.AutoField(u"记录id", primary_key=True)
    resource = models.CharField(u"资源ip/名称", max_length=64)
    personal_account = models.CharField(u"操作账号（个人）", max_length=64)
    privileged_account = models.CharField(u"操作账号（特权/程序）", max_length=256)
    operating_time = models.DateField(u"操作时间")

    def __unicode__(self):
        return self.record_id

    class Meta:
        verbose_name = u"使用特权/程序账号未备案记录表"
        verbose_name_plural = verbose_name
        ordering = ['record_id']
        db_table = 'privileged_account_without_record'


class hostAccountList(models.Model):
    # 主机账号列表
    account_id = models.AutoField(u"账号id", primary_key=True)
    host_ip = models.CharField(u"主机ip", max_length=64)
    host_name = models.CharField(u"主机名称", max_length=64)
    host_system = models.CharField(u"所属系统", max_length=64)
    account_name = models.CharField(u"账号名", max_length=64)
    account_group = models.CharField(u"账号所属主组", max_length=64)
    account_type = models.CharField(u"账号属性", max_length=32)
    account_4AAccount = models.CharField(u"绑定的4A主账号", max_length=256, null=True)
    is_keep = models.CharField(u"是否保留", max_length=16)
    is_in_4A = models.CharField(u"是否在4A侧存在", max_length=16)
    is_in_resource = models.CharField(u"是否在资源侧存在", max_length=16)
    is_new = models.CharField(u"是否新增账号", max_length=16)
    is_isolated = models.CharField(u"是否孤立账号", max_length=16)
    is_public = models.CharField(u"是否公共账号", max_length=16)
    is_applied = models.CharField(u"是否有开户记录", max_length=16)
    is_to_cancel = models.CharField(u"是否需销户", max_length=16)
    is_to_change = models.CharField(u"是否需变更", max_length=16)
    how_to_change = models.CharField(u"变更内容", max_length=256)

    def __unicode__(self):
        return self.account_id

    class Meta:
        verbose_name = u"主机账号列表"
        verbose_name_plural = verbose_name
        ordering = ['account_id']
        db_table = 'host_account_list'


class databaseAccountList(models.Model):
    # 数据库账号列表
    account_id = models.AutoField(u"账号id", primary_key=True)
    database_ip = models.CharField(u"数据库ip", max_length=64)
    database_name = models.CharField(u"数据库名称", max_length=64)
    database_system = models.CharField(u"所属系统", max_length=64)
    account_name = models.CharField(u"账号名", max_length=64)
    account_role = models.CharField(u"账号角色", max_length=1024)
    account_type = models.CharField(u"账号属性", max_length=32)
    account_4AAccount = models.CharField(u"绑定的4A主账号", max_length=256, null=True)
    is_keep = models.CharField(u"是否保留", max_length=16)
    is_in_4A = models.CharField(u"是否在4A侧存在", max_length=16)
    is_in_resource = models.CharField(u"是否在资源侧存在", max_length=16)
    is_new = models.CharField(u"是否新增账号", max_length=16)
    is_isolated = models.CharField(u"是否孤立账号", max_length=16)
    is_public = models.CharField(u"是否公共账号", max_length=16)
    is_applied = models.CharField(u"是否有开户记录", max_length=16)
    is_to_cancel = models.CharField(u"是否需销户", max_length=16)
    is_to_change = models.CharField(u"是否需变更", max_length=16)
    how_to_change = models.CharField(u"变更内容", max_length=256)

    def __unicode__(self):
        return self.account_id

    class Meta:
        verbose_name = u"数据库账号列表"
        verbose_name_plural = verbose_name
        ordering = ['account_id']
        db_table = 'database_account_list'

class applicationAccountList(models.Model):
    # 应用账号列表
    account_id = models.AutoField(u"账号id", primary_key=True)
    application_system = models.CharField(u"所属系统", max_length=64)
    account_name = models.CharField(u"账号名", max_length=64)
    account_role = models.CharField(u"账号角色", max_length=1024)
    account_type = models.CharField(u"账号属性", max_length=32)
    account_4AAccount = models.CharField(u"绑定的4A主账号", max_length=256, null=True)
    is_keep = models.CharField(u"是否保留", max_length=16)
    is_in_4A = models.CharField(u"是否在4A侧存在", max_length=16)
    is_in_resource = models.CharField(u"是否在资源侧存在", max_length=16)
    is_new = models.CharField(u"是否新增账号", max_length=16)
    is_isolated = models.CharField(u"是否孤立账号", max_length=16)
    is_public = models.CharField(u"是否公共账号", max_length=16)
    is_applied = models.CharField(u"是否有开户记录", max_length=16)
    is_to_cancel = models.CharField(u"是否需销户", max_length=16)
    is_to_change = models.CharField(u"是否需变更", max_length=16)
    how_to_change = models.CharField(u"变更内容", max_length=256)

    def __unicode__(self):
        return self.account_id

    class Meta:
        verbose_name = u"应用账号列表"
        verbose_name_plural = verbose_name
        ordering = ['account_id']
        db_table = 'application_account_list'