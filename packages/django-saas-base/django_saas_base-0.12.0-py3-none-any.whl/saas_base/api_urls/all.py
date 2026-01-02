from django.urls import path, include
from ..endpoints.permissions import PermissionListEndpoint
from ..endpoints.roles import RoleListEndpoint
from ..endpoints.tenant import SelectedTenantEndpoint

urlpatterns = [
    path('permissions/', PermissionListEndpoint.as_view()),
    path('roles/', RoleListEndpoint.as_view()),
    path('tenant/', SelectedTenantEndpoint.as_view()),
    path('user/', include('saas_base.api_urls.user')),
    path('user/emails/', include('saas_base.api_urls.user_emails')),
    path('user/members/', include('saas_base.api_urls.user_members')),
    path('tenants/', include('saas_base.api_urls.tenants')),
    path('groups/', include('saas_base.api_urls.groups')),
    path('members/', include('saas_base.api_urls.members')),
    path('session/', include('saas_base.api_urls.session')),
]
