from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import PaymentTransaction
from django.contrib.auth.models import User
from unittest.mock import patch


class PaymentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payment = {
            'order_id': 1,
            'user_id': 1,
            'amount': 3500,
            'payment_method': 'credit_card'
        }

    # ──────────────────────────────────────────────
    # PROCESS PAYMENT TESTS
    # ──────────────────────────────────────────────

    @patch('payments.views.requests.get')
    @patch('payments.views.requests.patch')
    def test_process_payment_success(self, mock_patch, mock_get):
        """Payment processes successfully"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'items': []}
        mock_patch.return_value.status_code = 200

        response = self.client.post(
            '/api/payments/process_payment/',
            self.valid_payment,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'completed')
        self.assertIsNotNone(response.data['transaction_id'])

    @patch('payments.views.requests.get')
    @patch('payments.views.requests.patch')
    def test_payment_reduces_stock_on_success(self, mock_patch, mock_get):
        """Successful payment reduces stock via Product Service"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'items': [
                {'product_id': 1, 'quantity': 2},
                {'product_id': 2, 'quantity': 1},
            ]
        }
        mock_patch.return_value.status_code = 200

        response = self.client.post('/api/payments/process_payment/', self.valid_payment, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'completed')

        # Check stock update calls were made
        stock_calls = [
            call for call in mock_patch.call_args_list
            if 'update_stock' in str(call)
        ]
        self.assertEqual(len(stock_calls), 2)

    def test_process_payment_missing_order_id(self):
        """order_id is required"""
        response = self.client.post(
            '/api/payments/process_payment/',
            {'user_id': 1, 'amount': 1000},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_process_payment_missing_user_id(self):
        """user_id is required"""
        response = self.client.post(
            '/api/payments/process_payment/',
            {'order_id': 1, 'amount': 1000},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_process_payment_missing_amount(self):
        """amount is required"""
        response = self.client.post(
            '/api/payments/process_payment/',
            {'order_id': 1, 'user_id': 1},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_process_payment_default_payment_method(self):
        """Default payment method is credit_card"""
        with patch('payments.views.requests.get') as mock_get, \
             patch('payments.views.requests.patch') as mock_patch:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'items': []}
            mock_patch.return_value.status_code = 200

            response = self.client.post(
                '/api/payments/process_payment/',
                {'order_id': 1, 'user_id': 1, 'amount': 2000},
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(PaymentTransaction.objects.first().payment_method, 'credit_card')

    # ──────────────────────────────────────────────
    # BY ORDER TESTS
    # ──────────────────────────────────────────────

    def test_by_order_returns_payments(self):
        """Returns payments for a specific order"""
        with patch('payments.views.requests.get') as mock_get, \
             patch('payments.views.requests.patch') as mock_patch:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'items': []}
            mock_patch.return_value.status_code = 200

            self.client.post('/api/payments/process_payment/', self.valid_payment, format='json')
            self.client.post('/api/payments/process_payment/', self.valid_payment, format='json')

        response = self.client.get('/api/payments/by_order/?order_id=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_by_order_missing_order_id(self):
        """order_id is required"""
        response = self.client.get('/api/payments/by_order/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_by_order_no_payments(self):
        """Returns empty list for order with no payments"""
        response = self.client.get('/api/payments/by_order/?order_id=999')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    # ──────────────────────────────────────────────
    # TRANSACTION TESTS
    # ──────────────────────────────────────────────

    def test_transaction_has_uuid(self):
        """Each transaction gets a unique ID"""
        with patch('payments.views.requests.get') as mock_get, \
             patch('payments.views.requests.patch') as mock_patch:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'items': []}
            mock_patch.return_value.status_code = 200

            response = self.client.post('/api/payments/process_payment/', self.valid_payment, format='json')
            self.assertIsNotNone(response.data['transaction_id'])
            self.assertEqual(len(response.data['transaction_id'].replace('-', '')), 32)

    def test_transaction_has_timestamp(self):
        """Each transaction records creation time"""
        with patch('payments.views.requests.get') as mock_get, \
             patch('payments.views.requests.patch') as mock_patch:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'items': []}
            mock_patch.return_value.status_code = 200

            response = self.client.post('/api/payments/process_payment/', self.valid_payment, format='json')
            self.assertIn('created_at', response.data)

    # ──────────────────────────────────────────────
    # HEALTH CHECK
    # ──────────────────────────────────────────────

    def test_health_check(self):
        response = self.client.get('/api/payments/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['service'], 'payment-service')

    # ──────────────────────────────────────────────
    # STOCK UPDATE ON SUCCESS
    # ──────────────────────────────────────────────

    @patch('payments.views.requests.get')
    @patch('payments.views.requests.patch')
    def test_stock_reduced_for_each_item(self, mock_patch, mock_get):
        """Each item in the order gets its stock reduced"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'items': [
                {'product_id': 10, 'quantity': 3},
                {'product_id': 20, 'quantity': 1},
                {'product_id': 30, 'quantity': 5},
            ]
        }
        mock_patch.return_value.status_code = 200

        self.client.post('/api/payments/process_payment/', {
            'order_id': 1, 'user_id': 1, 'amount': 5000
        }, format='json')

        # Count calls to update_stock
        stock_updates = [
            c for c in mock_patch.call_args_list
            if 'update_stock' in str(c)
        ]
        self.assertEqual(len(stock_updates), 3)

    @patch('payments.views.requests.get')
    @patch('payments.views.requests.patch')
    def test_payment_still_completes_if_stock_update_fails(self, mock_patch, mock_get):
        """If stock update fails, payment still marked as completed"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        mock_patch.side_effect = Exception('Product service down')

        response = self.client.post('/api/payments/process_payment/', self.valid_payment, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'completed')


class AdminTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='root',
            email='admin@test.com',
            password='admin123'
        )
        self.client.login(username='root', password='admin123')

    def test_admin_accessible(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_admin_payments_list(self):
        response = self.client.get('/admin/payments/paymenttransaction/')
        self.assertEqual(response.status_code, 200)