from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Annotated, ClassVar, Generic, Self, TypeVar
from nexo.types.datetime import OptDatetime, OptDatetimeT
from nexo.types.float import OptFloatT


class FromTimestamp(BaseModel, Generic[OptDatetimeT]):
    from_date: OptDatetimeT = Field(..., description="From date")


class ToTimestamp(BaseModel, Generic[OptDatetimeT]):
    to_date: OptDatetimeT = Field(..., description="To date")


class StartTimestamp(BaseModel, Generic[OptDatetimeT]):
    started_at: OptDatetimeT = Field(..., description="started_at timestamp")


class FinishTimestamp(BaseModel, Generic[OptDatetimeT]):
    finished_at: OptDatetimeT = Field(..., description="finished_at timestamp")


class ExecutionTimestamp(BaseModel, Generic[OptDatetimeT]):
    executed_at: OptDatetimeT = Field(..., description="executed_at timestamp")


class CompletionTimestamp(BaseModel, Generic[OptDatetimeT]):
    completed_at: OptDatetimeT = Field(..., description="completed_at timestamp")


class CreationTimestamp(BaseModel):
    created_at: datetime = Field(..., description="created_at timestamp")


class UpdateTimestamp(BaseModel):
    updated_at: datetime = Field(..., description="updated_at timestamp")


class LifecycleTimestamp(
    UpdateTimestamp,
    CreationTimestamp,
):
    pass


class DeletionTimestamp(BaseModel, Generic[OptDatetimeT]):
    deleted_at: OptDatetimeT = Field(..., description="deleted_at timestamp")


class RestorationTimestamp(BaseModel, Generic[OptDatetimeT]):
    restored_at: OptDatetimeT = Field(..., description="restored_at timestamp")


class DeactivationTimestamp(BaseModel, Generic[OptDatetimeT]):
    deactivated_at: OptDatetimeT = Field(..., description="deactivated_at timestamp")


class ActivationTimestamp(BaseModel, Generic[OptDatetimeT]):
    activated_at: OptDatetimeT = Field(..., description="activated_at timestamp")


DeletionTimestampT = TypeVar("DeletionTimestampT", bound=OptDatetime)
RestorationTimestampT = TypeVar("RestorationTimestampT", bound=OptDatetime)
DeactivationTimestampT = TypeVar("DeactivationTimestampT", bound=OptDatetime)
ActivationTimestampT = TypeVar("ActivationTimestampT", bound=OptDatetime)


class StatusTimestamp(
    ActivationTimestamp[ActivationTimestampT],
    DeactivationTimestamp[DeactivationTimestampT],
    RestorationTimestamp[RestorationTimestampT],
    DeletionTimestamp[DeletionTimestampT],
    Generic[
        DeletionTimestampT,
        RestorationTimestampT,
        DeactivationTimestampT,
        ActivationTimestampT,
    ],
):
    pass


class DataStatusTimestamp(
    StatusTimestamp[
        OptDatetime,
        OptDatetime,
        OptDatetime,
        datetime,
    ],
):
    pass


class DataTimestamp(
    DataStatusTimestamp,
    LifecycleTimestamp,
):
    pass


class Duration(BaseModel, Generic[OptFloatT]):
    duration: OptFloatT = Field(..., description="Duration")


class InferenceDuration(BaseModel, Generic[OptFloatT]):
    inference_duration: OptFloatT = Field(..., description="Inference duration")


class Uptime(BaseModel):
    _SECONDS_IN_MINUTE: ClassVar[int] = 60
    _SECONDS_IN_HOUR: ClassVar[int] = 3600
    _SECONDS_IN_DAY: ClassVar[int] = 86400
    _SECONDS_IN_MONTH: ClassVar[int] = 30 * _SECONDS_IN_DAY

    raw: Annotated[float, Field(0.0, description="Raw", ge=0.0)] = 0
    month: Annotated[int, Field(0, description="Month", ge=0)] = 0
    day: Annotated[int, Field(0, description="Day", ge=0)] = 0
    hour: Annotated[int, Field(0, description="Hour", ge=0)] = 0
    minute: Annotated[int, Field(0, description="Minute", ge=0)] = 0
    second: Annotated[int, Field(0, description="Second", ge=0)] = 0

    @classmethod
    def from_raw(cls, raw: float = 0) -> Self:
        sec = int(raw)

        month = sec // cls._SECONDS_IN_MONTH
        sec %= cls._SECONDS_IN_MONTH

        day = sec // cls._SECONDS_IN_DAY
        sec %= cls._SECONDS_IN_DAY

        hour = sec // cls._SECONDS_IN_HOUR
        sec %= cls._SECONDS_IN_HOUR

        minute = sec // cls._SECONDS_IN_MINUTE
        sec %= cls._SECONDS_IN_MINUTE

        second = sec

        return cls(
            raw=raw,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
        )

    @classmethod
    def from_timedelta(cls, timedelta: timedelta) -> Self:
        raw = timedelta.total_seconds()
        return cls.from_raw(raw=raw)

    def stringify(self, long: bool = False, skip_zero: bool = True) -> str:
        """
        Convert uptime into a human-readable string.

        Args:
            long: If True → "3 months 2 days".
                  If False → "3M 2D".
            skip_zero: If True → omit fields with zero value.

        Returns:
            A formatted uptime string.
        """

        parts = [
            ("Month", self.month, "Mo"),
            ("Day", self.day, "D"),
            ("Hour", self.hour, "H"),
            ("Minute", self.minute, "Mi"),
            ("Second", self.second, "S"),
        ]

        output = []

        for name, value, short in parts:
            if skip_zero and value == 0:
                continue

            if long:
                label = name if value == 1 else name + "s"
                output.append(f"{value} {label}")
            else:
                output.append(f"{value}{short}")

        return " ".join(output) if output else "0S"


class UptimeMixin(BaseModel):
    uptime: Annotated[Uptime, Field(Uptime(), description="Uptime")] = Uptime()
