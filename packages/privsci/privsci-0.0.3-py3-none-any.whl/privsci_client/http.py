import requests

class HttpClient:
    def __init__(self, base_url: str, token: str | None = None, api_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.api_key = api_key

    def set_token(self, token: str | None):
        self.token = token

    def set_api_key(self, api_key: str | None):
        self.api_key = api_key

    def _headers(self, use_api_key=False):
        headers = {"Content-Type": "application/json"}
        if use_api_key and self.api_key:
            headers["X-API-Key"] = self.api_key
        elif self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def post(self, path: str, json=None, use_api_key=False):
        url = f"{self.base_url}{path}"
        res = requests.post(url, json=json, headers=self._headers(use_api_key))
        self._handle_errors(res)
        return res.json()

    def get(self, path: str, use_api_key=False):
        url = f"{self.base_url}{path}"
        res = requests.get(url, headers=self._headers(use_api_key))
        self._handle_errors(res)
        return res.json()

    def _handle_errors(self, res):
        if not res.ok:
            try:
                raise Exception(res.json())
            except ValueError:
                res.raise_for_status()
