from datetime import date
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Generic, Self, TypeVar
from uuid import UUID as PythonUUID
from nexo.types.datetime import OptDate, OptDateT, OptListOfDatesT
from nexo.types.enum import StrEnumT, OptStrEnumT
from nexo.types.integer import OptIntT, OptListOfIntsT
from nexo.types.misc import (
    OptIntOrUUIDT,
    OptListOfIntsOrUUIDsT,
)
from nexo.types.string import OptStrT, OptListOfStrsT
from nexo.types.uuid import OptUUIDT, OptListOfUUIDsT


class IdentifierType(BaseModel, Generic[StrEnumT]):
    type: StrEnumT = Field(..., description="Identifier's type")


IdentifierValueT = TypeVar("IdentifierValueT")


class IdentifierValue(BaseModel, Generic[IdentifierValueT]):
    value: IdentifierValueT = Field(..., description="Identifier's value")


class Identifier(
    IdentifierValue[IdentifierValueT],
    IdentifierType[StrEnumT],
    Generic[StrEnumT, IdentifierValueT],
):
    pass


IdentifierT = TypeVar("IdentifierT", bound=Identifier)


class IdentifierMixin(BaseModel, Generic[IdentifierT]):
    identifier: Annotated[IdentifierT, Field(..., description="Identifier")]


# Id
class Id(BaseModel, Generic[OptIntOrUUIDT]):
    id: OptIntOrUUIDT = Field(..., description="Id")


class IntId(BaseModel, Generic[OptIntT]):
    id: OptIntT = Field(..., description="Id (Integer)", ge=1)


class UUIDId(BaseModel, Generic[OptUUIDT]):
    id: OptUUIDT = Field(..., description="Id (UUID)")


# Ids
class Ids(BaseModel, Generic[OptListOfIntsOrUUIDsT]):
    ids: OptListOfIntsOrUUIDsT = Field(..., description="Ids")


class IntIds(BaseModel, Generic[OptListOfIntsT]):
    ids: OptListOfIntsT = Field(..., description="Ids (Integers)")


class UUIDIds(BaseModel, Generic[OptListOfUUIDsT]):
    ids: OptListOfUUIDsT = Field(..., description="Ids (UUIDs)")


# UUID
class UUID(BaseModel, Generic[OptUUIDT]):
    uuid: OptUUIDT = Field(..., description="UUID")


class UUIDs(BaseModel, Generic[OptListOfUUIDsT]):
    uuids: OptListOfUUIDsT = Field(..., description="UUIDs")


# Identifier
class DataIdentifier(
    UUID[PythonUUID],
    IntId[int],
):
    pass


class EntityType(BaseModel, Generic[OptStrEnumT]):
    type: Annotated[OptStrEnumT, Field(..., description="Entity's type")]


class EntityIdentifier(
    EntityType[OptStrEnumT], UUID[PythonUUID], IntId[int], Generic[OptStrEnumT]
):
    pass


EntityIdentifierT = TypeVar("EntityIdentifierT", bound=EntityIdentifier)


class IdCard(BaseModel, Generic[OptStrT]):
    id_card: OptStrT = Field(..., description="ID Card")


class IdCards(BaseModel, Generic[OptListOfStrsT]):
    id_cards: OptListOfStrsT = Field(..., description="ID Cards")


class Passport(BaseModel, Generic[OptStrT]):
    passport: OptStrT = Field(..., description="Passport")


class Passports(BaseModel, Generic[OptListOfStrsT]):
    passports: OptListOfStrsT = Field(..., description="Passports")


class Key(BaseModel, Generic[OptStrT]):
    key: OptStrT = Field(..., description="Key")


class Keys(BaseModel, Generic[OptListOfStrsT]):
    keys: OptListOfStrsT = Field(..., description="Keys")


class FullName(BaseModel, Generic[OptStrT]):
    full_name: OptStrT = Field(..., description="Full Name")


class FullNames(BaseModel, Generic[OptListOfStrsT]):
    full_names: OptListOfStrsT = Field(..., description="Full Names")


class Name(BaseModel, Generic[OptStrT]):
    name: OptStrT = Field(..., description="Name")


class Names(BaseModel, Generic[OptListOfStrsT]):
    names: OptListOfStrsT = Field(..., description="Names")


