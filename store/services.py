import logging
from django.core.mail import EmailMessage
from django.db import transaction
from django.utils import timezone
from .models import EmailDelivery
logger = logging.getLogger(__name__)

def send_delivery(delivery_id):
    # Serialize retries so concurrent workers cannot send the same task together.
    with transaction.atomic():
        delivery = EmailDelivery.objects.select_for_update().select_related('order').get(pk=delivery_id)
        if delivery.status == 'sent' or delivery.order.status != 'confirmed': return
        delivery.attempt_count += 1
        order = delivery.order
        lines = ['eBook Placeholder', '', f'Order: {order.order_number}', '']
        lines += [f'Book: {item.book_title}' for item in order.items.all()]
        lines += ['', 'This file is a placeholder for the purchased eBooks.', 'No actual book content is included.']
        message = EmailMessage(subject=f'Your Leaf & Lore order {str(order.order_number)[:8]}', body=f'Hello {order.customer_name},\n\nThank you for your order. Your total is ${order.total_amount}. Your eBook placeholder is attached.\n\nLeaf & Lore', to=[delivery.recipient_email])
        message.attach(delivery.attachment_name, '\n'.join(lines), 'text/plain')
        try:
            if message.send() != 1: raise RuntimeError('Email backend did not accept the message')
        except Exception:
            logger.exception('Email delivery %s failed', delivery.pk)
            delivery.status = 'failed'
            delivery.last_error = 'Email could not be sent. Check server logs and SMTP settings.'
        else:
            delivery.status = 'sent'
            delivery.sent_at = timezone.now()
            delivery.last_error = ''
        delivery.save()
