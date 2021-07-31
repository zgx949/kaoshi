# Generated by Django 3.2.5 on 2021-07-22 05:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ccenpx', '0004_auto_20210721_1135'),
    ]

    operations = [
        migrations.CreateModel(
            name='Classname',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='分类名称')),
            ],
        ),
        migrations.AlterField(
            model_name='question_bank',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.IntegerField(choices=[(-1, '异常'), (0, '未开始'), (1, '已考试未交卷'), (2, '已考试')], default=0, null=True, verbose_name='当前状态'),
        ),
        migrations.AlterField(
            model_name='user',
            name='classname',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ccenpx.classname', verbose_name='分类'),
        ),
    ]