from django import template
from admin_panel.models import Notification

register = template.Library()


@register.simple_tag
def unread_notification_count(user):
    if not user or not user.is_authenticated:
        return 0
    return Notification.objects.filter(user=user, is_read=False).count()
