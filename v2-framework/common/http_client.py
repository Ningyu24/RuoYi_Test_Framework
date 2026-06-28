# common/http_client.py
import requests
from config.settings import Config

class HttpClient:
    _token = None

    @classmethod
    def get_token(cls):
        if cls._token is None:
            url = f"{Config.BASE_URL}/login"
            payload = {"username": Config.LOGIN_USER, "password": Config.LOGIN_PASSWORD}
            resp = requests.post(url, json=payload)
            assert resp.status_code == 200
            cls._token = resp.json().get("token")
            assert cls._token is not None, "获取 Token 失败"
        return cls._token

    @classmethod
    def post(cls, endpoint, **kwargs):
        """发送 POST 请求，自动带上 Token"""
        url = f"{Config.BASE_URL}{endpoint}"
        token = cls.get_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        # 如果调用方传了 headers，合并进去
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        # 直接透传所有参数给 requests.post
        return requests.post(url, headers=headers, **kwargs)
