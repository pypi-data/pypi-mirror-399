from email.utils import formataddr
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from saas_base.drf.views import Endpoint
from saas_base.settings import saas_settings
from saas_base.models import UserEmail
from saas_base.rules import check_rules
from saas_base.serializers.password import (
    PasswordForgetSerializer,
    PasswordResetSerializer,
)
from saas_base.tasks.send_mails import send_template_email

__all__ = [
    'PasswordForgotEndpoint',
    'PasswordResetEndpoint',
]


class PasswordForgotEndpoint(Endpoint):
    email_template_id = 'reset_password'
    email_subject = _('Password Reset Request')

    authentication_classes = []
    permission_classes = []
    throttle_classes = [AnonRateThrottle]
    serializer_class = PasswordForgetSerializer

    def post(self, request: Request):
        """Send a forgot password reset email code."""
        serializer: PasswordForgetSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj: UserEmail = serializer.save()

        # check bad request rules
        check_rules(saas_settings.RESET_PASSWORD_SECURITY_RULES, request)

        code = serializer.save_auth_code(obj.user_id)
        name = obj.user.get_full_name() or obj.user.get_username()
        recipients = [formataddr((name, obj.email))]
        send_template_email(
            template_id=self.email_template_id,
            subject=self.email_subject,
            recipients=recipients,
            context={'code': code, 'user': obj.user},
        )
        return Response(status=204)


class PasswordResetEndpoint(Endpoint):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [AnonRateThrottle]
    serializer_class = PasswordResetSerializer

    def post(self, request: Request):
        """Reset password of a user with the given code."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'next': settings.LOGIN_URL})
