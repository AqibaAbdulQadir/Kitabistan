import time
import random
import os
import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PaymentTransaction
from .serializers import PaymentSerializer, ProcessPaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentSerializer

    # ──────────────────────────────────────────────
    # POST /api/payments/process/
    # ─────────────────────────────────────────────-

    @action(detail=False, methods=['post'])
    def process_payment(self, request):
        serializer = ProcessPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order_id = serializer.validated_data['order_id']
        user_id = serializer.validated_data['user_id']
        amount = serializer.validated_data['amount']
        payment_method = serializer.validated_data.get('payment_method', 'credit_card')

        # Create transaction
        transaction = PaymentTransaction.objects.create(
            order_id=order_id,
            user_id=user_id,
            amount=amount,
            payment_method=payment_method,
            status='completed'
        )

        # Update order status to confirmed
        order_service_url = os.environ.get('ORDER_SERVICE_URL', 'http://order-service:8003')
        
        try:
            requests.patch(
                f'{order_service_url}/api/orders/{order_id}/update_status/',
                json={'order_status': 'confirmed'}
            )
        except Exception:
            pass

        return Response(PaymentSerializer(transaction).data, status=status.HTTP_201_CREATED)
    # ──────────────────────────────────────────────
    # GET /api/payments/order/{order_id}/
    # ──────────────────────────────────────────────
    @action(detail=False, methods=['get'])
    def by_order(self, request):
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response(
                {'error': 'order_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        payments = PaymentTransaction.objects.filter(order_id=order_id)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

    # ──────────────────────────────────────────────
    # GET /api/payments/health/
    # ──────────────────────────────────────────────
    @action(detail=False, methods=['get'])
    def health(self, request):
        return Response({'service': 'payment-service', 'status': 'healthy'})