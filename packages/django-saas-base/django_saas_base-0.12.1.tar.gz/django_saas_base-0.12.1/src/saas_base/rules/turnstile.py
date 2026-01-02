import requests
from rest_framework.request import Request
from saas_base.functions.ip import get_client_ip
from .base import Rule


class Turnstile(Rule):
    API_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
    DEFAULT_RESPONSE_FIELD = 'cf-turnstile-response'

    def bad_request(self, request: Request):
        token = self.get_response_field_value(request)
        if not token:
            return True

        secret = self.options.get('secret')
        ip = get_client_ip(request)
        data = {'secret': secret, 'remoteip': ip, 'response': token}
        resp = requests.post(self.API_URL, data=data, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return not data.get('success')
