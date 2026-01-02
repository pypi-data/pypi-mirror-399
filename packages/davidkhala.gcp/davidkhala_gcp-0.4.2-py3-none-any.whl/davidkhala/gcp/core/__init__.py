from google.cloud.client import ClientWithProject

from davidkhala.gcp.auth import OptionsInterface


class Client(ClientWithProject):
    @staticmethod
    def from_options(options: OptionsInterface):
        return Client(
            options.project, options.credentials, options.client_options
        )
