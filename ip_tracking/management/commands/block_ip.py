
from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP

class Command(BaseCommand):
    help = 'Block an IP address'

    def add_arguments(self, parser):
        parser.add_argument('ip_addresses', nargs='+', type=str, help='List of IP addresses to block.')

    def handle(self, *args, **kwargs):
        for ip_address in kwargs['ip_addresses']:
            try:
                blocked_ip, created = BlockedIP.objects.get_or_create(ip_address=ip_address)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully blocked IP address {ip_address}.'))
                else:
                    self.stdout.write(self.style.WARNING(f'IP address {ip_address} is already blocked.'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error blocking IP {ip_address}: {str(e)}'))