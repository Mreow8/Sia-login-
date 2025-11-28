import json
import random
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
# NEW IMPORTS
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from smtplib import SMTPException
from myproject.firebase import firebase_admin  # ensures Firebase is initialized
from myproject import init_firebase
from firebase_admin import auth
from .models import EmailVerification, LoginAttempt

import json
import random
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import EmailVerification
from .utils.email_service import send_email

@csrf_exempt
def send_email_otp(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error'}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()

        # 1. Validate Email Format
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'status': 'error', 'message': 'Invalid email address format.'})

        # 2. Check if already registered
        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Account already exists. Please login.'})

        # 3. Generate OTP
        otp = str(random.randint(100000, 999999))
        EmailVerification.objects.update_or_create(
            email=email,
            defaults={'otp_code': otp, 'is_verified': False, 'created_at': timezone.now()}
        )

        # 4. Send Email using Brevo
        html_content = f"<p>Your verification code is: <strong>{otp}</strong></p>"
        result = send_email(
            subject="Your Verification Code",
            html_content=html_content,
            to_emails=email
        )

        if result:
            return JsonResponse({'status': 'success', 'message': 'Code sent!'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to send email. Check server logs.'})

    except Exception as e:
        print(f"Error sending OTP: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'})

@ensure_csrf_cookie
def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    context = {
        'firebase_config': settings.FIREBASE_CONFIG
    }
    return render(request, 'login.html', context)

@login_required(login_url='/')
def dashboard(request):
    context = {
        'firebase_config': settings.FIREBASE_CONFIG
    }
    return render(request, 'dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('/')
from mainapp.utils.email_service import send_email

@csrf_exempt
def report_failure(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            identifier = data.get('identifier') 
            ip = request.META.get('REMOTE_ADDR')

            LoginAttempt.objects.create(email=identifier, ip_address=ip, success=False)

            # 30 Seconds Window
            time_threshold = timezone.now() - timedelta(seconds=30)
            recent_failures = LoginAttempt.objects.filter(
                email=identifier, 
                success=False,
                timestamp__gte=time_threshold
            ).count()

            response = {'status': 'ok', 'count': recent_failures}

            if recent_failures == 3:
                # Only alert existing users
                if User.objects.filter(email=identifier).exists():
                    email_body = (
                        f"Hello,\n\n"
                        f"We noticed 5 failed login attempts on your account.\n"
                        f"IP Address: {ip}\n"
                        f"Time: {timezone.now()}"
                    )
                    result = send_email(
                        to_emails=identifier,
                        subject="Security Alert",
                        html_content=email_body
                    )
                    if result['status'] == 'success':
                        response['alert'] = "Email alert sent."
                    else:
                        print(f"Email alert failed: {result['message']}")

            if recent_failures >= 5:
                response['status'] = 'blocked'
                response['message'] = 'Too many attempts.'

            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error'}, status=405)

@csrf_exempt
def verify_email_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get('email')
        otp = data.get('otp')

        try:
            time_threshold = timezone.now() - timedelta(minutes=5)
            record = EmailVerification.objects.filter(email=email, otp_code=otp, created_at__gte=time_threshold).first()
            
            if record:
                record.is_verified = True
                record.save()
                return JsonResponse({'status': 'success', 'message': 'Verified'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid or Expired Code'})
        except Exception:
             return JsonResponse({'status': 'error', 'message': 'Verification failed'})

@csrf_exempt
def complete_registration(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            token = data.get('token')
            
            # Ensure SDK is initialized; call again in case module-level init failed
            init_firebase()
            # Verify initialization explicitly so we can return a helpful error
            try:
                firebase_admin.get_app()
            except ValueError:
                return JsonResponse({'status': 'error', 'message': 'Server Firebase Admin SDK not configured.'}, status=500)
            decoded_token = auth.verify_id_token(token)
            email = decoded_token['email']

            if User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'error', 'message': 'User already exists'})

            User.objects.create_user(username=email, email=email)
            
            return JsonResponse({'status': 'success', 'message': 'Account created'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error'}, status=405)

@csrf_exempt
def handle_email_login(request):
    if request.method == "POST":
        data = json.loads(request.body)
        token = data.get('token')

        try:
            # 1. Verify Token
            init_firebase()
            try:
                firebase_admin.get_app()
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Server Firebase Admin SDK not configured.'}, status=500)
            decoded_token = auth.verify_id_token(token)
            email = decoded_token['email']
            
            # 2. Security Check (30s Lock)
            time_threshold = timezone.now() - timedelta(seconds=30)
            fail_count = LoginAttempt.objects.filter(
                email=email, 
                success=False,
                timestamp__gte=time_threshold
            ).count()
            
            if fail_count >= 5:
                return JsonResponse({
                    'success': False, 
                    'message': 'Account temporarily locked. Please wait.'
                }, status=403)

            # 3. GET OR CREATE (Fixes the "User does not exist" loop for valid Firebase users)
            # If the user passed Firebase Auth, we trust them. 
            user, created = User.objects.get_or_create(username=email, defaults={'email': email})
            
            # 4. Login
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            # 5. Clear Failures
            LoginAttempt.objects.filter(email=email, success=False).delete()
            LoginAttempt.objects.create(email=email, success=True, ip_address=request.META.get('REMOTE_ADDR'))
            
            return JsonResponse({'success': True})
        except Exception as e:
            print(f"Login Error: {e}")
            return JsonResponse({'success': False, 'message': 'Invalid Token'})