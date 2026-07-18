from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    description = models.TextField()

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to="products/"
    )

    featured = models.BooleanField(default=False)

    available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

# Create your models here.
