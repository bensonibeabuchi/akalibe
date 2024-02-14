# Generated by Django 4.2.6 on 2024-02-14 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_remove_orderproduct_variation_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='address',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='city',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='country',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='full_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='state',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]