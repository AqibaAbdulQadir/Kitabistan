from rest_framework import serializers
from .models import Category, Book
import re


# -------------------------------
# Category Serializer
# -------------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def validate_name(self, value):
        if not re.match(r'^[A-Za-z ]+$', value):
            raise serializers.ValidationError(
                "Category must contain only letters and spaces"
            )
        return value


# -------------------------------
# Book Serializer
# -------------------------------
class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    in_stock = serializers.ReadOnlyField()

    # This now accepts external image URLs
    image_url = serializers.URLField(required=False, allow_null=True)

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',
            'description',
            'image',
            'image_url',
            'price',
            'stock',
            'in_stock',
            'category',
            'category_name',
            'created_at'
        ]

        read_only_fields = [
            'id',
            'created_at',
            'in_stock',
            'category_name'
        ]

    # -------------------------------
    # Validations
    # -------------------------------
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than 0"
            )
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Stock cannot be negative"
            )
        return value


# -------------------------------
# Stock Update Serializer
# -------------------------------
class StockUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()

    def validate_quantity(self, value):
        book_id = self.context.get('book_id')

        if not book_id:
            raise serializers.ValidationError(
                "Book ID is required in context"
            )

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise serializers.ValidationError(
                "Book not found"
            )

        if book.stock - value < 0:
            raise serializers.ValidationError(
                "Insufficient stock"
            )

        return value