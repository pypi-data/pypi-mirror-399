from abc import ABC, abstractmethod
from enum import StrEnum
from fastapi import status, HTTPException
from fastapi.requests import HTTPConnection
from functools import cached_property
from pydantic import BaseModel, Field
from starlette.authentication import (
    AuthCredentials as StarletteCredentials,
    BaseUser as StarletteUser,
)
from typing import (
    Annotated,
    Callable,
    Generic,
    Literal,
    Self,
    TypeGuard,
    TypeVar,
    overload,
)
from nexo.enums.organization import (
    OrganizationRole,
    ListOfOrganizationRoles,
    OrganizationType,
    OptOrganizationType,
)
from nexo.enums.medical import (
    MedicalRole,
    ListOfMedicalRoles,
    OptSeqOfMedicalRoles,
    OptListOfMedicalRoles,
    OptListOfMedicalRolesT,
)
from nexo.enums.system import SystemRole, ListOfSystemRoles
from nexo.enums.user import UserType, OptUserType
from nexo.types.integer import OptInt
from nexo.types.string import (
    OptStr,
    OptStrT,
    ListOfStrs,
    OptListOfStrs,
    OptSeqOfStrs,
)
from nexo.types.uuid import OptUUID
from nexo.utils.exception import extract_details
from ..mixins.identity import EntityIdentifier
from .enums import Domain, OptDomain, OptDomainT
from .types import (
    ListOfDomainRoles,
    OptListOfDomainRoles,
    OptListOfDomainRolesT,
    OptSeqOfDomainRoles,
)


class ConversionDestination(StrEnum):
    BASE = "base"
    AUTHENTICATED = "authenticated"
    TENANT = "tenant"
    SYSTEM = "system"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]


class RequestCredentials(StarletteCredentials):
    def __init__(
        self,
        domain: OptDomain = None,
        user_id: OptInt = None,
        user_uuid: OptUUID = None,
        user_type: OptUserType = None,
        organization_id: OptInt = None,
        organization_uuid: OptUUID = None,
        organization_type: OptOrganizationType = None,
        domain_roles: OptSeqOfDomainRoles = None,
        medical_roles: OptSeqOfMedicalRoles = None,
        scopes: OptSeqOfStrs = None,
    ):
        self.domain = domain

        if user_id is None and user_uuid is None and user_type is None:
            self.user = None
        elif user_id is not None and user_uuid is not None and user_type is not None:
            self.user = EntityIdentifier[UserType](
                id=user_id, uuid=user_uuid, type=user_type
            )
        else:
            raise ValueError(
                "Both 'user_id', 'user_uuid', and 'user_type' must either be None or not None"
            )

        if (
            organization_id is None
            and organization_uuid is None
            and organization_type is None
        ):
            self.organization = None
        elif (
            organization_id is not None
            and organization_uuid is not None
            and organization_type is not None
        ):
            self.organization = EntityIdentifier[OrganizationType](
                id=organization_id, uuid=organization_uuid, type=organization_type
            )
        else:
            raise ValueError(
                "Both 'organization_id', 'organization_uuid', and 'organization_type' must either be None or not None"
            )

        self.domain_roles: OptListOfDomainRoles = list(domain_roles) if domain_roles is not None else None  # type: ignore
        self.medical_roles: OptListOfMedicalRoles = (
            list(medical_roles) if medical_roles is not None else None
        )
        self.scopes: OptListOfStrs = list[str](scopes) if scopes is not None else None


class RequestUser(StarletteUser):
    def __init__(
        self,
        authenticated: bool = False,
        organization: OptStr = None,
        username: str = "",
        email: str = "",
    ) -> None:
        self._authenticated = authenticated
        self._organization = organization
        self._username = username
        self._email = email

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    @property
    def organization(self) -> OptStr:
        return self._organization

    @property
    def display_name(self) -> str:
        return self._username

    @property
    def identity(self) -> str:
        return self._email


UserT = TypeVar("UserT", bound=EntityIdentifier[UserType] | None)
OrganizationT = TypeVar(
    "OrganizationT", bound=EntityIdentifier[OrganizationType] | None
)
ScopesT = TypeVar("ScopesT", bound=OptListOfStrs)


