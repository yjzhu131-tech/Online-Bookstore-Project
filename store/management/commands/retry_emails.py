from django.core.management.base import BaseCommand
from store.models import EmailDelivery
from store.services import send_delivery
class Command(BaseCommand):
    help = 'Retry pending and failed order emails'
    def handle(self,*args,**options):
        for pk in EmailDelivery.objects.exclude(status='sent').values_list('pk',flat=True): send_delivery(pk)
        self.stdout.write(self.style.SUCCESS('Email retry pass complete.'))
