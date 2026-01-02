from google.api_core.client_options import ClientOptions as GCPClientOptions


def from_api_key(api_key: str, client_options: GCPClientOptions = None) -> GCPClientOptions:
    if client_options is None:
        client_options = GCPClientOptions()
    client_options.api_key = api_key
    return client_options
