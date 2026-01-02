from pydantic import BaseModel, Field
from typing import Annotated, Generic
from nexo.types.service import (
    OptServiceKeyT,
    OptServiceKeysT,
    OptServiceNameT,
    OptServiceNamesT,
)


class SimpleServiceKeyMixin(BaseModel, Generic[OptServiceKeyT]):
    key: Annotated[OptServiceKeyT, Field(..., description="Service Key")]


class FullServiceKeyMixin(BaseModel, Generic[OptServiceKeyT]):
    service_key: Annotated[OptServiceKeyT, Field(..., description="Service Key")]


class SimpleServiceKeysMixin(BaseModel, Generic[OptServiceKeysT]):
    keys: Annotated[OptServiceKeysT, Field(..., description="Service Keys")]


class FullServiceKeysMixin(BaseModel, Generic[OptServiceKeysT]):
    service_keys: Annotated[OptServiceKeysT, Field(..., description="Service Keys")]


class SimpleServiceNameMixin(BaseModel, Generic[OptServiceNameT]):
    name: Annotated[OptServiceNameT, Field(..., description="Service Name")]


class FullServiceNameMixin(BaseModel, Generic[OptServiceNameT]):
    service_name: Annotated[OptServiceNameT, Field(..., description="Service Name")]


class SimpleServiceNamesMixin(BaseModel, Generic[OptServiceNamesT]):
    names: Annotated[OptServiceNamesT, Field(..., description="Service Names")]


class FullServiceNamesMixin(BaseModel, Generic[OptServiceNamesT]):
    service_names: Annotated[OptServiceNamesT, Field(..., description="Service Names")]
