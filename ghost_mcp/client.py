"""Ghost Admin API client."""

from datetime import datetime, timezone

import httpx
import jwt


class GhostAPIError(Exception):
    """Ghost API error."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Ghost API Error {status_code}: {message}")


class GhostClient:
    """Ghost Admin API client with JWT authentication."""

    def __init__(self, url: str, admin_key: str):
        parts = admin_key.split(":")
        if len(parts) != 2:
            raise ValueError("Invalid API key format. Expected: {id}:{secret}")
        self.base_url = f"{url.rstrip('/')}/ghost/api/admin"
        self.key_id = parts[0]
        self.key_secret = bytes.fromhex(parts[1])
        self._client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=False,
        )

    def _generate_token(self) -> str:
        """Generate a short-lived JWT token for Ghost Admin API."""
        now = int(datetime.now(timezone.utc).timestamp())
        payload = {"iat": now, "exp": now + 300, "aud": "/admin/"}
        return jwt.encode(
            payload,
            self.key_secret,
            algorithm="HS256",
            headers={"kid": self.key_id},
        )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Ghost {self._generate_token()}",
            "Accept-Version": "v5.0",
            "Content-Type": "application/json",
        }

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._headers()
        if "files" in kwargs:
            del headers["Content-Type"]
        response = await self._client.request(method, url, headers=headers, **kwargs)
        if response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("errors", [{}])[0].get("message", response.text)
            except Exception:
                message = response.text
            raise GhostAPIError(response.status_code, message)
        if response.status_code == 204:
            return {}
        return response.json()

    async def get(self, endpoint: str, params: dict | None = None) -> dict:
        return await self._request("GET", endpoint, params=params)

    async def post(self, endpoint: str, data: dict | None = None, files=None) -> dict:
        if files:
            return await self._request("POST", endpoint, files=files)
        return await self._request("POST", endpoint, json=data)

    async def put(self, endpoint: str, data: dict) -> dict:
        return await self._request("PUT", endpoint, json=data)

    async def delete(self, endpoint: str) -> dict:
        return await self._request("DELETE", endpoint)

    async def close(self):
        await self._client.aclose()
