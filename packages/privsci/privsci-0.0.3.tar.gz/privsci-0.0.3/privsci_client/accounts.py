from .config_store import load_config, save_config

class AccountsClient:
    def __init__(self, http):
        self.http = http

    def login(self, email: str, password: str):
        resp = self.http.post("/accounts/api/login", json={
            "email": email,
            "password": password
        })

        cfg = load_config()
        cfg["token"] = resp["access_token"]
        save_config(cfg)

        return {
            "ok": True,
            **resp
        }

    def logout(self):
        had_token = bool(self.http.token)
        
        cfg = load_config()
        cfg.pop("token", None)
        save_config(cfg)

        return {
            "ok": True,
            "message": "Logged out." if had_token else "No active session.",
            "token_cleared": had_token,
        }
