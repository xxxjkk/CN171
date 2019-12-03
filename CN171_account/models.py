from django.db import models

# Create your models here.
class User(models.Model):
    # '''用户表'''

    acc_user_id = models.AutoField(u"用户id",primary_key=True)

    acc_user_name = models.CharField(u"用户名",max_length=128, unique=True)
    acc_user_CNname = models.CharField(u"用户中文名",max_length=128, unique=True)

    acc_user_password = models.CharField(u"密码",max_length=256)

    acc_user_status = models.CharField(u"用户状态",max_length=30, null=True, blank=True)
    acc_user_createtime = models.DateTimeField(u"用户创建时间",auto_now_add=True)
    acc_user_email = models.EmailField(u"邮箱",null=True, blank=True)
    acc_user_mobile = models.CharField(u"电话",max_length=30, null=True, blank=True)
    acc_last_log_time = models.DateTimeField(u"最后登录时间",null=True, blank=True)
    acc_user_operation = models.CharField(u"用户最近操作",max_length=128,null=True, blank=True)
    roles = models.ManyToManyField(verbose_name='拥有的所有角色', to='Role')
    def __str__(self):
        return self.acc_user_name

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['acc_user_id']
        db_table = "acc_user"

#角色model
class Role(models.Model):
    """
    角色表
    """
    title = models.CharField(verbose_name='角色名称', max_length=32)
    permissions = models.ManyToManyField(verbose_name='拥有的所有权限', to='Permission')

    def __str__(self):
        return self.title
    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'
        db_table = "acc_role"


class Permission(models.Model):
    """
    权限表
    """
    url = models.CharField(verbose_name='含正则的URL', max_length=256)
    title = models.CharField(verbose_name='标题', max_length=32)
    menu = models.ForeignKey(verbose_name='所属菜单', to="Menu", on_delete=models.CASCADE, null=True)
    parent = models.ForeignKey('Permission', null=True, blank=True, verbose_name="二级菜单归属", on_delete=models.CASCADE)
    icon = models.CharField(verbose_name='图标', max_length=32, blank=True, null=True)
    name = models.CharField(verbose_name='url别名', max_length=32, default="")
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = '权限'
        verbose_name_plural = '权限'
        db_table = "acc_permission"

 # 新增一个菜单表
class Menu(models.Model):
    title = models.CharField(max_length=32, verbose_name='菜单')
    icon = models.CharField(max_length=32, verbose_name='图标', null=True, blank=True)
    url = models.CharField(verbose_name='含正则的URL', max_length=32,null=True, blank=True)
    classid = models.CharField(max_length=32, verbose_name='样式id', null=True, blank=True)
    weight = models.IntegerField(default=1, verbose_name='权重')
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = '菜单'
        verbose_name_plural = '菜单'
        db_table = "acc_menu"



