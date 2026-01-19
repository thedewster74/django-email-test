import ssl
import socket
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Check SSL certificate for SMTP server to diagnose hostname mismatches'

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            type=str,
            default=None,
            help='SMTP host to check (defaults to EMAIL_HOST setting)'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=None,
            help='SMTP port to check (defaults to EMAIL_PORT setting)'
        )

    def handle(self, *args, **options):
        host = options['host'] or settings.EMAIL_HOST
        port = options['port'] or settings.EMAIL_PORT

        self.stdout.write(self.style.WARNING(f'\n=== Checking SSL Certificate for {host}:{port} ===\n'))

        try:
            # Create a socket connection
            sock = socket.create_connection((host, port), timeout=10)

            # Create SSL context
            context = ssl.create_default_context()

            # For STARTTLS (port 587), we need to do SMTP handshake first
            if port == 587:
                self.stdout.write('Port 587 detected - attempting STARTTLS...')
                # Send EHLO command
                sock.sendall(b'EHLO localhost\r\n')
                response = sock.recv(1024)
                self.stdout.write(f'EHLO response: {response.decode("utf-8", errors="ignore").strip()}')

                # Send STARTTLS command
                sock.sendall(b'STARTTLS\r\n')
                response = sock.recv(1024)
                self.stdout.write(f'STARTTLS response: {response.decode("utf-8", errors="ignore").strip()}\n')

            # Wrap socket with SSL
            try:
                ssl_sock = context.wrap_socket(sock, server_hostname=host)
            except ssl.SSLError as e:
                self.stdout.write(self.style.ERROR(f'\nSSL Error: {e}\n'))
                # Try to get cert anyway without hostname verification
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock.close()
                sock = socket.create_connection((host, port), timeout=10)

                if port == 587:
                    sock.sendall(b'EHLO localhost\r\n')
                    sock.recv(1024)
                    sock.sendall(b'STARTTLS\r\n')
                    sock.recv(1024)

                ssl_sock = context.wrap_socket(sock, server_hostname=host)
                self.stdout.write(self.style.WARNING('Certificate retrieved without verification\n'))

            # Get certificate
            cert = ssl_sock.getpeercert()

            # Display certificate information
            self.stdout.write(self.style.SUCCESS('Certificate Details:'))
            self.stdout.write('-' * 50)

            # Subject (Common Name)
            subject = dict(x[0] for x in cert.get('subject', []))
            common_name = subject.get('commonName', 'N/A')
            self.stdout.write(f'Common Name (CN): {common_name}')

            # Issuer
            issuer = dict(x[0] for x in cert.get('issuer', []))
            issuer_cn = issuer.get('commonName', 'N/A')
            self.stdout.write(f'Issuer: {issuer_cn}')

            # Validity period
            self.stdout.write(f'Not Before: {cert.get("notBefore", "N/A")}')
            self.stdout.write(f'Not After: {cert.get("notAfter", "N/A")}')

            # Subject Alternative Names (SANs)
            self.stdout.write('\nSubject Alternative Names (SANs):')
            san_list = []
            for san_type, san_value in cert.get('subjectAltName', []):
                san_list.append(san_value)
                self.stdout.write(f'  - {san_value}')

            if not san_list:
                self.stdout.write('  (none)')

            # Provide recommendations
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write(self.style.WARNING('\nRecommendation:'))

            valid_hostnames = san_list if san_list else [common_name]
            if host not in valid_hostnames:
                self.stdout.write(self.style.ERROR(
                    f'\nThe hostname you are using ({host}) does NOT match the certificate!'
                ))
                self.stdout.write(self.style.SUCCESS(
                    f'\nTry using one of these hostnames instead:'
                ))
                for hostname in valid_hostnames:
                    self.stdout.write(f'  EMAIL_HOST={hostname}')
            else:
                self.stdout.write(self.style.SUCCESS(
                    f'\nThe hostname {host} matches the certificate!'
                ))

            # Close connection
            ssl_sock.close()

        except socket.timeout:
            self.stdout.write(self.style.ERROR(f'\nConnection timeout to {host}:{port}'))
        except socket.gaierror as e:
            self.stdout.write(self.style.ERROR(f'\nDNS resolution failed: {e}'))
        except ConnectionRefusedError:
            self.stdout.write(self.style.ERROR(f'\nConnection refused by {host}:{port}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nError: {type(e).__name__}: {e}'))
