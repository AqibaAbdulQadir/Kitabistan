from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User


class CartTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.base_url = '/api/cart'

    # ──────────────────────────────────────────────
    # MY CART TESTS
    # ──────────────────────────────────────────────

    def test_my_cart_empty(self):
        """New user gets empty cart"""
        response = self.client.get(f'{self.base_url}/my_cart/?user_id=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['items'], [])
        self.assertEqual(response.data['total_price'], 0)
        self.assertEqual(response.data['total_items'], 0)

    def test_my_cart_missing_user_id(self):
        """user_id is required"""
        response = self.client.get(f'{self.base_url}/my_cart/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ──────────────────────────────────────────────
    # ADD ITEM TESTS
    # ──────────────────────────────────────────────

    def test_add_item_new(self):
        """Add a new item to cart"""
        response = self.client.post(f'{self.base_url}/add/', {
            'user_id': 1,
            'product_id': 1,
            'product_name': 'Atomic Habits',
            'product_price': 3000,
            'quantity': 2,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['product_name'], 'Atomic Habits')
        self.assertEqual(response.data['quantity'], 2)

    def test_add_item_existing_increases_quantity(self):
        """Adding same product increases quantity"""
        # First add
        self.client.post(f'{self.base_url}/add/', {
            'user_id': 1, 'product_id': 1,
            'product_name': 'Book', 'product_price': 1000, 'quantity': 2,
        })
        # Second add
        response = self.client.post(f'{self.base_url}/add/', {
            'user_id': 1, 'product_id': 1,
            'product_name': 'Book', 'product_price': 1000, 'quantity': 3,
        })
        self.assertEqual(response.data['quantity'], 5)

    def test_add_item_missing_user_id(self):
        """user_id is required"""
        response = self.client.post(f'{self.base_url}/add/', {
            'product_id': 1,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_item_missing_product_id(self):
        """product_id is required"""
        response = self.client.post(f'{self.base_url}/add/', {
            'user_id': 1,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ──────────────────────────────────────────────
    # UPDATE ITEM TESTS
    # ──────────────────────────────────────────────

    def test_update_item_quantity(self):
        """Update quantity of existing item"""
        self.client.post(f'{self.base_url}/add/', {
            'user_id': 1, 'product_id': 1,
            'product_name': 'Book', 'product_price': 1000, 'quantity': 2,
        })
        response = self.client.put(f'{self.base_url}/update_item/', {
            'user_id': 1, 'product_id': 1, 'quantity': 7,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 7)

    def test_update_item_to_zero_removes(self):
        """Setting quantity to 0 removes the item"""
        self.client.post(f'{self.base_url}/add/', {
            'user_id': 1, 'product_id': 1,
            'product_name': 'Book', 'product_price': 1000, 'quantity': 2,
        })
        response = self.client.put(f'{self.base_url}/update_item/', {
            'user_id': 1, 'product_id': 1, 'quantity': 0,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Item removed')

        # Verify cart is empty
        cart_response = self.client.get(f'{self.base_url}/my_cart/?user_id=1')
        self.assertEqual(cart_response.data['items'], [])

    # ──────────────────────────────────────────────
    # REMOVE ITEM TESTS
    # ──────────────────────────────────────────────

    def test_remove_item(self):
        """Remove a specific item"""
        self.client.post(f'{self.base_url}/add/', {
            'user_id': 1, 'product_id': 1,
            'product_name': 'Book', 'product_price': 1000, 'quantity': 1,
        })
        response = self.client.delete(
            f'{self.base_url}/remove/?user_id=1&product_id=1'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_remove_missing_params(self):
        """Both user_id and product_id are required"""
        response = self.client.delete(f'{self.base_url}/remove/?user_id=1')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ──────────────────────────────────────────────
    # CLEAR CART TESTS
    # ──────────────────────────────────────────────

    def test_clear_cart(self):
        """Clear all items"""
        self.client.post(f'{self.base_url}/add/', {
            'user_id': 1, 'product_id': 1,
            'product_name': 'Book', 'product_price': 1000, 'quantity': 1,
        })
        response = self.client.delete(f'{self.base_url}/clear/?user_id=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        cart_response = self.client.get(f'{self.base_url}/my_cart/?user_id=1')
        self.assertEqual(cart_response.data['items'], [])

    # ──────────────────────────────────────────────
    # CART TOTAL TESTS
    # ──────────────────────────────────────────────

    def test_cart_total_calculation(self):
        """Total price and items are calculated correctly"""
        self.client.post(f'{self.base_url}/add/', {
            'user_id': 1, 'product_id': 1,
            'product_name': 'Book A', 'product_price': 1000, 'quantity': 3,
        })
        self.client.post(f'{self.base_url}/add/', {
            'user_id': 1, 'product_id': 2,
            'product_name': 'Book B', 'product_price': 500, 'quantity': 4,
        })
        response = self.client.get(f'{self.base_url}/my_cart/?user_id=1')

        # 1000*3 + 500*4 = 3000 + 2000 = 5000
        self.assertEqual(response.data['total_price'], 5000)
        # 3 + 4 = 7
        self.assertEqual(response.data['total_items'], 7)

    # ──────────────────────────────────────────────
    # DATA INTEGRITY TEST
    # ──────────────────────────────────────────────

    def test_carts_are_isolated_per_user(self):
        """User 1's cart doesn't affect User 2's cart"""
        self.client.post(f'{self.base_url}/add/', {
            'user_id': 1, 'product_id': 1,
            'product_name': 'Book', 'product_price': 1000, 'quantity': 1,
        })
        response = self.client.get(f'{self.base_url}/my_cart/?user_id=2')
        self.assertEqual(response.data['items'], [])

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

    def test_admin_carts_list(self):
        response = self.client.get('/admin/cart/cart/')
        self.assertEqual(response.status_code, 200)

    def test_admin_cart_items_list(self):
        response = self.client.get('/admin/cart/cartitem/')
        self.assertEqual(response.status_code, 200)