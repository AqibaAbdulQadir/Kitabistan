from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Book, Category
from .serializers import BookSerializer, CategorySerializer, StockUpdateSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category']
    search_fields = ['title', 'author']

    @action(detail=True, methods=['patch'])
    def update_stock(self, request, pk=None):
        """Reduce stock after order: PATCH /api/books/{id}/update_stock/"""
        book = self.get_object()
        serializer = StockUpdateSerializer(data=request.data, context={'book_id': book.id})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        quantity = serializer.validated_data['quantity']
        book.stock -= quantity
        book.save()

        return Response(BookSerializer(book).data)

    @action(detail=False, methods=['get'])
    def health(self, request):
        return Response({'service': 'product-service', 'status': 'healthy'})
    
    @action(detail=True, methods=['patch'])
    def restore_stock(self, request, pk=None):
        """Restore stock when payment fails"""
        book = self.get_object()
        quantity = int(request.data.get('quantity', 0))
        book.stock += quantity
        book.save()
        return Response(BookSerializer(book).data)