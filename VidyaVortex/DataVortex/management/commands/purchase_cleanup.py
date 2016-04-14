# purchase_cleanup.py for VidyaVortex project 2015-2016

from django.core.management.base import BaseCommand
from DataVortex.models import Purchase
from datetime import datetime, timedelta

# command used to clean invalid Purchase objects from database that are older than an hour
# invalid Purchase objects are created when user does not cancel or complete the payment properly
class Command(BaseCommand):
    def handle(self, **options):
        print("Running purchase cleanup...")
        now = datetime.now() - timedelta(hours=1)
        purchases = Purchase.objects.filter(valid=False)
        for purchase in purchases:
            if purchase.time.replace(tzinfo=None) < now:
                print("Delete invalid purchase > id: '%d', time: '%s', buyer: '%s', amount: '%f'" % (purchase.id, 
                    str(purchase.time).split('.')[0], purchase.buyer, purchase.amount))
                purchase.delete()
        print("DONE!")
