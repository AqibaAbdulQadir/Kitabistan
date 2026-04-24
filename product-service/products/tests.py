from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Category, Book
from django.contrib.auth.models import User


class ProductTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Self Help')
        self.book = Book.objects.create(
            title='Atomic Habits',
            author='James Clear',
            price=3000,
            stock=10,
            category=self.category
        )

    # ──────────────────────────────────────────────
    # CATEGORY TESTS
    # ──────────────────────────────────────────────

    def test_list_categories(self):
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_category(self):
        response = self.client.post('/api/categories/', {'name': 'Fiction'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)

    def test_category_name_validation(self):
        """Category name must be letters and spaces only"""
        response = self.client.post('/api/categories/', {'name': 'Fiction123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ──────────────────────────────────────────────
    # BOOK TESTS
    # ──────────────────────────────────────────────

    def test_list_books(self):
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_book(self):
        response = self.client.post('/api/books/', {
            'title': 'Deep Work',
            'author': 'Cal Newport',
            'price': 2500,
            'stock': 5,
            'category': self.category.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_create_book_negative_price(self):
        response = self.client.post('/api/books/', {
            'title': 'Bad Book',
            'author': 'Author',
            'price': -100,
            'stock': 5,
            'category': self.category.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_book_negative_stock(self):
        response = self.client.post('/api/books/', {
            'title': 'Bad Book',
            'author': 'Author',
            'price': 1000,
            'stock': -5,
            'category': self.category.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_book_in_stock_field(self):
        """in_stock is True when stock > 0"""
        response = self.client.get(f'/api/books/{self.book.id}/')
        self.assertTrue(response.data['in_stock'])

    def test_book_out_of_stock(self):
        """in_stock is False when stock is 0"""
        self.book.stock = 0
        self.book.save()
        response = self.client.get(f'/api/books/{self.book.id}/')
        self.assertFalse(response.data['in_stock'])

    def test_filter_by_category(self):
        fiction = Category.objects.create(name='Fiction')
        Book.objects.create(title='Fiction Book', author='Author', price=1000, stock=3, category=fiction)

        response = self.client.get(f'/api/books/?category={self.category.id}')
        self.assertEqual(len(response.data), 1)

    def test_search_books(self):
        response = self.client.get('/api/books/?search=Atomic')
        self.assertEqual(len(response.data), 1)

    def test_search_books_no_match(self):
        response = self.client.get('/api/books/?search=NonExistent')
        self.assertEqual(len(response.data), 0)

    # ──────────────────────────────────────────────
    # STOCK UPDATE TESTS
    # ──────────────────────────────────────────────

    def test_update_stock_success(self):
        response = self.client.patch(
            f'/api/books/{self.book.id}/update_stock/',
            {'quantity': 3}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stock'], 7)

    def test_update_stock_insufficient(self):
        """Cannot reduce stock below 0"""
        response = self.client.patch(
            f'/api/books/{self.book.id}/update_stock/',
            {'quantity': 20}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_stock_exact(self):
        """Reducing stock to exactly 0 works"""
        response = self.client.patch(
            f'/api/books/{self.book.id}/update_stock/',
            {'quantity': 10}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stock'], 0)

    # ──────────────────────────────────────────────
    # HEALTH CHECK
    # ──────────────────────────────────────────────

    def test_health_check(self):
        response = self.client.get('/api/books/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['service'], 'product-service')
    
    def test_restore_stock(self):
        """Stock can be restored (e.g., after failed payment)"""
        response = self.client.patch(
            f'/api/books/{self.book.id}/restore_stock/',
            {'quantity': 5}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stock'], 15)  # 10 + 5

    def test_restore_stock_then_reduce(self):
        """Full cycle: reduce → restore → reduce"""
        # Reduce
        self.client.patch(f'/api/books/{self.book.id}/update_stock/', {'quantity': 7})
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, 3)

        # Restore (failed payment)
        self.client.patch(f'/api/books/{self.book.id}/restore_stock/', {'quantity': 7})
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, 10)

        # Reduce again (new successful payment)
        self.client.patch(f'/api/books/{self.book.id}/update_stock/', {'quantity': 4})
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, 6)


class AdminTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='root',
            email='aqibaabdulqadir@gmail.com',
            password='aqiba123'
        )
        self.client.login(username='root', password='aqiba123')

    def test_admin_accessible(self):
        """Admin panel loads for superuser"""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_books_list(self):
        """Books are listed in admin"""
        response = self.client.get('/admin/products/book/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_categories_list(self):
        """Categories are listed in admin"""
        response = self.client.get('/admin/products/category/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_add_book_page(self):
        """Add book page loads"""
        response = self.client.get('/admin/products/book/add/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

