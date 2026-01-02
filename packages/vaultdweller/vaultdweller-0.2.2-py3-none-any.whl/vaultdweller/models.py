import time
from datetime import datetime
from enum import IntEnum
from typing import Optional
from uuid import UUID

import pyotp
from pydantic import BaseModel, field_validator, AliasChoices, Field

from .crypto import decrypt


def _datetime_parser(value):
    if isinstance(value, str):
        # 2025-12-17T13:02:50.840000+00:00Z
        if value.endswith('Z') and '+' in value:
            # 2025-12-17T13:02:50.840000+00:00Z
            value = value.replace('Z', '')  # Убираем Z
        try:
            return datetime.fromisoformat(value.replace('Z', ''))
        except ValueError:
            try:
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                try:
                    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    raise ValueError(f"Can't pase datetime: {value}")
    return value


class VaultwardenUserStatus(IntEnum):
    Enabled = 0
    Invited = 1
    Disabled = 2


class PermissiveBaseModel(
    BaseModel,
    extra="allow",
    alias_generator=lambda x: x[0].lower() + x[1:],
    populate_by_name=True,
    arbitrary_types_allowed=True,
):
    pass


class ConnectToken(PermissiveBaseModel):
    Kdf: int = 0
    KdfIterations: int = 0
    KdfMemory: Optional[int] = None
    KdfParallelism: Optional[int] = None
    Key: str
    PrivateKey: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: int
    token_type: str
    scope: str
    unofficialServer: bool = False
    ResetMasterPassword: Optional[bool] = None
    master_key: Optional[bytes] = None

    @field_validator("expires_in")
    @classmethod
    def expires_in_to_time(cls, v):
        return time.time() + v

    def is_expired(self, now=None):
        if now is None:
            now = time.time()
        return (self.expires_in is not None) and (self.expires_in <= now)

    @property
    def user_key(self):
        return decrypt(self.Key, self.master_key)

    @property
    def orgs_key(self):
        return decrypt(self.PrivateKey, self.user_key)


class ProfileOrganization(PermissiveBaseModel):
    Id: UUID
    Name: str
    Key: Optional[str] = None
    ProviderId: Optional[str] = None
    ProviderName: Optional[str] = None
    ResetPasswordEnrolled: bool
    Seats: Optional[int] = None
    SelfHost: bool
    SsoBound: bool
    Status: int
    Type: int
    Use2fa: bool
    UseApi: bool
    UseDirectory: bool
    UseEvents: bool
    UseGroups: bool
    UsePolicies: bool
    UseResetPassword: bool
    UseSso: bool
    UseTotp: bool


class UserProfile(PermissiveBaseModel):
    AvatarColor: Optional[str]
    Culture: str
    Email: str
    EmailVerified: bool
    ForcePasswordReset: bool
    Id: UUID
    Key: str
    MasterPasswordHint: Optional[str]
    Name: str
    Object: Optional[str]
    Organizations: list[ProfileOrganization]
    Premium: bool
    PrivateKey: Optional[str]
    ProviderOrganizations: list
    Providers: list
    SecurityStamp: str
    TwoFactorEnabled: bool
    status: VaultwardenUserStatus = Field(
        validation_alias=AliasChoices("_status", "_Status")
    )


class CustomFieldType(IntEnum):
    text = 0
    hidden = 1
    boolean = 2
    linked = 3


class Collection(PermissiveBaseModel):
    ExternalId: Optional[UUID]
    HidePasswords: bool
    Id: Optional[UUID]
    Name: str
    Object: str
    OrganizationId: Optional[UUID]
    ReadOnly: bool


class CipherPasswordHistory(PermissiveBaseModel):
    LastUsedDate: Optional[datetime]
    Password: Optional[str]

    @field_validator('LastUsedDate', mode='before')
    @classmethod
    def parse_datetime(cls, value):
        _datetime_parser(value)
        return value


class CustomField(PermissiveBaseModel):
    LinkedId: Optional[int]
    Name: str
    Type: CustomFieldType
    Value: Optional[str]


