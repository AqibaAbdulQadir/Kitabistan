import time
import random
import os
import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PaymentTransaction
from .serializers import PaymentSerializer, ProcessPaymentSerializer
from .circuit_breaker import CircuitBreaker
from .backoff import call_with_backoff

# Circuit breakers for external calls
order_cb = CircuitBreaker('order-service', failure_threshold=3, recovery_timeout=60)
product_cb = CircuitBreaker('product-service', failure_threshold=3, recovery_timeout=60)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=False, methods=['post'])
    def process_payment(self, request):
        serializer = ProcessPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order_id = serializer.validated_data['order_id']
        user_id = serializer.validated_data['user_id']
        amount = serializer.validated_data['amount']
        payment_method = serializer.validated_data.get('payment_method', 'credit_card')

        order_service_url = os.environ.get('ORDER_SERVICE_URL', 'http://order-service:8003')
        product_service_url = os.environ.get('PRODUCT_SERVICE_URL', 'http://product-service:8004')

        # Step 1: Update order status FIRST
        try:
            order_cb.call(
                lambda: call_with_backoff(
                    lambda: requests.patch(
                        f'{order_service_url}/api/orders/{order_id}/update_status/',
                        json={'order_status': 'confirmed'},
                        timeout=10
                    ),
                    max_retries=3, base_delay=1
                )
            )
        except Exception as e:
            return Response({
                'error': 'Failed to confirm order',
                'detail': str(e),
                'circuit_status': order_cb.get_status()
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Step 2: Only create transaction AFTER order is confirmed
        transaction = PaymentTransaction.objects.create(
            order_id=order_id,
            user_id=user_id,
            amount=amount,
            payment_method=payment_method,
            status='completed'
        )

        # Step 3: Reduce stock (best effort)
        try:
            order_resp = requests.get(f'{order_service_url}/api/orders/{order_id}/', timeout=10)
            if order_resp.status_code == 200:
                order = order_resp.json()
                for item in order.get('items', []):
                    pid = item['product_id']
                    qty = item['quantity']
                    product_cb.call(
                        lambda pid=pid, qty=qty: call_with_backoff(
                            lambda: requests.patch(
                                f'{product_service_url}/api/books/{pid}/update_stock/',
                                json={'quantity': qty},
                                timeout=10
                            ),
                            max_retries=3, base_delay=1
                        )
                    )
        except Exception as e:
            print(f"Stock update failed: {e}", flush=True)

        return Response(PaymentSerializer(transaction).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def by_order(self, request):
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response({'error': 'order_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        payments = PaymentTransaction.objects.filter(order_id=order_id)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def health(self, request):
        return Response({'service': 'payment-service', 'status': 'healthy'})
    
    @action(detail=False, methods=['get'])
    def circuit_status(self, request):
        return Response({
            'order_service': order_cb.get_status(),
            'product_service': product_cb.get_status(),
        })