class GenericCredentials(
    BaseModel,
    Generic[
        OptDomainT,
        UserT,
        OrganizationT,
        OptListOfDomainRolesT,
        OptListOfMedicalRolesT,
        ScopesT,
    ],
):
    domain: Annotated[OptDomainT, Field(..., description="Domain")]
    user: Annotated[UserT, Field(..., description="User")]
    organization: Annotated[OrganizationT, Field(..., description="Organization")]
    domain_roles: Annotated[
        OptListOfDomainRolesT, Field(..., description="Domain Roles")
    ]
    medical_roles: Annotated[
        OptListOfMedicalRolesT, Field(..., description="Medical roles")
    ]
    scopes: Annotated[ScopesT, Field(..., description="Scopes")]


class BaseCredentials(
    GenericCredentials[
        OptDomain,
        EntityIdentifier[UserType] | None,
        EntityIdentifier[OrganizationType] | None,
        OptListOfDomainRoles,
        OptListOfMedicalRoles,
        OptListOfStrs,
    ]
):
    domain: Annotated[OptDomain, Field(None, description="Domain")] = None
    user: Annotated[
        EntityIdentifier[UserType] | None, Field(None, description="User")
    ] = None
    organization: Annotated[
        EntityIdentifier[OrganizationType] | None,
        Field(None, description="Organization"),
    ] = None
    domain_roles: Annotated[
        OptListOfDomainRoles, Field(None, description="Domain Roles")
    ] = None
    medical_roles: Annotated[
        OptListOfMedicalRoles, Field(None, description="Medical roles")
    ] = None
    scopes: Annotated[OptListOfStrs, Field(None, description="Scopes")] = None


class AuthenticatedCredentials(
    GenericCredentials[
        Domain,
        EntityIdentifier[UserType],
        EntityIdentifier[OrganizationType] | None,
        ListOfDomainRoles,
        OptListOfMedicalRoles,
        ListOfStrs,
    ]
):
    domain: Annotated[Domain, Field(..., description="Domain")]
    user: Annotated[EntityIdentifier[UserType], Field(..., description="User")]
    organization: Annotated[
        EntityIdentifier[OrganizationType] | None,
        Field(..., description="Organization"),
    ]
    domain_roles: Annotated[
        ListOfDomainRoles, Field(..., description="Domain Roles", min_length=1)
    ]
    medical_roles: Annotated[
        OptListOfMedicalRoles, Field(..., description="Medical roles")
    ]
    scopes: Annotated[ListOfStrs, Field(..., description="Scopes", min_length=1)]


class TenantCredentials(
    GenericCredentials[
        Literal[Domain.TENANT],
        EntityIdentifier[UserType],
        EntityIdentifier[OrganizationType],
        ListOfOrganizationRoles,
        OptListOfMedicalRoles,
        ListOfStrs,
    ]
):
    domain: Literal[Domain.TENANT] = Domain.TENANT
    user: Annotated[EntityIdentifier[UserType], Field(..., description="User")]
    organization: Annotated[
        EntityIdentifier[OrganizationType], Field(..., description="Organization")
    ]
    domain_roles: Annotated[
        ListOfOrganizationRoles, Field(..., description="Domain Roles", min_length=1)
    ]
    medical_roles: Annotated[
        OptListOfMedicalRoles, Field(..., description="Medical roles")
    ]
    scopes: Annotated[ListOfStrs, Field(..., description="Scopes", min_length=1)]


class SystemCredentials(
    GenericCredentials[
        Literal[Domain.SYSTEM],
        EntityIdentifier[UserType],
        None,
        ListOfSystemRoles,
        None,
        ListOfStrs,
    ]
):
    domain: Literal[Domain.SYSTEM] = Domain.SYSTEM
    user: Annotated[EntityIdentifier[UserType], Field(..., description="User")]
    organization: Annotated[None, Field(None, description="Organization")] = None
    domain_roles: Annotated[
        ListOfSystemRoles, Field(..., description="Domain Roles", min_length=1)
    ]
    medical_roles: Annotated[None, Field(None, description="Medical roles")] = None
    scopes: Annotated[ListOfStrs, Field(..., description="Scopes", min_length=1)]


AnyCredentials = (
    BaseCredentials | AuthenticatedCredentials | TenantCredentials | SystemCredentials
)
AnyCredentialsT = TypeVar("AnyCredentialsT", bound=AnyCredentials)


class CredentialsMixin(BaseModel, Generic[AnyCredentialsT]):
    credentials: AnyCredentialsT = Field(..., description="Credentials")


IsAuthenticatedT = TypeVar("IsAuthenticatedT", bound=bool)


