from dataclasses import dataclass
from typing import TypedDict, NotRequired, Optional

from google.oauth2 import service_account

from davidkhala.gcp.auth import OptionsInterface, default_scopes


class ServiceAccount(OptionsInterface):
    credentials: service_account.Credentials

    @dataclass
    class Info(TypedDict):
        """
        The service account info in Google format.
        """
        client_email: str
        private_key: str
        token_uri: NotRequired[str]
        project_id: NotRequired[str]
        client_id: Optional[str]  # for Apache Spark pubsub
        private_key_id: Optional[str]  # for Apache Spark pubsub

    @staticmethod
    def assign(info: Info, project_id=None) -> Info:
        if project_id:
            info['project_id'] = project_id
        if not info.get('project_id'):
            info['project_id'] = info.get('client_email').split('@')[1].split('.')[0]
        info['token_uri'] = "https://oauth2.googleapis.com/token"
        return info


def from_service_account(info: ServiceAccount.Info = None,
                         *,
                         client_email=None, private_key=None, project_id=None, scopes=None
                         ) -> ServiceAccount:
    if scopes is None:
        scopes = default_scopes
    scopes = list(map(lambda scope: 'https://www.' + scope, scopes))
    if not info:
        info = ServiceAccount.Info(
            client_email=client_email,
            private_key=private_key,
            client_id=None,
            private_key_id=None,
        )
    info = ServiceAccount.assign(info, project_id)

    c = ServiceAccount()

    c.credentials = service_account.Credentials.from_service_account_info(
        info, scopes=scopes
    )
    c.project = info['project_id']
    return c