class Age(BaseModel):
    raw: Annotated[float, Field(0, description="Age", ge=0.0)] = 0
    year: Annotated[int, Field(0, description="Year", ge=0)] = 0
    month: Annotated[int, Field(0, description="Month", ge=0)] = 0
    day: Annotated[int, Field(0, description="Day", ge=0)] = 0

    @classmethod
    def from_date_of_birth(cls, date_of_birth: OptDate) -> Self:
        if date_of_birth is None:
            return cls()

        today = date.today()

        # Compute Y/M/D difference
        y = today.year - date_of_birth.year
        m = today.month - date_of_birth.month
        d = today.day - date_of_birth.day

        # Normalize negative days/months
        if d < 0:
            m -= 1
            # Approx: last month's number of days
            # If precision needed you can use calendar.monthrange
            prev_month = (today.month - 1) or 12
            prev_year = today.year if today.month > 1 else today.year - 1
            from calendar import monthrange

            d += monthrange(prev_year, prev_month)[1]

        if m < 0:
            y -= 1
            m += 12

        raw = y + m / 12 + d / 365.25

        return cls(raw=raw, year=y, month=m, day=d)


OptAge = Age | None
OptAgeT = TypeVar("OptAgeT", bound=OptAge)


class AgeMixin(BaseModel):
    age: Annotated[Age, Field(default_factory=Age, description="Age")]


class BirthDate(BaseModel, Generic[OptDateT]):
    birth_date: OptDateT = Field(..., description="Birth Date")

    @computed_field
    @property
    def age(self) -> Age:
        return Age.from_date_of_birth(self.birth_date)


class BirthDates(BaseModel, Generic[OptListOfDatesT]):
    birth_dates: OptListOfDatesT = Field(..., description="Birth Dates")


class DateOfBirth(BaseModel, Generic[OptDateT]):
    date_of_birth: OptDateT = Field(..., description="Date of Birth")

    @computed_field
    @property
    def age(self) -> Age:
        return Age.from_date_of_birth(self.date_of_birth)


class DateOfBirths(BaseModel, Generic[OptListOfDatesT]):
    date_of_births: OptListOfDatesT = Field(..., description="Date of Births")


class BirthPlace(BaseModel, Generic[OptStrT]):
    birth_place: OptStrT = Field(..., description="Birth Place")


class BirthPlaces(BaseModel, Generic[OptListOfStrsT]):
    birth_places: OptListOfStrsT = Field(..., description="Birth Places")


class PlaceOfBirth(BaseModel, Generic[OptStrT]):
    place_of_birth: OptStrT = Field(..., description="Place of Birth")


class PlaceOfBirths(BaseModel, Generic[OptListOfStrsT]):
    place_of_births: OptListOfStrsT = Field(..., description="Place of Births")


# ----- ----- ----- Organization ID ----- ----- ----- #


class OrganizationId(BaseModel, Generic[OptIntOrUUIDT]):
    organization_id: OptIntOrUUIDT = Field(..., description="Organization's ID")


class IntOrganizationId(BaseModel, Generic[OptIntT]):
    organization_id: OptIntT = Field(..., description="Organization's ID", ge=1)


class UUIDOrganizationId(BaseModel, Generic[OptUUIDT]):
    organization_id: OptUUIDT = Field(..., description="Organization's ID")


class OrganizationIds(BaseModel, Generic[OptListOfIntsOrUUIDsT]):
    organization_ids: OptListOfIntsOrUUIDsT = Field(
        ..., description="Organization's IDs"
    )


class IntOrganizationIds(BaseModel, Generic[OptListOfIntsT]):
    organization_ids: OptListOfIntsT = Field(..., description="Organization's IDs")


class UUIDOrganizationIds(BaseModel, Generic[OptListOfUUIDsT]):
    organization_ids: OptListOfUUIDsT = Field(..., description="Organization's IDs")


# ----- ----- ----- Parent ID ----- ----- ----- #


class ParentId(BaseModel, Generic[OptIntOrUUIDT]):
    parent_id: OptIntOrUUIDT = Field(..., description="Parent's ID")


class IntParentId(BaseModel, Generic[OptIntT]):
    parent_id: OptIntT = Field(..., description="Parent's ID", ge=1)


class UUIDParentId(BaseModel, Generic[OptUUIDT]):
    parent_id: OptUUIDT = Field(..., description="Parent's ID")


class ParentIds(BaseModel, Generic[OptListOfIntsOrUUIDsT]):
    parent_ids: OptListOfIntsOrUUIDsT = Field(..., description="Parent's IDs")


