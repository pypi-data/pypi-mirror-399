from .config_store import load_config, save_config

class KeysClient:
    def __init__(self, client):
        self.client = client
        self.http = client.http

    def generate_key(self, key_name):
        resp = self.http.post("/keys/api/generate_key", json={"key_name": key_name})
        return resp

    def revoke_key(self, key_id):
        resp = self.http.post("/keys/api/revoke_key", json={"key_id": key_id})

        cfg = load_config()
        if cfg["api_key"] == key_id: 
            cfg["api_key"] = None
        save_config(cfg)
        return resp