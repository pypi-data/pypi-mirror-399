from typing import Literal, Optional
from uuid import UUID, uuid4

from httpx import Response, AsyncClient

from .crypto import make_master_key
from .exceptions import VaultWarderError
from .models import ConnectToken, SyncData


class VaultWardenClient:
    TOKEN_PATH = 'identity/connect/token'
    SYNC_PATH = 'api/sync'
    CIPHER_PATH = 'api/ciphers/'

    def __init__(
            self,
            url: str,
            email: str,
            password: str,
            client_id: str,
            client_secret: str,
            device_id: UUID = None,
            timeout: int = 30,
    ):
        # if one of the parameters is None, raise an exception
        if not all(
                [url, email, password, client_id, client_secret]
        ):
            raise VaultWarderError("All parameters are required")
        self.email = email
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.device_id = device_id or uuid4()
        self.url = url.strip("/")
        self._http_client = AsyncClient(
            base_url=f"{self.url}/",
            timeout=timeout,
        )
        self._connect_token: Optional[ConnectToken] = None
        self._sync: Optional[SyncData] = None

    @property
    def connect_token(self) -> Optional[ConnectToken]:
        """
        Getter
        """
        return self._connect_token

    @connect_token.setter
    def connect_token(self, value: ConnectToken):
        self._connect_token = value

    # refresh connect token if expired
    async def _refresh_connect_token(self):
        if (
                self.connect_token is None
                or self.connect_token.refresh_token is None
        ):
            await self._set_connect_token()
            return
        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=utf-8",
        }
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.connect_token.refresh_token,
        }
        resp = await self._http_client.post(
            self.TOKEN_PATH, headers=headers, data=payload
        )
        self._connect_token = ConnectToken.model_validate_json(resp.text)

        self._connect_token.master_key = make_master_key(
            password=self.password,
            salt=self.email,
            iterations=self._connect_token.KdfIterations,
        )

    async def _set_connect_token(self):
        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=utf-8",
        }
        payload = {
            "grant_type": "client_credentials",
            "client_secret": f"{self.client_secret}",
            "client_id": f"{self.client_id}",
            "scope": "api",
            # 21 for "SDK",
            # see https://github.com/bitwarden/server/blob/master/src/Core/Enums/DeviceType.cs
            "deviceType": 21,
            "deviceIdentifier": f"{self.device_id}",
            "deviceName": "python-vaultdweller",
        }
        resp = await self._http_client.post(
            "identity/connect/token", headers=headers, data=payload
        )
        self._connect_token = ConnectToken.model_validate_json(resp.text)
        self._connect_token.master_key = make_master_key(
            password=self.password,
            salt=self.email,
            iterations=self._connect_token.KdfIterations,
        )

    # login to api
    async def api_login(self) -> None:
        """
        Log in vaultwarden
        """
        if self.connect_token is not None:
            if self.connect_token.is_expired():
                await self._refresh_connect_token()
            return

        await self._set_connect_token()

    async def _api_request(
            self,
            method: Literal["GET", "POST", "DELETE", "PUT"],
            path: str,
            **kwargs,
    ) -> Response:
        await self.api_login()
        if self.connect_token is None:
            raise VaultWarderError("Fail to connect")
        headers = {
            "Authorization": f"Bearer {self.connect_token.access_token}",
            "content-type": "application/json; charset=utf-8",
            "Accept": "*/*",
        }
        return await self._http_client.request(
            method, path, headers=headers, **kwargs
        )

    async def sync_vault(self, force_refresh: bool = False) -> SyncData:
        """
        Sync data with vaultwarden
        """
        if self._sync is None or force_refresh:
            resp = await self._api_request("GET", self.SYNC_PATH)
            self._sync = SyncData.model_validate_json(resp.text)
        return self._sync

    async def cipher_vault(self, item_id, put_json):
        """
        Put edited item
        """
        await self._api_request('PUT', self.CIPHER_PATH + str(item_id), json=put_json)
