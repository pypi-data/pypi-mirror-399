import asyncio
import datetime
from typing import Optional, Union
from uuid import UUID

import pyotp

from .client import VaultWardenClient
from .crypto import decrypt, decrypt_text, encrypt
from .exceptions import VaultItemNotFound
from .models import SyncData, Creds, Cipher, CustomField


class VaultWarden:

    def __init__(
            self,
            url: str,
            email: str,
            password: str,
            client_id: str,
            client_secret: str,
            device_id: UUID,
    ):
        self._sync_data: SyncData = None
        self._org_keys = {}
        self._client = VaultWardenClient(url, email, password, client_id, client_secret, device_id)

    async def sync_vault(self, force_refresh: bool = False) -> SyncData:
        """
        Sync with vault
        """
        if self._sync_data is None or force_refresh:
            self._sync_data: SyncData = await self._client.sync_vault(force_refresh)
            for org in self._sync_data.Profile.Organizations:
                self._org_keys[org.Id] = decrypt(org.Key, self._client.connect_token.orgs_key)
        return self._sync_data

    def _get_org_id(self, id_or_name: str) -> Optional[UUID]:
        """
        try to find organisation by name or id
        """
        for org in self._sync_data.Profile.Organizations:
            if str(org.Id) == id_or_name or org.Name == id_or_name:
                return org.Id
        return None

    def _get_collection_id(self, id_or_name: str, org_id: UUID = None) -> Optional[UUID]:
        for collection in self._sync_data.Collections:
            if org_id is not None and collection.OrganizationId != org_id:
                continue
            collection_name = decrypt_text(
                collection.Name,
                self._org_keys.get(collection.OrganizationId)
            )
            if str(collection.Id) == id_or_name or collection_name == id_or_name:
                return collection.Id
        return None

    def _extract_creds(self, item: Cipher):
        org_key = self._org_keys.get(item.OrganizationId)

        password = decrypt_text(item.Login.Password, org_key)
        username = decrypt_text(item.Login.Username, org_key)

        uri = None
        if item.Login.Uri:
            uri = decrypt_text(item.Login.Uri, org_key)

        topt = None
        totp_secret = None
        if item.Login.Totp:
            totp_secret = decrypt_text(item.Login.Totp, org_key)
            totp = pyotp.TOTP(totp_secret)
            topt = totp.now()

        custom_fields = None
        if item.Fields:
            custom_fields = []
            for field in item.Fields:
                value = None
                if field.Value:
                    value = decrypt_text(field.Value, org_key)
                custom_fields.append(
                    CustomField(
                        LinkedId=field.LinkedId,
                        Type=field.Type,
                        Name=decrypt_text(field.Name, org_key),
                        Value=value
                    )
                )
        return Creds(
            item_id=str(item.Id),
            username=username,
            password=password,
            topt=topt,
            totp_secret=totp_secret,
            uri=uri,
            custom_fields=custom_fields
        )

    async def creds_by_name(
            self,
            record_name,
            organisation: str = None,
            collection: str = None,
            force_refresh: bool = False
    ) -> Creds:
        """
        It will return the first found credits with the same name.
        If the name is not unique, you should additionally specify the collection or|and organization.
        """
        await self.sync_vault(force_refresh)

        org_id = None
        collection_id = None

        if organisation:
            org_id = self._get_org_id(organisation)
        if collection:
            collection_id = self._get_collection_id(collection, org_id)

        for item in self._sync_data.Ciphers:
            if org_id is not None and org_id != item.OrganizationId:
                continue
            if collection_id is not None and collection_id not in item.CollectionIds:
                continue

            item_name = decrypt_text(item.Name, self._org_keys[item.OrganizationId])
            if item_name == record_name:
                return self._extract_creds(item)

        raise VaultItemNotFound(f'Item with name={record_name} not found')

    async def creds_by_id(self, item_id: Union[str, UUID], force_refresh: bool = False) -> Creds:
        """
        get creds by ID
        you can find the ItemId in the url path in the web version of the VaultWarden.
        """
        await self.sync_vault(force_refresh)

        if isinstance(item_id, str):
            item_id = UUID(item_id)

        for item in self._sync_data.Ciphers:
            if item.Id == item_id:
                return self._extract_creds(item)

        raise VaultItemNotFound(f'Item with id={item_id} not found')

    async def get_totp_by_id(self, item_id: Union[str, UUID]) -> Optional[str]:
        """
        Return the current TOTP code for the given credential ID without forcing a resync.
        Assumes an initial sync has occurred to have keys and ciphers; loads once if needed.
        """
        if self._sync_data is None:
            await self.sync_vault(False)

        if isinstance(item_id, str):
            item_id = UUID(item_id)

        for item in self._sync_data.Ciphers:
            if item.Id == item_id:
                org_key = self._org_keys.get(item.OrganizationId)
                if not item.Login or not item.Login.Totp:
                    return None
                secret = decrypt_text(item.Login.Totp, org_key)
                totp = pyotp.TOTP(secret)
                return totp.now()
        return None

    async def change_password(self, item_id: Union[str, UUID], new_password: str):
        """
        Change password in item
        """
        if isinstance(item_id, str):
            item_id = UUID(item_id)

        for elm in self._sync_data.Ciphers:
            if elm.Id == item_id:
                item = elm
                break
        else:
            raise VaultItemNotFound(f'Item with id={item_id} not found')

        put_json = self._prepare_put_body(item.OrganizationId, item.to_export_format(), new_password)

        await self._client.cipher_vault(item_id, put_json)

        await self.sync_vault(True)

    def _prepare_put_body(self, org_id: UUID, item: dict, new_password) -> dict:
        org_key = self._org_keys.get(org_id)

        item['Login']['Password'] = encrypt(2, new_password, org_key)
        item['Login']['PasswordRevisionDate'] = str(datetime.datetime.now())

        return item

    def creds_by_name_sync(
            self,
            record_name: str,
            organisation: str = None,
            collection: str = None,
            force_refresh: bool = False
    ) -> Creds:
        """
        It will return the first found credits with the same name.
        If the name is not unique, you should additionally specify the collection or|and organization.
        """
        return asyncio.run(
            self.creds_by_name(record_name, organisation, collection, force_refresh)
        )

    def get_creds_by_id_sync(self, item_id: Union[str, UUID], force_refresh: bool = False) -> Creds:
        """
        get creds by ID
        you can find the ItemId in the url path in the web version of the VaultWarden.
        """
        return asyncio.run(self.creds_by_id(item_id, force_refresh))
