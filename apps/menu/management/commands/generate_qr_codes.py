from django.core.management.base import BaseCommand
from apps.menu.utils import generate_table_qr

class Command(BaseCommand):
    help = 'Bulk generates QR codes for dining tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tables',
            type=int,
            default=20,
            help='Number of dining tables to generate QR codes for (default 20)'
        )

    def handle(self, *args, **options):
        num_tables = options['tables']
        self.stdout.write(self.style.NOTICE(f'Starting QR code generation for {num_tables} tables...'))
        
        for table in range(1, num_tables + 1):
            path = generate_table_qr(table)
            self.stdout.write(self.style.SUCCESS(f'Successfully generated QR code for Table {table} at {path}'))

        self.stdout.write(self.style.SUCCESS(f'Finished generating QR codes for {num_tables} tables.'))
