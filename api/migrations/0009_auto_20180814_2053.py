# Generated by Django 2.1 on 2018-08-14 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20180814_1931'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shopifysku',
            name='sku',
        ),
        migrations.AddField(
            model_name='shopifysku',
            name='variant_id',
            field=models.CharField(default='asdf', max_length=30, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shopifysku',
            name='variant_sku',
            field=models.CharField(max_length=50, null=True),
        ),
    ]