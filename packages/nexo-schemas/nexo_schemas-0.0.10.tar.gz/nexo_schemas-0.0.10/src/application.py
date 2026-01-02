import socket
from Crypto.PublicKey.RSA import RsaKey
from enum import StrEnum
from functools import cached_property
from pathlib import Path
from pydantic import BaseModel, Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated, ClassVar, Self, TypeVar, overload
from uuid import UUID
from nexo.enums.environment import Environment
from nexo.enums.system import SystemRole, ListOfSystemRoles
from nexo.enums.user import UserType
from nexo.types.boolean import OptBool
from nexo.types.dict import StrToAnyDict
from nexo.types.misc import BytesOrStr
from nexo.types.string import ListOfStrs, OptStr
from .mixins.identity import EntityIdentifier
from .operation.enums import ListOfOperationTypes
from .security.api_key import validate
from .security.authentication import SystemCredentials, SystemUser, SystemAuthentication
from .security.authorization import APIKeyAuthorization
from .security.enums import Domain
from .security.token import SystemToken


class Execution(StrEnum):
    CONTAINER = "container"
    DIRECT = "direct"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]


class ApplicationContext(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(extra="ignore")

    name: Annotated[str, Field(..., validation_alias="NAME")]
    environment: Annotated[Environment, Field(..., validation_alias="ENVIRONMENT")]
    service_key: Annotated[str, Field(..., validation_alias="SERVICE_KEY")]

    @computed_field
    @cached_property
    def instance_id(self) -> str:
        return socket.gethostname()

    @classmethod
    def new(cls) -> Self:
        return cls()  # type: ignore


OptApplicationContext = ApplicationContext | None


class ApplicationContextMixin(BaseModel):
    application_context: ApplicationContext = Field(
        default_factory=ApplicationContext.new,
        description="Application's context",
    )


class ApplicationSettings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(extra="ignore")

    @computed_field
    @cached_property
    def instance_id(self) -> str:
        return socket.gethostname()

    # Application related settings
    NAME: Annotated[str, Field(..., description="Application's name")]
    # Service related settings
    ENVIRONMENT: Annotated[Environment, Field(..., description="Environment")]
    SERVICE_KEY: Annotated[str, Field(..., description="Service's key")]
    SERVICE_NAME: Annotated[str, Field(..., description="Service's name")]

    @cached_property
    def context(self) -> ApplicationContext:
        return ApplicationContext(
            name=self.NAME, environment=self.ENVIRONMENT, service_key=self.SERVICE_KEY
        )

    CLIENT_ID: Annotated[UUID, Field(..., description="Client's ID")]
    CLIENT_SECRET: Annotated[UUID, Field(..., description="Client's Secret")]

    # Serving related settings
    EXECUTION: Annotated[
        Execution, Field(Execution.CONTAINER, description="Execution mode")
    ] = Execution.CONTAINER
    RELOAD: Annotated[OptBool, Field(None, description="Reload")] = None

    @cached_property
    def reload(self) -> bool:
        if self.RELOAD is not None:
            return self.RELOAD
        else:
            return (
                self.EXECUTION is Execution.DIRECT
                and self.ENVIRONMENT is Environment.LOCAL
            )

    HOST: Annotated[str, Field("127.0.0.1", description="Application's host")] = (
        "127.0.0.1"
    )
    PORT: Annotated[int, Field(8000, description="Application's port")] = 8000
    HOST_PORT: Annotated[int, Field(8000, description="Host's port")] = 8000

    @cached_property
    def port(self) -> int:
        if self.EXECUTION is Execution.DIRECT and self.ENVIRONMENT is Environment.LOCAL:
            return self.HOST_PORT
        else:
            return self.PORT

    DOCKER_NETWORK: Annotated[str, Field(..., description="Docker's network")]

    @model_validator(mode="before")
    def define_default_docker_network(cls, data: StrToAnyDict):
        if "DOCKER_NETWORK" not in data:
            data["DOCKER_NETWORK"] = data["NAME"]
        return data

    ROOT_PATH: Annotated[str, Field("", description="Application's root path")] = ""

    # Configuration related settings
    USE_LOCAL_CONFIG: Annotated[
        bool, Field(False, description="Whether to use locally stored config")
    ] = False
    CONFIG_PATH: Annotated[OptStr, Field(None, description="Config path")] = None

    @model_validator(mode="after")
    def validate_config_path(self) -> Self:
        if self.USE_LOCAL_CONFIG:
            if self.CONFIG_PATH is None:
                self.CONFIG_PATH = f"/etc/{self.NAME}/config/{self.SERVICE_KEY}/{self.ENVIRONMENT}.yaml"
            config_path = Path(self.CONFIG_PATH)
            if not config_path.exists() or not config_path.is_file():
                raise ValueError(
                    f"Config path '{self.CONFIG_PATH}' either did not exist or is not a file"
                )

        return self

    # Credential related settings
    GOOGLE_APPLICATION_CREDENTIALS: Annotated[
        str,
        Field(
            ...,
            description="Google application credential's file path",
        ),
    ]

    @model_validator(mode="before")
    def define_default_google_aplication_credentials(cls, data: StrToAnyDict):
        if "GOOGLE_APPLICATION_CREDENTIALS" not in data:
            name: str = data["NAME"]
            credentials = f"/etc/{name}/credentials/google-service-account.json"
            data["GOOGLE_APPLICATION_CREDENTIALS"] = credentials
        return data

    API_KEY: Annotated[str, Field(..., description="Maleo's API Key")]

    @model_validator(mode="after")
    def validate_api_key(self) -> Self:
        validate(self.API_KEY, self.NAME, self.ENVIRONMENT)
        return self

    @cached_property
    def authorization(self) -> APIKeyAuthorization:
        return APIKeyAuthorization(credentials=self.API_KEY)

    SA_ID: Annotated[int, Field(..., description="SA's ID", ge=1)]
    SA_UUID: Annotated[UUID, Field(..., description="SA's UUID")]
    SA_ROLES: Annotated[
        ListOfSystemRoles,
        Field([SystemRole.ADMINISTRATOR], description="SA's Roles", min_length=1),
    ] = [SystemRole.ADMINISTRATOR]
    SA_USERNAME: Annotated[str, Field(..., description="SA's Username")]
    SA_EMAIL: Annotated[str, Field(..., description="SA's Email")]

    @cached_property
    def authentication(self) -> SystemAuthentication:
        return SystemAuthentication(
            credentials=SystemCredentials(
                user=EntityIdentifier[UserType](
                    id=self.SA_ID, uuid=self.SA_UUID, type=UserType.SERVICE
                ),
                domain_roles=self.SA_ROLES,
                scopes=["authenticated"]
                + [f"{Domain.SYSTEM}:{role.value}" for role in self.SA_ROLES],
            ),
            user=SystemUser(display_name=self.SA_USERNAME, identity=self.SA_EMAIL),
        )

    @property
    def token(self) -> SystemToken:
        return SystemToken.new(sub=self.SA_UUID)

    @overload
    def generate_token_string(
        self,
        key: RsaKey,
    ) -> str: ...
    @overload
    def generate_token_string(
        self,
        key: BytesOrStr,
        *,
        password: OptStr = None,
    ) -> str: ...
    def generate_token_string(
        self,
        key: BytesOrStr | RsaKey,
        *,
        password: OptStr = None,
    ) -> str:
        return self.token.to_string(key, password=password)

    # Infra related settings
    PUBLISH_HEARTBEAT: Annotated[
        OptBool, Field(None, description="Whether to publish heartbeat")
    ] = None

    @cached_property
    def publish_heartbeat(self) -> bool:
        if self.PUBLISH_HEARTBEAT is not None:
            return self.PUBLISH_HEARTBEAT
        else:
            return self.ENVIRONMENT in (Environment.STAGING, Environment.PRODUCTION)

    PUBLISH_RESOURCE_MEASUREMENT: Annotated[
        OptBool, Field(None, description="Whether to publish resource measurement")
    ] = None

    @cached_property
    def publish_resource_measurement(self) -> bool:
        if self.PUBLISH_RESOURCE_MEASUREMENT is not None:
            return self.PUBLISH_RESOURCE_MEASUREMENT
        else:
            return self.ENVIRONMENT in (Environment.STAGING, Environment.PRODUCTION)

    # Operation related settings
    PUBLISHABLE_OPERATIONS: Annotated[
        ListOfOperationTypes, Field([], description="Publishable operations")
    ] = []

    # Security related settings
    USE_LOCAL_KEY: Annotated[
        bool, Field(False, description="Whether to use locally stored key")
    ] = False
    PRIVATE_KEY_PASSWORD: Annotated[
        OptStr, Field(None, description="Private key's password")
    ] = None
    PRIVATE_KEY_PATH: Annotated[str, Field(..., description="Private key's path")]

    @model_validator(mode="before")
    def define_default_private_key_path(cls, data: StrToAnyDict):
        if "PRIVATE_KEY_PATH" not in data:
            name: str = data["NAME"]
            keys = f"/etc/{name}/keys/private.pem"
            data["PRIVATE_KEY_PATH"] = keys
        return data

    PUBLIC_KEY_PATH: Annotated[str, Field(..., description="Public key's path")]

    @model_validator(mode="before")
    def define_default_public_key_path(cls, data: StrToAnyDict):
        if "PUBLIC_KEY_PATH" not in data:
            name: str = data["NAME"]
            keys = f"/etc/{name}/keys/public.pem"
            data["PUBLIC_KEY_PATH"] = keys
        return data

    @model_validator(mode="after")
    def validate_keys_path(self) -> Self:
        if self.USE_LOCAL_KEY:
            private_key_path = Path(self.PRIVATE_KEY_PATH)
            if not private_key_path.exists() or not private_key_path.is_file():
                raise ValueError(
                    f"Private key path: '{self.PRIVATE_KEY_PATH}' either did not exist or is not a file"
                )

            public_key_path = Path(self.PUBLIC_KEY_PATH)
            if not public_key_path.exists() or not public_key_path.is_file():
                raise ValueError(
                    f"Public key path: '{self.PUBLIC_KEY_PATH}' either did not exist or is not a file"
                )

        return self


ApplicationSettingsT = TypeVar("ApplicationSettingsT", bound=ApplicationSettings)
