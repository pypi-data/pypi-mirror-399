from django.urls import path
from ..endpoints.tenant import (
    TenantListEndpoint,
    TenantItemEndpoint,
)

urlpatterns = [
    path('', TenantListEndpoint.as_view()),
    path('<pk>/', TenantItemEndpoint.as_view()),
]
