from django.core.management.base import BaseCommand
from products.models import Category, Book

class Command(BaseCommand):
    help = 'Seeds the database with sample books and categories'

    def handle(self, *args, **kwargs):
        # Create Categories
        categories = {
            'Self Help': [
                ('Atomic Habits', 'James Clear', 3000, 50),
                ('The 7 Habits of Highly Effective People', 'Stephen Covey', 3500, 40),
                ('Think and Grow Rich', 'Napoleon Hill', 2500, 60),
                ('The Power of Now', 'Eckhart Tolle', 2800, 35),
                ('How to Win Friends and Influence People', 'Dale Carnegie', 3200, 45),
                ('The Subtle Art of Not Giving a F*ck', 'Mark Manson', 2700, 55),
                ('You Are a Badass', 'Jen Sincero', 2200, 30),
            ],
            'Fiction': [
                ('To Kill a Mockingbird', 'Harper Lee', 2000, 25),
                ('1984', 'George Orwell', 1800, 40),
                ('Pride and Prejudice', 'Jane Austen', 1500, 35),
                ('The Great Gatsby', 'F. Scott Fitzgerald', 1600, 30),
                ('One Hundred Years of Solitude', 'Gabriel García Márquez', 3000, 20),
                ('The Catcher in the Rye', 'J.D. Salinger', 2200, 28),
                ('Brave New World', 'Aldous Huxley', 1900, 32),
                ('Animal Farm', 'George Orwell', 1400, 50),
            ],
            'Technology': [
                ('Clean Code', 'Robert C. Martin', 4500, 25),
                ('The Pragmatic Programmer', 'David Thomas', 5000, 20),
                ('Design Patterns', 'Gang of Four', 5500, 15),
                ('Introduction to Algorithms', 'Thomas H. Cormen', 6000, 12),
                ('Deep Learning', 'Ian Goodfellow', 7000, 10),
                ('Python Crash Course', 'Eric Matthes', 3800, 30),
                ('The DevOps Handbook', 'Gene Kim', 4200, 18),
            ],
            'Business': [
                ('Zero to One', 'Peter Thiel', 3500, 28),
                ('The Lean Startup', 'Eric Ries', 3200, 30),
                ('Good to Great', 'Jim Collins', 2800, 25),
                ('Start with Why', 'Simon Sinek', 2500, 35),
                ('The 4-Hour Work Week', 'Tim Ferriss', 3000, 22),
                ('Rich Dad Poor Dad', 'Robert Kiyosaki', 2200, 50),
                ('Shoe Dog', 'Phil Knight', 4000, 18),
            ],
            'Science': [
                ('A Brief History of Time', 'Stephen Hawking', 3500, 20),
                ('Sapiens', 'Yuval Noah Harari', 4000, 40),
                ('The Selfish Gene', 'Richard Dawkins', 3200, 15),
                ('Cosmos', 'Carl Sagan', 2800, 22),
                ('Surely You\'re Joking, Mr. Feynman!', 'Richard Feynman', 3000, 18),
            ],
            'History': [
                ('Guns, Germs, and Steel', 'Jared Diamond', 3800, 20),
                ('The Diary of a Young Girl', 'Anne Frank', 1800, 35),
                ('A People\'s History of the United States', 'Howard Zinn', 4200, 15),
                ('Sapiens', 'Yuval Noah Harari', 4000, 40),
                ('The Rise and Fall of the Third Reich', 'William Shirer', 5000, 10),
            ],
        }

        total = 0
        for cat_name, books in categories.items():
            category, _ = Category.objects.get_or_create(name=cat_name)
            for title, author, price, stock in books:
                book, created = Book.objects.get_or_create(
                    title=title,
                    defaults={
                        'author': author,
                        'price': price,
                        'stock': stock,
                        'category': category,
                    }
                )
                if created:
                    total += 1
                    self.stdout.write(f'  ✅ {title}')

        self.stdout.write(self.style.SUCCESS(f'\n🎉 Seeded {total} new books across {len(categories)} categories!'))