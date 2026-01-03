import urllib.parse
import urllib.request


class SignalgridError(Exception):
    pass


class Client:
    def __init__(self, client_key: str, endpoint: str = "https://api.signalgrid.co"):
        if not client_key:
            raise SignalgridError("Client key is required")

        self.client_key = client_key
        self.endpoint = endpoint

    def send(self, payload: dict) -> dict:
        if "channel" not in payload:
            raise SignalgridError("Channel token is required")

        data = payload.copy()
        data["client_key"] = self.client_key

        encoded = urllib.parse.urlencode(data).encode("utf-8")

        req = urllib.request.Request(
            self.endpoint,
            data=encoded,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode()
        except Exception as e:
            raise SignalgridError(str(e))