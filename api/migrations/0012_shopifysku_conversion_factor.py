# Generated by Django 2.1 on 2018-08-22 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20180820_2137'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopifysku',
            name='conversion_factor',
            field=models.DecimalField(decimal_places=6, default=1, max_digits=10),
        ),
    ]