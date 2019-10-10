# Generated by Django 2.2.5 on 2019-10-05 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CN171_background', '0003_auto_20190930_1111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bgtasklog',
            name='bg_id',
            field=models.IntegerField(verbose_name='后台id'),
        ),
        migrations.AlterField(
            model_name='bgtasklog',
            name='bg_log_dir',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='详细日志'),
        ),
        migrations.AlterField(
            model_name='bgtasklog',
            name='bg_log_id',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='日志id'),
        ),
        migrations.AlterField(
            model_name='bgtasklog',
            name='bg_operation',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='操作类型'),
        ),
        migrations.AlterField(
            model_name='bgtasklog',
            name='bg_operation_time',
            field=models.DateTimeField(verbose_name='操作时间'),
        ),
        migrations.AlterField(
            model_name='bgtasklog',
            name='bg_operation_user',
            field=models.CharField(blank=True, max_length=56, null=True, verbose_name='操作人员'),
        ),
        migrations.AlterField(
            model_name='bgtasklog',
            name='bg_opr_result',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='操作结果'),
        ),
        migrations.AlterField(
            model_name='bgtaskmanagement',
            name='bg_id',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='后台id'),
        ),
        migrations.AlterField(
            model_name='bgtaskmanagement',
            name='bg_insert_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='录入时间'),
        ),
        migrations.AlterField(
            model_name='bgtaskmanagement',
            name='bg_task_query',
            field=models.TextField(verbose_name='查询脚本'),
        ),
        migrations.AlterField(
            model_name='bgtaskmanagement',
            name='bg_task_restart',
            field=models.TextField(verbose_name='重启脚本'),
        ),
        migrations.AlterField(
            model_name='bgtaskmanagement',
            name='bg_task_start',
            field=models.TextField(verbose_name='启动脚本'),
        ),
        migrations.AlterField(
            model_name='bgtaskmanagement',
            name='bg_task_stop',
            field=models.TextField(verbose_name='停止脚本'),
        ),
    ]