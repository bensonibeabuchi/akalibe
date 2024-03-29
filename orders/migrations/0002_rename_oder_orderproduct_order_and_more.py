# Generated by Django 4.2.6 on 2024-01-19 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderproduct',
            old_name='oder',
            new_name='order',
        ),
        migrations.RenameField(
            model_name='orderproduct',
            old_name='sixe',
            new_name='size',
        ),
        migrations.AlterField(
            model_name='order',
            name='address_line_1',
            field=models.CharField(blank=True, max_length=90, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='address_line_2',
            field=models.CharField(blank=True, max_length=90, null=True),
        ),
    ]
