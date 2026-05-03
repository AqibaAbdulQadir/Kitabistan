from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book, Category
from .serializers import BookSerializer, CategorySerializer, StockUpdateSerializer


# -------------------------------
# Category ViewSet
# -------------------------------
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# -------------------------------
# Book ViewSet
# -------------------------------
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('category').all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category']
    search_fields = ['title', 'author']

    # -------------------------------
    # Reduce Stock
    # -------------------------------
    @action(detail=True, methods=['patch'])
    def update_stock(self, request, pk=None):
        book = self.get_object()

        serializer = StockUpdateSerializer(
            data=request.data,
            context={'book_id': book.id}
        )
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data['quantity']
        book.stock -= quantity
        book.save()

        return Response(
            BookSerializer(book, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    # -------------------------------
    # Restore Stock
    # -------------------------------
    @action(detail=True, methods=['patch'])
    def restore_stock(self, request, pk=None):
        book = self.get_object()

        serializer = StockUpdateSerializer(
            data=request.data,
            context={'book_id': book.id}
        )
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data['quantity']
        book.stock += quantity
        book.save()

        return Response(
            BookSerializer(book, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    # -------------------------------
    # Health Check Endpoint
    # -------------------------------
    @action(detail=False, methods=['get'])
    def health(self, request):
        return Response({
            'service': 'product-service',
            'status': 'healthy'
        })