from django.core.management.base import BaseCommand
from django.db import transaction
from store.models import Book

# USD demonstration prices based on the editions linked in docs/book-prices.md.
BOOKS = [
    ('1984', 'George Orwell', 'Dystopian Fiction', '9.99',
     'Winston Smith questions a government that monitors its citizens and controls the record of the past.'),
    ('The Hobbit', 'J. R. R. Tolkien', 'Fantasy', '11.99',
     'Bilbo Baggins leaves his comfortable home to join a company of dwarves on a journey to reclaim treasure guarded by a dragon.'),
    ('Pride and Prejudice', 'Jane Austen', 'Classic Fiction', '2.99',
     'Elizabeth Bennet and Mr. Darcy reconsider their first impressions while navigating family expectations and social class.'),
    ('The Great Gatsby', 'F. Scott Fitzgerald', 'Classic Fiction', '0.49',
     'Nick Carraway encounters Jay Gatsby and the wealth, ambition, and disappointed hopes of 1920s Long Island.'),
    ('To Kill a Mockingbird', 'Harper Lee', 'Classic Fiction', '13.99',
     'Scout Finch grows up in Alabama as her father, Atticus, defends a Black man accused of a crime in a community shaped by prejudice.'),
    ('The Alchemist', 'Paulo Coelho', 'Adventure Fiction', '14.99',
     'A shepherd named Santiago travels in search of treasure and reflects on the meaning of his dreams along the way.'),
    ('Atomic Habits', 'James Clear', 'Self-Help', '12.99',
     'A practical guide to building useful habits and changing unwanted routines through small, consistent actions.'),
    ('Jane Eyre', 'Charlotte Brontë', 'Classic Fiction', '2.99',
     'An orphan becomes a governess and seeks independence while confronting difficult choices about love and self-respect.'),
]

# Retire only the original demonstration records, preserving past order references.
LEGACY_BOOKS = [
    ('The Art of Paying Attention', 'Clara Bennett'),
    ('A Map of Small Wonders', 'Elias Rivers'),
    ('The Last Light in August', 'Nora Ellis'),
    ('How Ideas Grow', 'Samuel Park'),
    ('Beneath the Quiet Sky', 'Maya Chen'),
    ('The Everyday Kitchen', 'Sofia Hart'),
    ('Notes from the Garden', 'Oliver Reed'),
    ('A Life Less Hurried', 'Amelia Brooks'),
]


class Command(BaseCommand):
    help = 'Add well-known books and hide the original fictional samples'

    @transaction.atomic
    def handle(self, *args, **options):
        for title, author in LEGACY_BOOKS:
            Book.objects.filter(title=title, author=author).update(is_active=False)
        created_count = 0
        for title, author, category, price, description in BOOKS:
            _, created = Book.objects.get_or_create(
                title=title, author=author,
                defaults={'category': category, 'price': price, 'description': description},
            )
            created_count += created
        self.stdout.write(self.style.SUCCESS(
            f'Catalog ready: {created_count} books added. Existing book edits were preserved.'
        ))
