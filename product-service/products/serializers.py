from rest_framework import serializers
from .models import Category, Book
import re


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def validate_name(self, value):
        if not re.match(r'^[A-Za-z ]+$', value):
            raise serializers.ValidationError("Category must contain only letters and spaces")
        return value


class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', 'stock', 'in_stock', 'category', 'category_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'in_stock']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value


class StockUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()

    def validate_quantity(self, value):
        book_id = self.context.get('book_id')
        book = Book.objects.get(id=book_id)
        if book.stock - value < 0:
            raise serializers.ValidationError("Insufficient stock")
        return value