import os

from davidkhala.gcp.auth import OptionsInterface, default
from davidkhala.gcp.auth.api_key import from_api_key
from davidkhala.gcp.auth.service_account import from_service_account


def credential() -> OptionsInterface:
    private_key = os.environ.get('PRIVATE_KEY')
    api_key = os.environ.get('API_KEY')
    r = OptionsInterface()
    if api_key:
        r.client_options = from_api_key(api_key)
    else:
        if private_key:
            r = from_service_account(
                client_email=os.environ.get('CLIENT_EMAIL'),
                private_key=os.environ.get('PRIVATE_KEY')
            )
        else:
            r = default()
        OptionsInterface.token.fget(r)
    return r
