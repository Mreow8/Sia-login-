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
from .models import EmailVerification, LoginAttempt
from firebase_admin import auth

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

# --- REGISTRATION & OTP SECTION ---

@csrf_exempt
def send_email_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get('email')
        
        if User.objects.filter(email=email).exists():
             return JsonResponse({'status': 'error', 'message': 'Email already registered. Please login.'})

        otp = str(random.randint(100000, 999999))
        
        EmailVerification.objects.update_or_create(
            email=email,
            defaults={'otp_code': otp, 'is_verified': False, 'created_at': timezone.now()}
        )
        
        try:
            send_mail(
                'Verification Code',
                f'Your code is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return JsonResponse({'status': 'success', 'message': 'Code sent!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

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
            
            decoded_token = auth.verify_id_token(token)
            email = decoded_token['email']

            if User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'error', 'message': 'User already exists'})

            User.objects.create_user(username=email, email=email)
            
            return JsonResponse({'status': 'success', 'message': 'Account created'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error'}, status=405)

# --- LOGIN & SECURITY SECTION ---

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
                # We check if user exists before alerting to prevent spam on non-users
                if User.objects.filter(email=identifier).exists():
                    try:
                        email_body = (
                            f"Hello,\n\n"
                            f"We noticed 3 failed login attempts on your account.\n"
                            f"IP Address: {ip}\n"
                            f"Time: {timezone.now()}"
                        )
                        send_mail(
                            subject="Security Alert",
                            message=email_body,
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[identifier],
                            fail_silently=False, 
                        )
                        response['alert'] = "Email alert sent."
                    except Exception:
                        pass

            if recent_failures >= 5:
                response['status'] = 'blocked'
                response['message'] = 'Too many attempts.'

            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)

@csrf_exempt
def handle_email_login(request):
    if request.method == "POST":
        data = json.loads(request.body)
        token = data.get('token')

        try:
            # 1. Verify Token
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