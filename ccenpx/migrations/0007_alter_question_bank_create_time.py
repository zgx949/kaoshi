# Generated by Django 3.2.5 on 2021-07-22 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ccenpx', '0006_alter_question_bank_create_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question_bank',
            name='create_time',
            field=models.DateTimeField(auto_created=True, blank=True, null=True, verbose_name='创建时间'),
        ),
    ]