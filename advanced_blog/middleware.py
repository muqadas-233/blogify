import time
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model

User = get_user_model()


class UserActivityMiddleware(MiddlewareMixin):
    """
    Simple middleware to track last activity timestamp on authenticated users.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            User.objects.filter(pk=request.user.pk).update(
                last_login=time.strftime("%Y-%m-%d %H:%M:%S")
            )
        return None