class GenericUser(BaseModel, Generic[IsAuthenticatedT, OptStrT]):
    is_authenticated: IsAuthenticatedT = Field(..., description="Authenticated")
    organization: Annotated[OptStrT, Field(..., description="Organization")]
    display_name: Annotated[str, Field("", description="Username")] = ""
    identity: Annotated[str, Field("", description="Email")] = ""


class BaseUser(GenericUser[bool, OptStr]):
    is_authenticated: Annotated[bool, Field(False, description="Authenticated")] = False
    organization: Annotated[OptStr, Field(None, description="Organization")] = None


class AuthenticatedUser(GenericUser[Literal[True], OptStr]):
    is_authenticated: Literal[True] = True
    organization: Annotated[OptStr, Field(..., description="Organization")]


class TenantUser(GenericUser[Literal[True], str]):
    is_authenticated: Literal[True] = True
    organization: Annotated[str, Field(..., description="Organization")]


class SystemUser(GenericUser[Literal[True], None]):
    is_authenticated: Literal[True] = True
    organization: Annotated[None, Field(None, description="Organization")] = None


AnyUser = BaseUser | AuthenticatedUser | TenantUser | SystemUser
AnyUserT = TypeVar("AnyUserT", bound=AnyUser)


class UserMixin(BaseModel, Generic[AnyUserT]):
    user: AnyUserT = Field(..., description="User")


