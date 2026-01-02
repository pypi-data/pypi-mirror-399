from django.urls import path
from ..endpoints.password import (
    PasswordResetEndpoint,
    PasswordForgotEndpoint,
)
from ..endpoints.auth import (
    LogoutEndpoint,
    PasswordLogInEndpoint,
    SignupRequestEndpoint,
    SignupConfirmEndpoint,
    SignupWithInvitationEndpoint,
    InvitationEndpoint,
)


urlpatterns = [
    path('logout/', LogoutEndpoint.as_view()),
    path('login/', PasswordLogInEndpoint.as_view()),
    path('signup/request/', SignupRequestEndpoint.as_view()),
    path('signup/confirm/', SignupConfirmEndpoint.as_view()),
    path('signup/via/<pk>/', SignupWithInvitationEndpoint.as_view()),
    path('password/forgot/', PasswordForgotEndpoint.as_view()),
    path('password/reset/', PasswordResetEndpoint.as_view()),
    path('invitation/<pk>/', InvitationEndpoint.as_view()),
]
