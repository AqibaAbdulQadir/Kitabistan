from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)

    description = models.TextField(blank=True)  
    image = models.ImageField(upload_to='books/', null=True, blank=True) 
    image_url = models.URLField(blank=True, null=True) 

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def in_stock(self):
        return self.stock > 0
image_url = models.URLField(blank=True, null=True)