from typing import Generic
from .mixins.filter import DateFilters
from .mixins.identity import IdentifierMixin, IdentifierT
from .mixins.parameter import (
    MandatorySimpleDataStatusesMixin,
    Search,
    UseCache,
)
from .mixins.sort import SortColumns
from .operation.action.status import StatusUpdateOperationAction
from .pagination import BaseFlexiblePagination, BaseStrictPagination


class ReadSingleParameter(
    UseCache,
    MandatorySimpleDataStatusesMixin,
    IdentifierMixin[IdentifierT],
    Generic[IdentifierT],
):
    pass


class BaseReadMultipleParameter(
    SortColumns,
    Search,
    MandatorySimpleDataStatusesMixin,
    DateFilters,
):
    pass


class ReadUnpaginatedMultipleParameter(
    UseCache,
    BaseFlexiblePagination,
    BaseReadMultipleParameter,
):
    pass


class ReadPaginatedMultipleParameter(
    UseCache,
    BaseStrictPagination,
    BaseReadMultipleParameter,
):
    pass


class StatusUpdateParameter(
    StatusUpdateOperationAction,
    IdentifierMixin[IdentifierT],
    Generic[IdentifierT],
):
    pass


class DeleteSingleParameter(
    IdentifierMixin[IdentifierT],
    Generic[IdentifierT],
):
    pass
