from django.db import models
from django.utils import timezone
import datetime

# 1. To store the temporary OTP codes (For HTML Step 1 & 2)
class EmailVerification(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)  # Becomes True after Step 2

    def is_expired(self):
        # expire after 5 minutes (even though frontend says 60s for resend)
        return timezone.now() > self.created_at + datetime.timedelta(minutes=5)

    def __str__(self):
        return f"{self.email} - {self.otp_code}"

# 2. To track login history (Good for security)
class LoginAttempt(models.Model):
    email = models.EmailField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.timestamp}"