class GenericAuthentication(
    UserMixin[AnyUserT],
    CredentialsMixin[AnyCredentialsT],
    Generic[AnyCredentialsT, AnyUserT],
    ABC,
):
    @classmethod
    def _validate_request_credentials(cls, conn: HTTPConnection):
        if not isinstance(conn.auth, RequestCredentials):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid type of request's credentials: '{type(conn.auth)}'",
            )

    @classmethod
    def _validate_request_user(cls, conn: HTTPConnection):
        if not isinstance(conn.user, RequestUser):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid type of request's user: '{type(conn.user)}'",
            )

    @classmethod
    @abstractmethod
    def _extract(
        cls,
        conn: HTTPConnection,
        /,
    ) -> Self:
        """Main extractor logic"""

    @classmethod
    def extract(
        cls,
        conn: HTTPConnection,
        /,
    ) -> Self:
        try:
            return cls._extract(conn)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=extract_details(e)
            )

    @classmethod
    def as_dependency(cls) -> Callable[[HTTPConnection], Self]:
        """Create a FastAPI dependency for this authentication"""

        def dependency(conn: HTTPConnection) -> Self:
            return cls.extract(conn)

        return dependency

    @cached_property
    def is_valid_domain(self) -> bool:
        return self.credentials.domain is not None and isinstance(
            self.credentials.domain, Domain
        )

    @cached_property
    def is_system_domain(self) -> bool:
        return self.is_valid_domain and self.credentials.domain is Domain.SYSTEM

    @cached_property
    def is_tenant_domain(self) -> bool:
        return self.is_valid_domain and self.credentials.domain is Domain.TENANT

    @cached_property
    def is_valid_domain_roles(self) -> bool:
        return self.credentials.domain_roles is not None and (
            all(
                isinstance(role, OrganizationRole)
                for role in self.credentials.domain_roles
            )
            or all(
                isinstance(role, SystemRole) for role in self.credentials.domain_roles
            )
        )

    def has_all_domain_roles(self, roles: ListOfDomainRoles) -> bool:
        return (
            self.is_valid_domain_roles
            and self.credentials.domain_roles is not None
            and all(role in self.credentials.domain_roles for role in roles)
        )

    def has_any_domain_roles(self, roles: ListOfDomainRoles) -> bool:
        return (
            self.is_valid_domain_roles
            and self.credentials.domain_roles is not None
            and any(role in self.credentials.domain_roles for role in roles)
        )

    def has_domain_roles(
        self, roles: ListOfDomainRoles, *, logic: Literal["all", "any"]
    ) -> bool:
        if logic == "all":
            return self.has_all_domain_roles(roles)
        elif logic == "any":
            return self.has_any_domain_roles(roles)

    @cached_property
    def is_valid_system_roles(self) -> bool:
        return (
            self.is_valid_domain_roles
            and self.credentials.domain_roles is not None
            and all(
                isinstance(role, SystemRole) for role in self.credentials.domain_roles
            )
        )

    def has_all_system_roles(self, roles: ListOfSystemRoles) -> bool:
        return (
            self.is_valid_system_roles
            and self.credentials.domain_roles is not None
            and all(role in self.credentials.domain_roles for role in roles)
        )

    def has_any_system_roles(self, roles: ListOfSystemRoles) -> bool:
        return (
            self.is_valid_system_roles
            and self.credentials.domain_roles is not None
            and any(role in self.credentials.domain_roles for role in roles)
        )

    def has_system_roles(
        self, roles: ListOfSystemRoles, *, logic: Literal["all", "any"]
    ) -> bool:
        if logic == "all":
            return self.has_all_system_roles(roles)
        elif logic == "any":
            return self.has_any_system_roles(roles)

    @cached_property
    def is_valid_tenant_roles(self) -> bool:
        return (
            self.is_valid_domain_roles
            and self.credentials.domain_roles is not None
            and all(
                isinstance(role, OrganizationRole)
                for role in self.credentials.domain_roles
            )
        )

    def has_all_tenant_roles(self, roles: ListOfOrganizationRoles) -> bool:
        return (
            self.is_valid_tenant_roles
            and self.credentials.domain_roles is not None
            and all(role in self.credentials.domain_roles for role in roles)
        )

    def has_any_tenant_roles(self, roles: ListOfOrganizationRoles) -> bool:
        return (
            self.is_valid_tenant_roles
            and self.credentials.domain_roles is not None
            and any(role in self.credentials.domain_roles for role in roles)
        )

    def has_tenant_roles(
        self, roles: ListOfOrganizationRoles, *, logic: Literal["all", "any"]
    ) -> bool:
        if logic == "all":
            return self.has_all_tenant_roles(roles)
        elif logic == "any":
            return self.has_any_tenant_roles(roles)

    @cached_property
    def is_valid_medical_roles(self) -> bool:
        return self.credentials.medical_roles is not None and all(
            isinstance(role, MedicalRole) for role in self.credentials.medical_roles
        )

    def has_all_medical_roles(self, roles: ListOfMedicalRoles) -> bool:
        return (
            self.is_valid_medical_roles
            and self.credentials.medical_roles is not None
            and all(role in self.credentials.medical_roles for role in roles)
        )

    def has_any_medical_roles(self, roles: ListOfMedicalRoles) -> bool:
        return (
            self.is_valid_medical_roles
            and self.credentials.medical_roles is not None
            and any(role in self.credentials.medical_roles for role in roles)
        )

    def has_medical_roles(
        self, roles: ListOfMedicalRoles, *, logic: Literal["all", "any"]
    ) -> bool:
        if logic == "all":
            return self.has_all_medical_roles(roles)
        elif logic == "any":
            return self.has_any_medical_roles(roles)

    @cached_property
    def is_authenticated(self) -> bool:
        return (
            self.user.is_authenticated
            and self.is_valid_domain
            and self.credentials.user is not None
            and self.is_valid_domain_roles
            and self.credentials.scopes is not None
        )

    @cached_property
    def is_system(self) -> bool:
        return (
            self.is_authenticated
            and self.user.organization is None
            and self.is_system_domain
            and self.credentials.organization is None
            and self.credentials.domain_roles is not None
            and self.is_valid_system_roles
            and self.credentials.medical_roles is None
        )

    @cached_property
    def is_system_administrator(self) -> bool:
        return self.is_system and self.has_all_system_roles([SystemRole.ADMINISTRATOR])

    @cached_property
    def is_tenant(self) -> bool:
        return (
            self.is_authenticated
            and self.user.organization is not None
            and self.is_tenant_domain
            and self.credentials.organization is not None
            and self.credentials.domain_roles is not None
            and self.is_valid_tenant_roles
        )

    @cached_property
    def is_tenant_owner(self) -> bool:
        return self.is_tenant and self.has_all_tenant_roles([OrganizationRole.OWNER])

    @cached_property
    def is_tenant_administrator(self) -> bool:
        return self.is_tenant and self.has_all_tenant_roles(
            [OrganizationRole.ADMINISTRATOR]
        )

    @cached_property
    def is_tenant_owner_or_administrator(self) -> bool:
        return self.is_tenant and self.has_any_tenant_roles(
            [OrganizationRole.OWNER, OrganizationRole.ADMINISTRATOR]
        )


