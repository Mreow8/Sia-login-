import sib_api_v3_sdk
from sib_api_v3_sdk.api.transactional_emails_api import TransactionalEmailsApi
from sib_api_v3_sdk.rest import ApiException
from decouple import config

def send_email(subject, html_content, to_emails, sender_name=None, sender_email=None):
    """
    Sends an email using Brevo (Sendinblue) API.
    - subject: Email subject
    - html_content: HTML content of the email
    - to_emails: single email string or list of emails
    - sender_name: optional sender name
    - sender_email: optional sender email (default from .env)
    Returns: api_response object on success, None on failure
    """
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = config('BREVO_API_KEY')

    api_instance = TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Sender info
    sender = {
        "name": sender_name or config('BREVO_SENDER_NAME', default='SIA Project'),
        "email": sender_email or config('EMAIL_HOST_USER')
    }

    # Recipient(s)
    if isinstance(to_emails, str):
        to = [{"email": to_emails}]
    else:
        to = [{"email": email} for email in to_emails]

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        sender=sender,
        subject=subject,
        html_content=html_content
    )

    try:
        response = api_instance.send_transac_email(send_smtp_email)
        print(f"✅ Email sent successfully! Message ID: {response.message_id}")
        return response
    except ApiException as e:
        print(f"❌ Exception when sending email: {e}")
        return None
