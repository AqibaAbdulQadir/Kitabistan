from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import (
    CartSerializer, CartItemSerializer,
    AddItemSerializer, UpdateItemSerializer
)


class CartViewSet(viewsets.GenericViewSet):
    """
    One cart per user. Endpoints operate on the user's cart.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_cart(self, user_id):
        """Get or create a cart for the given user_id"""
        cart, _ = Cart.objects.get_or_create(user_id=user_id)
        return cart

    # ──────────────────────────────────────────────
    # GET /api/cart/?user_id=1
    # ──────────────────────────────────────────────
    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = self.get_cart(user_id)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    # ──────────────────────────────────────────────
    # POST /api/cart/add/
    # ──────────────────────────────────────────────
    @action(detail=False, methods=['post'])
    def add(self, request):
        serializer = AddItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_id = serializer.validated_data['user_id']
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data.get('quantity', 1)

        cart = self.get_cart(user_id)

        # Check if item already exists in cart
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            defaults={
                'product_name': serializer.validated_data.get('product_name', ''),
                'product_price': serializer.validated_data.get('product_price', 0),
                'quantity': quantity,
            }
        )

        if not created:
            # Item exists — increase quantity
            item.quantity += quantity
            item.save()

        return Response(CartItemSerializer(item).data, status=status.HTTP_200_OK)

    # ──────────────────────────────────────────────
    # PUT /api/cart/update/
    # ──────────────────────────────────────────────
    @action(detail=False, methods=['put'])
    def update_item(self, request):
        serializer = UpdateItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        quantity = serializer.validated_data['quantity']

        cart = get_object_or_404(Cart, user_id=user_id)

        if quantity == 0:
            # Remove item if quantity is 0
            CartItem.objects.filter(cart=cart, product_id=product_id).delete()
            return Response({'message': 'Item removed'}, status=status.HTTP_200_OK)

        item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        item.quantity = quantity
        item.save()

        return Response(CartItemSerializer(item).data)

    # ──────────────────────────────────────────────
    # DELETE /api/cart/remove/?user_id=1&product_id=5
    # ──────────────────────────────────────────────
    @action(detail=False, methods=['delete'])
    def remove(self, request):
        user_id = request.query_params.get('user_id')
        product_id = request.query_params.get('product_id')

        if not user_id or not product_id:
            return Response(
                {'error': 'user_id and product_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = get_object_or_404(Cart, user_id=user_id)
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()

        return Response({'message': 'Item removed'}, status=status.HTTP_200_OK)

    # ──────────────────────────────────────────────
    # DELETE /api/cart/clear/?user_id=1
    # ──────────────────────────────────────────────
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = self.get_cart(user_id)
        cart.items.all().delete()

        return Response({'message': 'Cart cleared'}, status=status.HTTP_200_OK)