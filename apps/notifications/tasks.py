from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(bind=True, max_retries=3)
def send_notification(self, user_id, message, notif_type="system", channel="in_app"):
    """
    Create an in-app notification and optionally send SMS / email.
    channel: 'in_app' | 'sms' | 'email' | 'both'
    """
    from django.contrib.auth import get_user_model
    from .models import Notification

    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    # Always create in-app record
    Notification.objects.create(
        user=user,
        type=notif_type,
        channel=channel,
        message=message,
    )

    # SMS via Africa's Talking
    if channel in ("sms", "both") and user.phone:
        try:
            import africastalking

            africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
            sms = africastalking.SMS
            sms.send(message, [user.phone], settings.AT_SENDER_ID)
        except Exception as exc:
            self.retry(exc=exc, countdown=60)

    # Email via SMTP
    if channel in ("email", "both") and user.email:
        try:
            send_mail(
                subject="Roommate Finder Notification",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as exc:
            self.retry(exc=exc, countdown=60)


@shared_task
def send_bulk_notification(user_ids, message, notif_type="system", channel="in_app"):
    """Send notifications to multiple users at once."""
    for uid in user_ids:
        send_notification.delay(uid, message, notif_type, channel)
    return f"Queued {len(user_ids)} notifications"
