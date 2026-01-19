import ssl
import socket
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False


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

                # Read server greeting (220)
                greeting = sock.recv(4096)
                self.stdout.write(f'Server greeting: {greeting.decode("utf-8", errors="ignore").strip()}')

                # Send EHLO command
                sock.sendall(b'EHLO localhost\r\n')
                # Read EHLO response (may be multi-line with 250-)
                ehlo_response = b''
                while True:
                    chunk = sock.recv(4096)
                    ehlo_response += chunk
                    # Check if we got the final line (250 without dash)
                    if b'\n250 ' in chunk or (chunk.endswith(b'\n') and not b'250-' in chunk.split(b'\n')[-2]):
                        break
                self.stdout.write(f'EHLO response: {ehlo_response.decode("utf-8", errors="ignore").strip()}')

                # Send STARTTLS command
                sock.sendall(b'STARTTLS\r\n')
                starttls_response = sock.recv(4096)
                self.stdout.write(f'STARTTLS response: {starttls_response.decode("utf-8", errors="ignore").strip()}\n')

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
                    # Read greeting
                    sock.recv(4096)
                    # Send EHLO
                    sock.sendall(b'EHLO localhost\r\n')
                    # Read EHLO response
                    while True:
                        chunk = sock.recv(4096)
                        if b'\n250 ' in chunk or (chunk.endswith(b'\n') and not b'250-' in chunk.split(b'\n')[-2]):
                            break
                    # Send STARTTLS
                    sock.sendall(b'STARTTLS\r\n')
                    # Read STARTTLS response
                    sock.recv(4096)

                ssl_sock = context.wrap_socket(sock, server_hostname=host)
                self.stdout.write(self.style.WARNING('Certificate retrieved without verification\n'))

            # Get certificate in binary form
            cert_der = ssl_sock.getpeercert(binary_form=True)

            # Display certificate information
            self.stdout.write(self.style.SUCCESS('Certificate Details:'))
            self.stdout.write('-' * 50)

            # Parse certificate
            if HAS_CRYPTOGRAPHY and cert_der:
                cert_obj = x509.load_der_x509_certificate(cert_der, default_backend())

                # Common Name
                try:
                    common_name = cert_obj.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value
                except (IndexError, AttributeError):
                    common_name = 'N/A'
                self.stdout.write(f'Common Name (CN): {common_name}')

                # Issuer
                try:
                    issuer_cn = cert_obj.issuer.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value
                except (IndexError, AttributeError):
                    issuer_cn = 'N/A'
                self.stdout.write(f'Issuer: {issuer_cn}')

                # Validity period
                self.stdout.write(f'Not Before: {cert_obj.not_valid_before_utc}')
                self.stdout.write(f'Not After: {cert_obj.not_valid_after_utc}')

                # Subject Alternative Names (SANs)
                self.stdout.write('\nSubject Alternative Names (SANs):')
                san_list = []
                try:
                    san_ext = cert_obj.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
                    for san in san_ext.value:
                        if isinstance(san, x509.DNSName):
                            san_list.append(san.value)
                            self.stdout.write(f'  - {san.value}')
                except x509.ExtensionNotFound:
                    pass

                if not san_list:
                    self.stdout.write('  (none)')
            else:
                # Fallback to getpeercert() dict form
                cert = ssl_sock.getpeercert()

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
