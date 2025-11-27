import json
import random
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt # Import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailVerification, LoginAttempt
from firebase_admin import auth # Make sure you have this

# mainapp/views.py
from django.conf import settings # Import settings

@ensure_csrf_cookie
def login_page(request):
    # Pass the config dictionary to the template
    context = {
        'firebase_config': settings.FIREBASE_CONFIG
    }
    return render(request, 'login.html', context)
# 2. Send OTP
@csrf_exempt  # Added to allow POST from JS without complex headers
def send_email_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get('email')
        
        # Create OTP
        otp = str(random.randint(100000, 999999))
        
        # Save locally
        EmailVerification.objects.update_or_create(
            email=email,
            defaults={'otp_code': otp, 'is_verified': False}
        )
        
        # Send Email
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

# 3. Verify OTP
@csrf_exempt
def verify_email_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get('email') # We need to receive this from JS now!
        otp = data.get('otp')

        try:
            record = EmailVerification.objects.get(email=email)
            if record.otp_code == otp and not record.is_expired():
                record.is_verified = True
                record.save()
                return JsonResponse({'status': 'success', 'message': 'Verified'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid Code'})
        except EmailVerification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})

# 4. Handle Login (Fixed to accept Firebase Token)
@csrf_exempt
def handle_email_login(request):
    if request.method == "POST":
        data = json.loads(request.body)
        token = data.get('token') # JS sends 'token', not password

        try:
            # Verify the token with Firebase
            decoded_token = auth.verify_id_token(token)
            email = decoded_token['email']
            
            # Log the success
            LoginAttempt.objects.create(email=email, success=True, ip_address=request.META.get('REMOTE_ADDR'))
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Invalid Token'})