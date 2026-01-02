from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth import login, logout
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.exceptions import NotFound
from saas_base.models import Member
from saas_base.drf.views import Endpoint
from saas_base.settings import saas_settings
from saas_base.rules import check_rules
from saas_base.serializers.auth import (
    EmailCode,
    SignupRequestCodeSerializer,
    SignupCreateUserSerializer,
    SignupConfirmCodeSerializer,
    SignupConfirmPasswordSerializer,
    SignupWithInvitationSerializer,
)
from saas_base.serializers.member import InvitationInfoSerializer
from saas_base.serializers.password import PasswordLoginSerializer
from saas_base.signals import after_signup_user, after_login_user
from saas_base.tasks.send_mails import send_template_email


__all__ = [
    'SignupRequestEndpoint',
    'SignupConfirmEndpoint',
    'SignupWithInvitationEndpoint',
    'PasswordLogInEndpoint',
    'LogoutEndpoint',
    'InvitationEndpoint',
]


class SignupRequestEndpoint(Endpoint):
    email_template_id = 'signup_code'
    email_subject = _('Signup Request')
    authentication_classes = []
    permission_classes = []
    throttle_classes = [AnonRateThrottle]

    def get_serializer_class(self):
        if saas_settings.SIGNUP_REQUEST_CREATE_USER:
            return SignupCreateUserSerializer
        return SignupRequestCodeSerializer

    def post(self, request: Request):
        """Send a sign-up code to user's email address."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj: EmailCode = serializer.save()
        # check bad request rules
        check_rules(saas_settings.SIGNUP_SECURITY_RULES, request)

        send_template_email(
            template_id=self.email_template_id,
            subject=self.email_subject,
            recipients=[obj.recipient()],
            context={'code': obj.code},
        )
        return Response(status=204)


class _BaseSignupConfirmEndpoint(Endpoint):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [AnonRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        """Register a new user and login."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # update related membership
        Member.objects.filter(email=user.email).update(user=user, status=Member.InviteStatus.WAITING)
        after_signup_user.send(
            self.__class__,
            user=user,
            request=request,
            strategy='password',
        )
        return Response({'next': settings.LOGIN_REDIRECT_URL})


class SignupConfirmEndpoint(_BaseSignupConfirmEndpoint):
    def get_serializer_class(self):
        if saas_settings.SIGNUP_REQUEST_CREATE_USER:
            return SignupConfirmCodeSerializer
        return SignupConfirmPasswordSerializer


class SignupWithInvitationEndpoint(_BaseSignupConfirmEndpoint):
    serializer_class = SignupWithInvitationSerializer
    queryset = Member.objects.all()

    def get_serializer_context(self):
        obj: Member = self.get_object()
        # only allow signup with "request" status
        if obj.status == Member.InviteStatus.REQUEST:
            context = super().get_serializer_context()
            context['member'] = obj
            return context
        raise NotFound()


class PasswordLogInEndpoint(Endpoint):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [AnonRateThrottle]
    serializer_class = PasswordLoginSerializer

    def post(self, request: Request):
        """Login a user with the given username and password."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request._request, user)

        after_login_user.send(
            self.__class__,
            user=user,
            request=request,
            strategy='password',
        )
        return Response({'next': settings.LOGIN_REDIRECT_URL})


class LogoutEndpoint(Endpoint):
    authentication_classes = []
    permission_classes = []

    def post(self, request: Request):
        """Clear the user session and log the user out."""
        logout(request._request)
        return Response({'next': settings.LOGIN_URL})


class InvitationEndpoint(Endpoint):
    authentication_classes = []
    permission_classes = []
    serializer_class = InvitationInfoSerializer
    queryset = Member.objects.all()

    def get(self, request: Request, *args, **kwargs):
        """Retrieve a pending membership invitation."""
        obj: Member = self.get_object()
        if obj.status == Member.InviteStatus.ACTIVE:
            raise NotFound()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
