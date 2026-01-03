from .http import HttpClient
from .accounts import AccountsClient
from .keys import KeysClient
from .groups import GroupsClient

class Client:
    def __init__(self, base_url: str, token: str | None = None, api_key: str | None = None):
        self.http = HttpClient(base_url=base_url, api_key=api_key)
        self.token = token
        self.api_key = api_key

        self.accounts = AccountsClient(self.http)
        self.keys = KeysClient(self)
        self.groups = GroupsClient(self.http)

    def set_token(self, token: str | None):
        self.token = token
        self.http.set_token(token)

    def set_api_key(self, api_key: str | None):
        self.api_key = api_key
        self.http.set_api_key(api_key)