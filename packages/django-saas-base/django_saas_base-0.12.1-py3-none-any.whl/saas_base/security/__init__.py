import warnings
from saas_base.rules import check_rules as check_security_rules
from .rules import Rule, BlockedEmailDomains, TooManyDots, Turnstile

warnings.warn('saas_base.security is deprecated, use saas_base.rules instead', DeprecationWarning)

__all__ = [
    'Rule',
    'BlockedEmailDomains',
    'TooManyDots',
    'Turnstile',
    'check_security_rules',
]