class BaseAuthentication(GenericAuthentication[BaseCredentials, BaseUser]):
    credentials: Annotated[
        BaseCredentials,
        Field(BaseCredentials(), description="Credentials"),
    ] = BaseCredentials()

    user: Annotated[BaseUser, Field(BaseUser(), description="User")] = BaseUser()

    @classmethod
    def _extract(
        cls,
        conn: HTTPConnection,
        /,
    ) -> Self:
        # validate credentials
        cls._validate_request_credentials(conn=conn)
        credentials = BaseCredentials.model_validate(conn.auth, from_attributes=True)

        # validate user
        cls._validate_request_user(conn=conn)
        user = BaseUser.model_validate(conn.user, from_attributes=True)
        return cls(credentials=credentials, user=user)


class AuthenticatedAuthentication(
    GenericAuthentication[AuthenticatedCredentials, AuthenticatedUser]
):
    credentials: Annotated[
        AuthenticatedCredentials, Field(..., description="Credentials")
    ]

    user: Annotated[AuthenticatedUser, Field(..., description="User")]

    @classmethod
    def _extract(
        cls,
        conn: HTTPConnection,
        /,
    ) -> Self:
        # validate credentials
        cls._validate_request_credentials(conn=conn)
        credentials = AuthenticatedCredentials.model_validate(
            conn.auth, from_attributes=True
        )

        # validate user
        cls._validate_request_user(conn=conn)
        user = AuthenticatedUser.model_validate(conn.user, from_attributes=True)
        return cls(credentials=credentials, user=user)


class TenantAuthentication(GenericAuthentication[TenantCredentials, TenantUser]):
    credentials: Annotated[TenantCredentials, Field(..., description="Credentials")]
    user: Annotated[TenantUser, Field(..., description="User")]

    @classmethod
    def _extract(
        cls,
        conn: HTTPConnection,
        /,
    ) -> Self:
        # validate credentials
        cls._validate_request_credentials(conn=conn)
        credentials = TenantCredentials.model_validate(conn.auth, from_attributes=True)

        # validate user
        cls._validate_request_user(conn=conn)
        user = TenantUser.model_validate(conn.user, from_attributes=True)
        return cls(credentials=credentials, user=user)


class SystemAuthentication(GenericAuthentication[SystemCredentials, SystemUser]):
    credentials: Annotated[SystemCredentials, Field(..., description="Credentials")]
    user: Annotated[SystemUser, Field(..., description="User")]

    @classmethod
    def _extract(
        cls,
        conn: HTTPConnection,
        /,
    ) -> Self:
        # validate credentials
        cls._validate_request_credentials(conn=conn)
        credentials = SystemCredentials.model_validate(conn.auth, from_attributes=True)

        # validate user
        cls._validate_request_user(conn=conn)
        user = SystemUser.model_validate(conn.user, from_attributes=True)
        return cls(credentials=credentials, user=user)


AnyAuthenticatedAuthentication = (
    AuthenticatedAuthentication | TenantAuthentication | SystemAuthentication
)
AnyAuthenticatedAuthenticationT = TypeVar(
    "AnyAuthenticatedAuthenticationT", bound=AnyAuthenticatedAuthentication
)
OptAnyAuthenticatedAuthentication = AnyAuthenticatedAuthentication | None
OptAnyAuthenticatedAuthenticationT = TypeVar(
    "OptAnyAuthenticatedAuthenticationT",
    bound=OptAnyAuthenticatedAuthentication,
)


AnyAuthentication = BaseAuthentication | AnyAuthenticatedAuthentication
AnyAuthenticationT = TypeVar("AnyAuthenticationT", bound=AnyAuthentication)
OptAnyAuthentication = AnyAuthentication | None
OptAnyAuthenticationT = TypeVar("OptAnyAuthenticationT", bound=OptAnyAuthentication)


def is_authenticated(
    authentication: AnyAuthentication,
) -> TypeGuard[AnyAuthenticatedAuthentication]:
    return authentication.is_authenticated


def is_system(
    authentication: AnyAuthentication,
) -> TypeGuard[SystemAuthentication]:
    return authentication.is_system


def is_tenant(
    authentication: AnyAuthentication,
) -> TypeGuard[TenantAuthentication]:
    return authentication.is_tenant


class AuthenticationMixin(BaseModel, Generic[OptAnyAuthenticationT]):
    authentication: OptAnyAuthenticationT = Field(..., description="Authentication")


