from django.db import models
from django.urls import reverse
import uuid


class Category(models.Model):
    category_name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    category_image = models.ImageField(
        upload_to='photos/categories', null=True, blank=True)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = ('Categories')


class Product(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product_name = models.CharField(
        max_length=255, null=True, blank=True, unique=True)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    product_image = models.ImageField(
        upload_to='photos/products', null=True, blank=True)
    stock = models.IntegerField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name

    def get_url(self):
        return reverse('product-detail', args=[self.category.slug, self.slug])

    class Meta:
        ordering = ('product_name',)


class VariationManager(models.Manager):
    def colors(self):
        return self.filter(variation_category='color', is_active=True)

    def sizes(self):
        return self.filter(variation_category='size', is_active=True)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(
        max_length=255, choices=(('color', 'Color'), ('size', 'Size')),)
    variation_value = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value

    class Meta:
        ordering = ['product__product_name']


class Cart(models.Model):
    cart_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product.product_name

    def get_product_name(self):
        return self.product.product_name

    class Meta:
        ordering = ['product__product_name']