class CipherData(PermissiveBaseModel):
    AutofillOnPageLoad: Optional[str]
    Fields: Optional[list[CustomField]]
    Name: str
    Notes: Optional[str]
    Password: Optional[str]
    PasswordHistory: Optional[list[CipherPasswordHistory]]
    PasswordRevisionDate: Optional[datetime]
    Totp: Optional[str]
    Uri: Optional[str]
    Uris: Optional[list]
    Username: Optional[str]

    @field_validator('PasswordRevisionDate', mode='before')
    @classmethod
    def parse_datetime(cls, value):
        _datetime_parser(value)
        return value


class CipherLogin(PermissiveBaseModel):
    AutofillOnPageLoad: Optional[str]
    Password: Optional[str]
    PasswordRevisionDate: Optional[datetime]
    Totp: Optional[str]
    Uri: Optional[str]
    Uris: Optional[list]
    Username: Optional[str]

    @field_validator('PasswordRevisionDate', mode='before')
    @classmethod
    def parse_datetime(cls, value):
        _datetime_parser(value)
        return value


class Cipher(PermissiveBaseModel):
    Attachments: Optional[list]
    Card: Optional[str]
    CollectionIds: list[UUID]
    CreationDate: datetime
    Data: CipherData
    DeletedDate: Optional[datetime]
    Edit: bool
    Favorite: bool
    Fields: Optional[list[CustomField]]
    FolderId: Optional[UUID]
    Id: UUID
    Identity: Optional[str]
    Key: Optional[str]
    Login: CipherLogin
    Name: str
    Notes: Optional[str]
    Object: str
    OrganizationId: Optional[UUID]
    OrganizationUseTotp: bool
    PasswordHistory: Optional[list[CipherPasswordHistory]]
    Reprompt: int
    RevisionDate: Optional[datetime]
    SecureNote: Optional[str]
    Type: int
    ViewPassword: bool

    def to_export_format(self) -> dict:
        """
        Hydrate the Cipher for the put request
        """

        login_source = self.Login or self.Data
        fields_source = self.Data.Fields if self.Data.Fields else self.Fields or []
        history_source = self.PasswordHistory if self.PasswordHistory else self.Data.PasswordHistory or []

        return {
            "Type": self.Type,
            "FolderId": str(self.FolderId) if self.FolderId else None,
            "OrganizationId": str(self.OrganizationId) if self.OrganizationId else None,
            "Name": self.Name,
            "Notes": self.Notes,
            "Favorite": self.Favorite,
            "LastKnownRevisionDate": str(self.RevisionDate),
            "Reprompt": self.Reprompt,
            "Login": {
                "Response": None,
                "Uris": login_source.Uris,
                "Username": login_source.Username,
                "Password": login_source.Password,
                "PasswordRevisionDate": str(login_source.PasswordRevisionDate),
                "Totp": login_source.Totp,
                "AutofillOnPageLoad": login_source.AutofillOnPageLoad,
            },
            "Fields": [
                {
                    "Response": None,
                    "Type": field.Type,
                    "Name": field.Name,
                    "Value": field.Value,
                    "LinkedId": field.LinkedId,
                }
                for field in fields_source
            ],
            "PasswordHistory": [
                {
                    "LastUsedDate": str(item.LastUsedDate),
                    "Password": item.Password,
                }
                for item in history_source
            ]
        }


class SyncData(PermissiveBaseModel):
    Ciphers: list[Cipher]
    Collections: list[Collection]
    Domains: Optional[dict]
    Folders: list[dict]
    Policies: list[dict]
    Profile: UserProfile
    Sends: list[dict]
    LastUpdate: datetime = datetime.now()


class Creds(BaseModel):
    item_id: str
    username: str
    password: str
    topt: Optional[str]
    totp_secret: Optional[str] = None
    uri: Optional[str]
    custom_fields: Optional[list[CustomField]]

    def get_current_totp(self) -> Optional[str]:
        if not self.totp_secret:
            return None
        return pyotp.TOTP(self.totp_secret).now()