class AuthenticationFactory:
    @overload
    @classmethod
    def extract(
        cls,
        domain: Literal[Domain.TENANT],
        *,
        conn: HTTPConnection,
        mandatory: Literal[True] = True,
    ) -> TenantAuthentication: ...
    @overload
    @classmethod
    def extract(
        cls,
        domain: Literal[Domain.SYSTEM],
        *,
        conn: HTTPConnection,
        mandatory: Literal[True] = True,
    ) -> SystemAuthentication: ...
    @overload
    @classmethod
    def extract(
        cls,
        domain: None = None,
        *,
        conn: HTTPConnection,
        mandatory: Literal[True] = True,
    ) -> AuthenticatedAuthentication: ...
    @overload
    @classmethod
    def extract(
        cls, domain: None = None, *, conn: HTTPConnection, mandatory: Literal[False]
    ) -> BaseAuthentication: ...
    @overload
    @classmethod
    def extract(
        cls,
        domain: OptDomain = None,
        *,
        conn: HTTPConnection,
        mandatory: bool = False,
    ) -> AnyAuthentication: ...
    @classmethod
    def extract(
        cls,
        domain: OptDomain = None,
        *,
        conn: HTTPConnection,
        mandatory: bool = True,
    ) -> AnyAuthentication:
        if not mandatory:
            return BaseAuthentication.extract(conn)
        if domain is None:
            return AuthenticatedAuthentication.extract(conn)
        elif domain is Domain.TENANT:
            return TenantAuthentication.extract(conn)
        elif domain is Domain.SYSTEM:
            return SystemAuthentication.extract(conn)

    @overload
    @classmethod
    def as_dependency(
        cls, domain: Literal[Domain.TENANT], *, mandatory: Literal[True] = True
    ) -> Callable[[HTTPConnection], TenantAuthentication]: ...
    @overload
    @classmethod
    def as_dependency(
        cls, domain: Literal[Domain.SYSTEM], *, mandatory: Literal[True] = True
    ) -> Callable[[HTTPConnection], SystemAuthentication]: ...
    @overload
    @classmethod
    def as_dependency(
        cls, domain: None = None, *, mandatory: Literal[True] = True
    ) -> Callable[[HTTPConnection], AuthenticatedAuthentication]: ...
    @overload
    @classmethod
    def as_dependency(
        cls, domain: None = None, *, mandatory: Literal[False]
    ) -> Callable[[HTTPConnection], BaseAuthentication]: ...
    @classmethod
    def as_dependency(
        cls, domain: OptDomain = None, *, mandatory: bool = True
    ) -> Callable[[HTTPConnection], AnyAuthentication]:

        def dependency(conn: HTTPConnection) -> AnyAuthentication:
            return cls.extract(domain, conn=conn, mandatory=mandatory)

        return dependency

    @overload
    @classmethod
    def convert(
        cls,
        destination: Literal[ConversionDestination.BASE],
        *,
        authentication: AnyAuthentication,
    ) -> BaseAuthentication: ...
    @overload
    @classmethod
    def convert(
        cls,
        destination: Literal[ConversionDestination.AUTHENTICATED],
        *,
        authentication: AnyAuthentication,
    ) -> AuthenticatedAuthentication: ...
    @overload
    @classmethod
    def convert(
        cls,
        destination: Literal[ConversionDestination.TENANT],
        *,
        authentication: AnyAuthentication,
    ) -> TenantAuthentication: ...
    @overload
    @classmethod
    def convert(
        cls,
        destination: Literal[ConversionDestination.SYSTEM],
        *,
        authentication: AnyAuthentication,
    ) -> BaseAuthentication: ...
    @classmethod
    def convert(
        cls, destination: ConversionDestination, *, authentication: AnyAuthentication
    ) -> AnyAuthentication:
        if destination is ConversionDestination.BASE:
            return BaseAuthentication.model_validate(authentication.model_dump())
        elif destination is ConversionDestination.AUTHENTICATED:
            return AuthenticatedAuthentication.model_validate(
                authentication.model_dump()
            )
        elif destination is ConversionDestination.TENANT:
            if isinstance(authentication, SystemAuthentication):
                raise TypeError(
                    "Failed converting SystemAuthentication to TenantAuthentication",
                    "Both authentications can not be converted into one another",
                )
            return TenantAuthentication.model_validate(authentication.model_dump())
        elif destination is ConversionDestination.SYSTEM:
            if isinstance(authentication, TenantAuthentication):
                raise TypeError(
                    "Failed converting TenantAuthentication to SystemAuthentication",
                    "Both authentications can not be converted into one another",
                )
            return SystemAuthentication.model_validate(authentication.model_dump())
