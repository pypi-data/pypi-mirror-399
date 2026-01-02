import typing as t
from .rules import Rule

class TypedSite(t.TypedDict):
    name: str
    url: str
    icon: str
    copyright: str

class TypedProvider(t.TypedDict):
    backend: str
    options: t.Dict[str, t.Any]

class Settings:
    SITE: TypedSite
    TENANT_ID_HEADER: str
    CLIENT_IP_HEADERS: t.Optional[t.List[str]]

    PERMISSION_NAME_FORMATTER: str
    DEFAULT_REGION: str
    DEFAULT_FROM_EMAIL: t.Optional[str]

    SIGNUP_SECURITY_RULES: t.List[Rule]
    SIGNUP_REQUEST_CREATE_USER: bool
    RESET_PASSWORD_SECURITY_RULES: t.List[Rule]
    MEMBER_INVITE_LINK: str
    MEMBER_PERMISSION_MANAGERS: t.List[t.Literal['permissions', 'groups', 'role']]

    # internal properties
    settings_key: str
    user_settings: t.Dict[str, t.Any]
    _cached_attrs: t.Set[str]

    def __init__(
        self,
        settings_key: t.Optional[str] = 'SAAS',
        user_settings: t.Optional[t.Dict[str, t.Any]] = None,
        defaults: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> 'Settings': ...
    def reload(self, value: t.Optional[t.Dict[str, t.Any]] = None): ...
    def listen_setting_changed(self, setting: str, **kwargs): ...

def perform_import_provider(data: TypedProvider): ...
def perform_import(val: t.Union[t.List[TypedProvider], t.Dict[str, TypedProvider], TypedProvider]): ...

saas_settings: Settings