class IntParentIds(BaseModel, Generic[OptListOfIntsT]):
    parent_ids: OptListOfIntsT = Field(..., description="Parent's IDs")


class UUIDParentIds(BaseModel, Generic[OptListOfUUIDsT]):
    parent_ids: OptListOfUUIDsT = Field(..., description="Parent's IDs")


# ----- ----- ----- Patient ID ----- ----- ----- #


class PatientId(BaseModel, Generic[OptIntOrUUIDT]):
    patient_id: OptIntOrUUIDT = Field(..., description="Patient's ID")


class IntPatientId(BaseModel, Generic[OptIntT]):
    patient_id: OptIntT = Field(..., description="Patient's ID", ge=1)


class UUIDPatientId(BaseModel, Generic[OptUUIDT]):
    patient_id: OptUUIDT = Field(..., description="Patient's ID")


class PatientIds(BaseModel, Generic[OptListOfIntsOrUUIDsT]):
    patient_ids: OptListOfIntsOrUUIDsT = Field(..., description="Patient's IDs")


class IntPatientIds(BaseModel, Generic[OptListOfIntsT]):
    patient_ids: OptListOfIntsT = Field(..., description="Patient's IDs")


class UUIDPatientIds(BaseModel, Generic[OptListOfUUIDsT]):
    patient_ids: OptListOfUUIDsT = Field(..., description="Patient's IDs")


# ----- ----- ----- Source ID ----- ----- ----- #


class SourceId(BaseModel, Generic[OptIntOrUUIDT]):
    source_id: OptIntOrUUIDT = Field(..., description="Source's ID")


class IntSourceId(BaseModel, Generic[OptIntT]):
    source_id: OptIntT = Field(..., description="Source's ID", ge=1)


class UUIDSourceId(BaseModel, Generic[OptUUIDT]):
    source_id: OptUUIDT = Field(..., description="Source's ID")


class SourceIds(BaseModel, Generic[OptListOfIntsOrUUIDsT]):
    source_ids: OptListOfIntsOrUUIDsT = Field(..., description="Source's IDs")


class IntSourceIds(BaseModel, Generic[OptListOfIntsT]):
    source_ids: OptListOfIntsT = Field(..., description="Source's IDs")


class UUIDSourceIds(BaseModel, Generic[OptListOfUUIDsT]):
    source_ids: OptListOfUUIDsT = Field(..., description="Source's IDs")


# ----- ----- ----- Target ID ----- ----- ----- #


class TargetId(BaseModel, Generic[OptIntOrUUIDT]):
    target_id: OptIntOrUUIDT = Field(..., description="Target's ID")


class IntTargetId(BaseModel, Generic[OptIntT]):
    target_id: OptIntT = Field(..., description="Target's ID", ge=1)


class UUIDTargetId(BaseModel, Generic[OptUUIDT]):
    target_id: OptUUIDT = Field(..., description="Target's ID")


class TargetIds(BaseModel, Generic[OptListOfIntsOrUUIDsT]):
    target_ids: OptListOfIntsOrUUIDsT = Field(..., description="Target's IDs")


class IntTargetIds(BaseModel, Generic[OptListOfIntsT]):
    target_ids: OptListOfIntsT = Field(..., description="Target's IDs")


class UUIDTargetIds(BaseModel, Generic[OptListOfUUIDsT]):
    target_ids: OptListOfUUIDsT = Field(..., description="Target's IDs")


# ----- ----- ----- User ID ----- ----- ----- #


class UserId(BaseModel, Generic[OptIntOrUUIDT]):
    user_id: OptIntOrUUIDT = Field(..., description="User's ID")


class IntUserId(BaseModel, Generic[OptIntT]):
    user_id: OptIntT = Field(..., description="User's ID", ge=1)


class UUIDUserId(BaseModel, Generic[OptUUIDT]):
    user_id: OptUUIDT = Field(..., description="User's ID")


class UserIds(BaseModel, Generic[OptListOfIntsOrUUIDsT]):
    user_ids: OptListOfIntsOrUUIDsT = Field(..., description="User's IDs")


class IntUserIds(BaseModel, Generic[OptListOfIntsT]):
    user_ids: OptListOfIntsT = Field(..., description="User's IDs")


class UUIDUserIds(BaseModel, Generic[OptListOfUUIDsT]):
    user_ids: OptListOfUUIDsT = Field(..., description="User's IDs")
