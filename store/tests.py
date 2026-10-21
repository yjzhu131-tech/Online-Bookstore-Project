from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase, override_settings, Client
from django.core import mail
from .models import Book, SalesOrder, EmailDelivery
from .services import send_delivery

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class StoreTests(TestCase):
    def setUp(self):
        self.book = Book.objects.create(title='A quiet story', author='Alice; Bob', category='Fiction',description='A story.',price='12.50')
    def prepare(self):
        self.client.post(f'/bag/add/{self.book.pk}/')
        self.client.get('/checkout/')
    def place(self):
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post('/checkout/',{'name':'Reader','email':'reader@example.com','total':'0.01'})
    def test_search_by_author_and_category(self):
        self.assertContains(self.client.get('/?q=Bob&category=Fiction'),'A quiet story')
        self.assertContains(self.client.get('/?q=Unknown'),'No books found')
    def test_checkout_snapshot_attachment_and_idempotency(self):
        self.prepare()
        response = self.place()
        order = SalesOrder.objects.get()
        self.assertEqual(order.total_amount, Decimal('12.50'))
        self.assertEqual(order.items.get().unit_price,Decimal('12.50'))
        self.assertEqual(len(mail.outbox),1)
        attachment = mail.outbox[0].attachments[0]
        self.assertTrue(attachment[0].endswith('.txt'))
        self.assertIn('A quiet story',attachment[1])
        self.assertEqual(attachment[2],'text/plain')
        self.assertContains(self.client.get(response.url),'Your order is confirmed')
        self.place()
        self.assertEqual(SalesOrder.objects.count(),1)
        self.assertEqual(len(mail.outbox),1)
        self.assertEqual(Client().get(response.url).status_code,404)
        self.book.price = Decimal('99.00')
        self.book.save()
        order.refresh_from_db()
        self.assertEqual(order.items.get().unit_price,Decimal('12.50'))
    def test_failed_email_keeps_order_and_retries(self):
        self.prepare()
        with patch('store.services.EmailMessage.send',side_effect=OSError('SMTP unavailable')):
            with self.assertLogs('store.services',level='ERROR'): self.place()
        delivery = EmailDelivery.objects.get()
        self.assertEqual(delivery.status,'failed')
        self.assertEqual(SalesOrder.objects.count(),1)
        send_delivery(delivery.pk)
        delivery.refresh_from_db()
        self.assertEqual(delivery.status,'sent')
        self.assertEqual(delivery.attempt_count,2)
        send_delivery(delivery.pk)
        self.assertEqual(len(mail.outbox),1)
    def test_cart_duplicates_inactive_and_remove(self):
        self.prepare()
        self.client.post(f'/bag/add/{self.book.pk}/')
        self.assertEqual(len(self.client.session['cart']),1)
        self.book.is_active = False
        self.book.save()
        self.assertRedirects(self.client.get('/checkout/'),'/')
        self.assertEqual(self.client.post(f'/bag/add/{self.book.pk}/').status_code,404)
        self.client.post(f'/bag/remove/{self.book.pk}/')
        self.assertEqual(self.client.session['cart'],[])
    def test_validation_and_csrf(self):
        self.prepare()
        self.assertContains(self.client.post('/checkout/',{'name':'Reader','email':'bad'}),'Enter a valid email')
        self.assertFalse(SalesOrder.objects.exists())
        csrf_client = Client(enforce_csrf_checks=True)
        self.assertEqual(csrf_client.post(f'/bag/add/{self.book.pk}/').status_code,403)
    def test_second_order_gets_new_key(self):
        self.prepare()
        self.place()
        self.prepare()
        self.place()
        self.assertEqual(SalesOrder.objects.count(),2)
    def test_pages_render(self):
        for url in ['/',f'/books/{self.book.pk}/','/bag/','/admin/login/']:
            self.assertEqual(self.client.get(url).status_code,200)
    def test_file_backend_writes_readable_mime_attachment(self):
        import tempfile
        from pathlib import Path
        from email import policy
        from email.parser import BytesParser
        self.prepare()
        with tempfile.TemporaryDirectory() as directory:
            with override_settings(EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend', EMAIL_FILE_PATH=directory):
                self.place()
            files = list(Path(directory).glob('*.log'))
            self.assertEqual(len(files),1)
            message = BytesParser(policy=policy.default).parsebytes(files[0].read_bytes())
            attachment = list(message.iter_attachments())[0]
            self.assertIn('A quiet story',attachment.get_content())
            self.assertTrue(attachment.get_filename().endswith('.txt'))
