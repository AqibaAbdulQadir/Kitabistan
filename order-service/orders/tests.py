from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User


class OrderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.base_url = '/api/orders'
        self.valid_order = {
            'user_id': 1,
            'items': [
                {'product_id': 1, 'product_name': 'Book A', 'product_price': 1000, 'quantity': 2},
                {'product_id': 2, 'product_name': 'Book B', 'product_price': 500, 'quantity': 3},
            ],
            'shipping_address': '123 Main St, Karachi'
        }

    # ──────────────────────────────────────────────
    # CREATE ORDER TESTS
    # ──────────────────────────────────────────────

    def test_create_order_success(self):
        """Create a valid order"""
        response = self.client.post(
            f'{self.base_url}/create_order/',
            self.valid_order,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user_id'], 1)
        self.assertEqual(len(response.data['items']), 2)
        # 1000*2 + 500*3 = 2000 + 1500 = 3500
        self.assertEqual(response.data['total_price'], '3500.00')
        self.assertEqual(response.data['order_status'], 'pending')
        self.assertEqual(response.data['payment_status'], 'pending')

    def test_create_order_empty_items(self):
        """Order with no items should fail"""
        response = self.client.post(
            f'{self.base_url}/create_order/',
            {'user_id': 1, 'items': []},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_missing_user_id(self):
        """user_id is required"""
        response = self.client.post(
            f'{self.base_url}/create_order/',
            {'items': [{'product_id': 1, 'product_name': 'Book', 'product_price': 500, 'quantity': 1}]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_missing_items(self):
        """items list is required"""
        response = self.client.post(
            f'{self.base_url}/create_order/',
            {'user_id': 1},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_invalid_product_price(self):
        """product_price must be a number"""
        response = self.client.post(
            f'{self.base_url}/create_order/',
            {'user_id': 1, 'items': [{'product_id': 1, 'product_name': 'Book', 'product_price': 'free', 'quantity': 1}]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ──────────────────────────────────────────────
    # MY ORDERS TESTS
    # ──────────────────────────────────────────────

    def test_my_orders_returns_user_orders(self):
        """Only returns orders for the specified user"""
        # Create order for user 1
        self.client.post(f'{self.base_url}/create_order/', self.valid_order, format='json')

        # Create order for user 2
        self.client.post(
            f'{self.base_url}/create_order/',
            {'user_id': 2, 'items': [{'product_id': 3, 'product_name': 'Book C', 'product_price': 300, 'quantity': 1}]},
            format='json'
        )

        # Get user 1's orders
        response = self.client.get(f'{self.base_url}/my_orders/?user_id=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Get user 2's orders
        response = self.client.get(f'{self.base_url}/my_orders/?user_id=2')
        self.assertEqual(len(response.data), 1)

        # User 3 has no orders
        response = self.client.get(f'{self.base_url}/my_orders/?user_id=3')
        self.assertEqual(response.data, [])

    def test_my_orders_missing_user_id(self):
        """user_id is required"""
        response = self.client.get(f'{self.base_url}/my_orders/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ──────────────────────────────────────────────
    # UPDATE STATUS TESTS
    # ──────────────────────────────────────────────

    def test_update_order_status(self):
        """Update order status"""
        create_response = self.client.post(
            f'{self.base_url}/create_order/', self.valid_order, format='json'
        )
        order_id = create_response.data['id']

        response = self.client.patch(
            f'{self.base_url}/{order_id}/update_status/',
            {'order_status': 'confirmed'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_status'], 'confirmed')

    def test_update_invalid_status(self):
        """Invalid status should fail"""
        create_response = self.client.post(
            f'{self.base_url}/create_order/', self.valid_order, format='json'
        )
        order_id = create_response.data['id']

        response = self.client.patch(
            f'{self.base_url}/{order_id}/update_status/',
            {'order_status': 'invalid_status'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_nonexistent_order(self):
        """Updating non-existent order returns 404"""
        response = self.client.patch(
            f'{self.base_url}/999/update_status/',
            {'order_status': 'confirmed'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ──────────────────────────────────────────────
    # ALL ORDERS TEST
    # ──────────────────────────────────────────────

    def test_all_orders(self):
        """Returns all orders regardless of user"""
        self.client.post(f'{self.base_url}/create_order/', self.valid_order, format='json')
        self.client.post(
            f'{self.base_url}/create_order/',
            {'user_id': 2, 'items': [{'product_id': 3, 'product_name': 'Book C', 'product_price': 300, 'quantity': 1}]},
            format='json'
        )

        response = self.client.get(f'{self.base_url}/all_orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    # ──────────────────────────────────────────────
    # DATA INTEGRITY TESTS
    # ──────────────────────────────────────────────

    def test_order_total_calculation(self):
        """Total price is sum of item subtotals"""
        response = self.client.post(
            f'{self.base_url}/create_order/',
            {'user_id': 1, 'items': [
                {'product_id': 1, 'product_name': 'X', 'product_price': 100, 'quantity': 5},
                {'product_id': 2, 'product_name': 'Y', 'product_price': 50, 'quantity': 2},
            ]},
            format='json'
        )
        # 100*5 + 50*2 = 600
        self.assertEqual(response.data['total_price'], '600.00')

    def test_order_defaults(self):
        """New order has correct default values"""
        response = self.client.post(f'{self.base_url}/create_order/', self.valid_order, format='json')
        self.assertEqual(response.data['order_status'], 'pending')
        self.assertEqual(response.data['payment_status'], 'pending')
        self.assertIn('created_at', response.data)

    def test_shipping_address_optional(self):
        """Order can be created without shipping address"""
        response = self.client.post(
            f'{self.base_url}/create_order/',
            {'user_id': 1, 'items': [{'product_id': 1, 'product_name': 'Book', 'product_price': 500, 'quantity': 1}]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['shipping_address'], '')


class AdminTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='root',
            email='aqibaabdulqadir@gmail.com',
            password='aqiba123'
        )
        self.client.login(username='root', password='aqiba123')


    def test_admin_accessible(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_admin_orders_list(self):
        response = self.client.get('/admin/orders/order/')
        self.assertEqual(response.status_code, 200)

    def test_admin_order_items_list(self):
        response = self.client.get('/admin/orders/orderitem/')
        self.assertEqual(response.status_code, 200)