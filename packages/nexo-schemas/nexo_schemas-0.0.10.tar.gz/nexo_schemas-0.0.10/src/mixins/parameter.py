from pydantic import BaseModel, Field
from typing import Annotated, Generic
from nexo.enums.status import (
    ListOfDataStatuses,
    OptListOfDataStatuses,
    SimpleDataStatusesMixin,
    FULL_DATA_STATUSES,
)
from nexo.types.enum import OptListOfStrEnumsT
from nexo.types.string import OptStr


class OptionalSimpleDataStatusesMixin(SimpleDataStatusesMixin[OptListOfDataStatuses]):
    statuses: Annotated[
        OptListOfDataStatuses,
        Field(None, description="Data statuses", min_length=1),
    ] = None


class MandatorySimpleDataStatusesMixin(SimpleDataStatusesMixin[ListOfDataStatuses]):
    statuses: Annotated[
        ListOfDataStatuses,
        Field(FULL_DATA_STATUSES, description="Data statuses", min_length=1),
    ] = FULL_DATA_STATUSES


class Search(BaseModel):
    search: Annotated[OptStr, Field(None, description="Search string")] = None


class UseCache(BaseModel):
    use_cache: Annotated[bool, Field(True, description="Whether to use cache")] = True


class IncludeURL(BaseModel):
    include_url: Annotated[bool, Field(False, description="Whether to include URL")] = (
        False
    )


class Include(BaseModel, Generic[OptListOfStrEnumsT]):
    include: Annotated[OptListOfStrEnumsT, Field(..., description="Included field(s)")]


class Exclude(BaseModel, Generic[OptListOfStrEnumsT]):
    exclude: Annotated[OptListOfStrEnumsT, Field(..., description="Excluded field(s)")]


class Expand(BaseModel, Generic[OptListOfStrEnumsT]):
    expand: Annotated[OptListOfStrEnumsT, Field(..., description="Expanded field(s)")]
