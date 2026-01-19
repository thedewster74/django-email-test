from django.http import JsonResponse
from django.core.mail import send_mail, EmailMessage
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json


@csrf_exempt
@require_http_methods(["POST"])
def send_test_email(request):
    """
    Send a test email.
    POST body: {
        "to_email": "recipient@example.com",
        "subject": "Test Subject",
        "message": "Test message body"
    }
    """
    try:
        data = json.loads(request.body)
        to_email = data.get('to_email')
        subject = data.get('subject', 'Test Email')
        message = data.get('message', 'This is a test email from Django.')

        if not to_email:
            return JsonResponse({
                'success': False,
                'error': 'to_email is required'
            }, status=400)

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )

        return JsonResponse({
            'success': True,
            'message': f'Email sent successfully to {to_email}'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def send_html_email(request):
    """
    Send an HTML email.
    POST body: {
        "to_email": "recipient@example.com",
        "subject": "Test Subject",
        "html_content": "<h1>Test HTML Email</h1>"
    }
    """
    try:
        data = json.loads(request.body)
        to_email = data.get('to_email')
        subject = data.get('subject', 'Test HTML Email')
        html_content = data.get('html_content', '<h1>This is a test HTML email</h1>')

        if not to_email:
            return JsonResponse({
                'success': False,
                'error': 'to_email is required'
            }, status=400)

        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.content_subtype = 'html'
        email.send()

        return JsonResponse({
            'success': True,
            'message': f'HTML email sent successfully to {to_email}'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def email_config_status(request):
    """
    Get current email configuration status (without exposing sensitive data).
    """
    config = {
        'email_backend': settings.EMAIL_BACKEND,
        'email_host': settings.EMAIL_HOST,
        'email_port': settings.EMAIL_PORT,
        'email_use_tls': settings.EMAIL_USE_TLS,
        'email_use_ssl': settings.EMAIL_USE_SSL,
        'default_from_email': settings.DEFAULT_FROM_EMAIL,
        'has_credentials': bool(settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD),
    }

    return JsonResponse({
        'success': True,
        'config': config
    })
