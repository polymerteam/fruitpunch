# Generated by Django 2.1 on 2018-08-12 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20180812_1923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
