# Generated by Django 2.1 on 2018-08-12 00:11

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('i', 'in progress'), ('c', 'completed')], default='i', max_length=1)),
                ('amount', models.DecimalField(decimal_places=3, default=1, max_digits=10)),
                ('started_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('completed_at', models.DateTimeField(blank=True)),
                ('is_trashed', models.BooleanField(db_index=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name='BatchItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=3, default=1, max_digits=10)),
                ('is_trashed', models.BooleanField(db_index=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=3, default=1, max_digits=10)),
                ('is_trashed', models.BooleanField(db_index=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=20)),
                ('icon', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('unit', models.CharField(default='kilogram', max_length=20)),
                ('dollar_value', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('is_trashed', models.BooleanField(db_index=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ReceivedInventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=3, default=1, max_digits=10)),
                ('received_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('is_trashed', models.BooleanField(db_index=True, default=False)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_inventory', to='api.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_batch_size', models.DecimalField(decimal_places=3, default=1, max_digits=10)),
                ('is_trashed', models.BooleanField(db_index=True, default=False)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to='api.Product')),
            ],
        ),
        migrations.AddField(
            model_name='ingredient',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='api.Product'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='api.Recipe'),
        ),
        migrations.AddField(
            model_name='batchitem',
            name='active_recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='batch_items', to='api.Recipe'),
        ),
        migrations.AddField(
            model_name='batchitem',
            name='batch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='batch_items', to='api.Batch'),
        ),
        migrations.AddField(
            model_name='batchitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='batch_items', to='api.Product'),
        ),
        migrations.AddField(
            model_name='batch',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='batches', to='api.Product'),
        ),
        migrations.AddField(
            model_name='batch',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='batches', to='api.Recipe'),
        ),
    ]