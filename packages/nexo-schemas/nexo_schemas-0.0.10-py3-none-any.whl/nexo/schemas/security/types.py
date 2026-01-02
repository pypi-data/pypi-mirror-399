from typing import TypeVar
from nexo.enums.organization import ListOfOrganizationRoles, SeqOfOrganizationRoles
from nexo.enums.system import ListOfSystemRoles, SeqOfSystemRoles


ListOfDomainRoles = ListOfOrganizationRoles | ListOfSystemRoles
ListOfDomainRolesT = TypeVar("ListOfDomainRolesT", bound=ListOfDomainRoles)

OptListOfDomainRoles = ListOfDomainRoles | None
OptListOfDomainRolesT = TypeVar("OptListOfDomainRolesT", bound=OptListOfDomainRoles)


SeqOfDomainRoles = SeqOfOrganizationRoles | SeqOfSystemRoles
SeqOfDomainRolesT = TypeVar("SeqOfDomainRolesT", bound=SeqOfDomainRoles)

OptSeqOfDomainRoles = SeqOfDomainRoles | None
OptSeqOfDomainRolesT = TypeVar("OptSeqOfDomainRolesT", bound=OptSeqOfDomainRoles)
