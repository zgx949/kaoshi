# Generated by Django 3.2.5 on 2021-07-21 03:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ccenpx', '0003_cdkey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cdkey',
            name='cdk',
            field=models.CharField(max_length=255, verbose_name='卡密'),
        ),
        migrations.AlterField(
            model_name='cdkey',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ccenpx.user', verbose_name='使用人'),
        ),
    ]
