# Generated by Django 4.2.6 on 2023-10-23 11:24

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('date_added', models.DateField(auto_now_add=True)),
            ],
            options={
                'ordering': ['date_added'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(blank=True, max_length=255, null=True)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('category_image', models.ImageField(blank=True, null=True, upload_to='photos/categories')),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('product_name', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=255, null=True, unique=True)),
                ('description', models.TextField(blank=True, max_length=255, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('product_image', models.ImageField(blank=True, null=True, upload_to='photos/products')),
                ('stock', models.IntegerField(blank=True, null=True)),
                ('is_available', models.BooleanField(default=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.category')),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.product')),
            ],
            options={
                'ordering': ['product'],
            },
        ),
    ]
