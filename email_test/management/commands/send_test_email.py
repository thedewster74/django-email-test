from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Send a test email to verify email configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            'to_email',
            type=str,
            help='Email address to send the test email to'
        )
        parser.add_argument(
            '--subject',
            type=str,
            default='Test Email from Django',
            help='Subject line for the test email'
        )
        parser.add_argument(
            '--message',
            type=str,
            default='This is a test email sent from the Django email test application.',
            help='Message body for the test email'
        )

    def handle(self, *args, **options):
        to_email = options['to_email']
        subject = options['subject']
        message = options['message']

        self.stdout.write(self.style.WARNING(f'Sending test email to: {to_email}'))
        self.stdout.write(f'Subject: {subject}')
        self.stdout.write(f'Backend: {settings.EMAIL_BACKEND}')

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully sent test email to {to_email}'))
        except Exception as e:
            raise CommandError(f'Failed to send email: {str(e)}')
