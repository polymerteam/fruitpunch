# Generated by Django 2.1 on 2018-08-13 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20180813_1857'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('shopify_access_token', models.TextField(null=True)),
                ('shopify_store_name', models.CharField(max_length=50, null=True)),
            ],
        ),
    ]
