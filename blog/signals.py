from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Post


@receiver(post_save, sender=Post)
def notify_on_publish(sender, instance, created, **kwargs):
    if instance.status == "published":
        subject = f"Post published: {instance.title}"
        message = f"Your post '{instance.title}' has been published."
        recipient_list = [instance.author.email]
        if instance.author.email:
            send_mail(
                subject,
                message,
                getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list,
                fail_silently=True,
            )
