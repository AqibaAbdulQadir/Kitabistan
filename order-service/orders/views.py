from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer, CreateOrderSerializer, UpdateOrderStatusSerializer
)
import os
import requests
from .circuit_breaker import CircuitBreaker
from .backoff import call_with_backoff

product_cb = CircuitBreaker('product-service', failure_threshold=3, recovery_timeout=60)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    # ──────────────────────────────────────────────
    # POST /api/orders/
    # ──────────────────────────────────────────────

    @action(detail=False, methods=['post'])
    def create_order(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_id = serializer.validated_data['user_id']
        items_data = serializer.validated_data['items']
        shipping_address = serializer.validated_data.get('shipping_address', '')

        if not items_data:
            return Response(
                {'error': 'Order must contain at least one item'},
                status=status.HTTP_400_BAD_REQUEST
            )

        product_service_url = os.environ.get(
            'PRODUCT_SERVICE_URL',
            'http://product-service:8004'
        )

        # Step 1: Verify stock for ALL items before reserving
        for item in items_data:
            product_id = item['product_id']
            quantity = item['quantity']

            try:
                # Use circuit breaker + exponential backoff
                resp = product_cb.call(
                    lambda pid=product_id: call_with_backoff(
                        lambda: requests.get(
                            f'{product_service_url}/api/books/{pid}/',
                            timeout=10
                        ),
                        max_retries=3,
                        base_delay=1,
                        max_delay=10
                    )
                )
                
                if resp.status_code != 200:
                    return Response(
                        {'error': f'Product {product_id} not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                book = resp.json()
                if book['stock'] < quantity:
                    return Response(
                        {'error': f'Insufficient stock for "{book["title"]}". Available: {book["stock"]}, Requested: {quantity}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            except Exception as e:
                return Response(
                    {
                        'error': f'Product Service unavailable: {str(e)}',
                        'circuit_status': product_cb.get_status()
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
                

            except requests.exceptions.ConnectionError:
                return Response(
                    {'error': 'Product Service unavailable'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

        # Step 2: All items OK — now reserve stock
        for item in items_data:
            try:
                requests.patch(
                    f'{product_service_url}/api/books/{item["product_id"]}/update_stock/',
                    json={'quantity': item['quantity']}
                )
            except Exception:
                return Response(
                    {'error': f'Failed to reserve stock for product {item["product_id"]}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Step 3: Create order
        total_price = 0
        order_items = []

        for item in items_data:
            product_price = float(item['product_price'])
            quantity = item['quantity']
            total_price += product_price * quantity
            order_items.append(OrderItem(
                product_id=item['product_id'],
                product_name=item['product_name'],
                product_price=product_price,
                quantity=quantity
            ))

        order = Order.objects.create(
            user_id=user_id,
            total_price=total_price,
            shipping_address=shipping_address
        )

        for item in order_items:
            item.order = order
        OrderItem.objects.bulk_create(order_items)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    # ──────────────────────────────────────────────
    # GET /api/orders/my_orders/?user_id=1
    # ──────────────────────────────────────────────
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        orders = Order.objects.filter(user_id=user_id)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    # ──────────────────────────────────────────────
    # GET /api/orders/  (admin: all orders)
    # ──────────────────────────────────────────────
    @action(detail=False, methods=['get'])
    def all_orders(self, request):
        """List all orders — admin endpoint"""
        orders = Order.objects.all()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    # ──────────────────────────────────────────────
    # PATCH /api/orders/{id}/update_status/
    # ──────────────────────────────────────────────
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = UpdateOrderStatusSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order.order_status = serializer.validated_data['order_status']
        order.save()

        return Response(OrderSerializer(order).data)
    
    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        """Cancel order and restore stock"""
        order = self.get_object()
        
        if order.order_status in ['delivered', 'cancelled']:
            return Response(
                {'error': 'Cannot cancel this order'},
                status=status.HTTP_400_BAD_REQUEST
            )

        product_service_url = os.environ.get('PRODUCT_SERVICE_URL', 'http://product-service:8004')

        # Restore stock
        for item in order.items.all():
            try:
                requests.patch(
                    f'{product_service_url}/api/books/{item.product_id}/restore_stock/',
                    json={'quantity': item.quantity}
                )
            except Exception:
                pass

        order.order_status = 'cancelled'
        order.save()

        return Response(OrderSerializer(order).data)
    
    @action(detail=False, methods=['get'])
    def circuit_status(self, request):
        return Response({
            'product_service': product_cb.get_status(),
        })