# Generated by Django 2.1 on 2018-09-19 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_auto_20180912_2215'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='finished_onboarding',
            field=models.BooleanField(default=False),
        ),
    ]
