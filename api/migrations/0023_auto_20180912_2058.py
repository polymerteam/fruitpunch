# Generated by Django 2.1 on 2018-09-12 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_auto_20180911_2326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopifysku',
            name='variant_id',
            field=models.CharField(max_length=50),
        ),
    ]
