import typing
from typing import Any, Literal, NamedTuple, cast, get_args, overload

from vitalx.types.query import (
    ActivityColumnExpr,
    ActivityColumnT,
    AggregateExpr,
    AsleepAtValueMacroExpr,
    AwakeAtValueMacroExpr,
    BloodPressureTimeseriesExpr,
    BloodPressureTimeseriesFieldT,
    BloodPressureTimeseriesT,
    BodyColumnExpr,
    BodyColumnT,
    ChronotypeValueMacroExpr,
    ColumnExpr,
    DatePartExpr,
    DatePartT,
    DateTimeUnit,
    DateTruncExpr,
    DiscreteTimeseriesExpr,
    DiscreteTimeseriesFieldT,
    DiscreteTimeseriesT,
    GroupByExpr,
    GroupKeyColumnExpr,
    IndexColumnExpr,
    IntervalTimeseriesExpr,
    IntervalTimeseriesFieldT,
    IntervalTimeseriesT,
    NoteTimeseriesExpr,
    NoteTimeseriesFieldT,
    NoteTimeseriesT,
    Period,
    ProfileColumnExpr,
    ProfileColumnT,
    Query,
    SelectExpr,
    SleepColumnExpr,
    SleepColumnT,
    SleepScoreValueMacroExpr,
    SourceColumnExpr,
    SourceFieldT,
    TemperatureTimeseriesExpr,
    TemperatureTimeseriesFieldT,
    TemperatureTimeseriesT,
    TimeseriesExpr,
    TimeseriesT,
    WorkoutColumnExpr,
    WorkoutColumnT,
    WorkoutDurationTimeseriesExpr,
    WorkoutDurationTimeseriesFieldT,
    WorkoutDurationTimeseriesT,
)


def period(value: int, unit: DateTimeUnit) -> Period:
    return Period(value=value, unit=unit)


class SupportsAggregate:
    @property
    def _column_expr(self) -> ColumnExpr:
        return cast(ColumnExpr, self)

    def sum(self) -> AggregateExpr:
        return AggregateExpr(arg=self._column_expr, func="sum")

    def mean(self) -> AggregateExpr:
        return AggregateExpr(arg=self._column_expr, func="mean")

    def min(self) -> AggregateExpr:
        return AggregateExpr(arg=self._column_expr, func="min")

    def max(self) -> AggregateExpr:
        return AggregateExpr(arg=self._column_expr, func="max")

    def median(self) -> AggregateExpr:
        return AggregateExpr(arg=self._column_expr, func="median")

    def stddev(self) -> AggregateExpr:
        return AggregateExpr(arg=self._column_expr, func="stddev")

    def newest(self) -> AggregateExpr:
        return AggregateExpr(arg=self._column_expr, func="newest")

    def oldest(self) -> AggregateExpr:
        return AggregateExpr(arg=self._column_expr, func="oldest")

    def count(self) -> AggregateExpr:
        return AggregateExpr(arg=self._column_expr, func="count")


class IndexColumnExprLike(IndexColumnExpr, SupportsAggregate):
    pass


class SleepColumnExprLike(SleepColumnExpr, SupportsAggregate):
    pass


class ActivityColumnExprLike(ActivityColumnExpr, SupportsAggregate):
    pass


class WorkoutColumnExprLike(WorkoutColumnExpr, SupportsAggregate):
    pass


class BodyColumnExprLike(BodyColumnExpr, SupportsAggregate):
    pass


class ProfileColumnExprLike(ProfileColumnExpr, SupportsAggregate):
    pass


class SleepScoreValueMacroExprLike(SleepScoreValueMacroExpr, SupportsAggregate):
    pass


class ChronotypeValueMacroExprLike(ChronotypeValueMacroExpr, SupportsAggregate):
    pass


class AsleepAtValueMacroExprLike(AsleepAtValueMacroExpr, SupportsAggregate):
    pass


class AwakeAtValueMacroExprLike(AwakeAtValueMacroExpr, SupportsAggregate):
    pass


class DiscreteTimeseriesColumnExprLike(DiscreteTimeseriesExpr, SupportsAggregate):
    pass


class IntervalTimeseriesExprLike(IntervalTimeseriesExpr, SupportsAggregate):
    pass


class BloodPressureTimeseriesExprLike(BloodPressureTimeseriesExpr, SupportsAggregate):
    pass


class TemperatureTimeseriesExprLike(TemperatureTimeseriesExpr, SupportsAggregate):
    pass


class WorkoutDurationExprLike(WorkoutDurationTimeseriesExpr, SupportsAggregate):
    pass


class NoteTimeseriesExprLike(NoteTimeseriesExpr, SupportsAggregate):
    pass


class SourceColumnExprLike(SourceColumnExpr, SupportsAggregate):
    pass


TimeseriesExprVar = typing.TypeVar(
    "TimeseriesExprVar",
    bound=TimeseriesExpr,
)


class DiscreteTimeseriesPartial:
    def __init__(self, resource: DiscreteTimeseriesT) -> None:
        self.resource: DiscreteTimeseriesT = resource

    def field(self, name: DiscreteTimeseriesFieldT) -> DiscreteTimeseriesColumnExprLike:
        return DiscreteTimeseriesColumnExprLike(
            field=name,
            timeseries=self.resource,
        )


class IntervalTimeseriesPartial:
    def __init__(self, resource: IntervalTimeseriesT) -> None:
        self.resource: IntervalTimeseriesT = resource

    def field(self, name: IntervalTimeseriesFieldT) -> IntervalTimeseriesExprLike:
        return IntervalTimeseriesExprLike(
            field=name,
            timeseries=self.resource,
        )


class BloodPressureTimeseriesPartial:
    def __init__(self, resource: BloodPressureTimeseriesT) -> None:
        self.resource: BloodPressureTimeseriesT = resource

    def field(
        self, name: BloodPressureTimeseriesFieldT
    ) -> BloodPressureTimeseriesExprLike:
        return BloodPressureTimeseriesExprLike(
            field=name,
            timeseries=self.resource,
        )


class TemperatureTimeseriesPartial:
    def __init__(self, resource: TemperatureTimeseriesT) -> None:
        self.resource: TemperatureTimeseriesT = resource

    def field(self, name: TemperatureTimeseriesFieldT) -> TemperatureTimeseriesExprLike:
        return TemperatureTimeseriesExprLike(
            field=name,
            timeseries=self.resource,
        )


class WorkoutDurationTimeseriesPartial:
    def __init__(self, resource: WorkoutDurationTimeseriesT) -> None:
        self.resource: WorkoutDurationTimeseriesT = resource

    def field(self, name: WorkoutDurationTimeseriesFieldT) -> WorkoutDurationExprLike:
        return WorkoutDurationExprLike(
            field=name,
            timeseries=self.resource,
        )


class NoteTimeseriesPartial:
    def __init__(self, resource: NoteTimeseriesT) -> None:
        self.resource: NoteTimeseriesT = resource

    def field(self, name: NoteTimeseriesFieldT) -> NoteTimeseriesExprLike:
        return NoteTimeseriesExprLike(
            field=name,
            timeseries=self.resource,
        )


class Timeseries:
    @typing.overload
    @staticmethod
    def col(resource: DiscreteTimeseriesT, /) -> DiscreteTimeseriesPartial:
        ...

    @typing.overload
    @staticmethod
    def col(resource: BloodPressureTimeseriesT, /) -> BloodPressureTimeseriesPartial:
        ...

    @typing.overload
    @staticmethod
    def col(resource: TemperatureTimeseriesT, /) -> TemperatureTimeseriesPartial:
        ...

    @typing.overload
    @staticmethod
    def col(
        resource: WorkoutDurationTimeseriesT, /
    ) -> WorkoutDurationTimeseriesPartial:
        ...

    @typing.overload
    @staticmethod
    def col(resource: NoteTimeseriesT, /) -> NoteTimeseriesPartial:
        ...

    @typing.overload
    @staticmethod
    def col(resource: IntervalTimeseriesT, /) -> IntervalTimeseriesPartial:
        ...

    @staticmethod
    def col(resource: TimeseriesT, /) -> Any:
        if resource in get_args(DiscreteTimeseriesT):
            return DiscreteTimeseriesPartial(
                resource=cast(DiscreteTimeseriesT, resource)
            )

        if resource in get_args(IntervalTimeseriesT):
            return IntervalTimeseriesPartial(
                resource=cast(IntervalTimeseriesT, resource)
            )

        if resource in get_args(BloodPressureTimeseriesT):
            return BloodPressureTimeseriesPartial(
                resource=cast(BloodPressureTimeseriesT, resource)
            )

        if resource in get_args(TemperatureTimeseriesT):
            return TemperatureTimeseriesPartial(
                resource=cast(TemperatureTimeseriesT, resource)
            )

        if resource in get_args(WorkoutDurationTimeseriesT):
            return WorkoutDurationTimeseriesPartial(
                resource=cast(WorkoutDurationTimeseriesT, resource)
            )

        if resource in get_args(NoteTimeseriesT):
            return NoteTimeseriesPartial(resource=cast(NoteTimeseriesT, resource))

        raise ValueError(f"Unsupported timeseries type: {resource}.")

    @staticmethod
    def index() -> IndexColumnExprLike:
        """
        The Timeseries datetime index (YYYY-mm-dd HH:mm:ss).
        """
        return IndexColumnExprLike(index="timeseries")


class Source:
    @staticmethod
    def col(name: SourceFieldT) -> SourceColumnExprLike:
        return SourceColumnExprLike(source=name)


class Sleep:
    @staticmethod
    def col(name: SleepColumnT) -> SleepColumnExprLike:
        return SleepColumnExprLike(sleep=name)

    @staticmethod
    def index() -> IndexColumnExprLike:
        """
        The Sleep Session End datetime index (YYYY-mm-dd HH:mm:ss).
        """
        return IndexColumnExprLike(index="sleep")

    @staticmethod
    def score(
        *, version: Literal["automatic"] = "automatic"
    ) -> SleepScoreValueMacroExprLike:
        """
        Computed sleep score using the Vital Horizon AI Sleep Score model.
        """
        return SleepScoreValueMacroExprLike(value_macro="sleep_score", version=version)

    @staticmethod
    def chronotype(
        *, version: Literal["automatic"] = "automatic"
    ) -> ChronotypeValueMacroExprLike:
        """
        Computed chronotype based on the midpoint of the sleep session.
        """
        return ChronotypeValueMacroExprLike(value_macro="chronotype", version=version)

    @staticmethod
    def asleep_at(
        *, version: Literal["automatic"] = "automatic"
    ) -> AsleepAtValueMacroExprLike:
        """
        Computed time of user falling asleep based on sleep session start time and latency
        """
        return AsleepAtValueMacroExprLike(value_macro="asleep_at", version=version)

    @staticmethod
    def awake_at(
        *, version: Literal["automatic"] = "automatic"
    ) -> AwakeAtValueMacroExprLike:
        """
        Computed time of user waking up based on sleep session end time and final sleep segments
        """
        return AwakeAtValueMacroExprLike(value_macro="awake_at", version=version)


class Activity:
    @staticmethod
    def col(name: ActivityColumnT) -> ActivityColumnExprLike:
        return ActivityColumnExprLike(activity=name)

    @staticmethod
    def index() -> IndexColumnExprLike:
        """
        The Activity calendar date index (YYYY-mm-dd).
        """
        return IndexColumnExprLike(index="activity")


class Workout:
    @staticmethod
    def col(name: WorkoutColumnT) -> WorkoutColumnExprLike:
        return WorkoutColumnExprLike(workout=name)

    @staticmethod
    def index() -> IndexColumnExprLike:
        """
        The Sleep Session End datetime index (YYYY-mm-dd HH:mm:ss).
        """
        return IndexColumnExprLike(index="workout")


class Body:
    @staticmethod
    def col(name: BodyColumnT) -> BodyColumnExprLike:
        return BodyColumnExprLike(body=name)

    @staticmethod
    def index() -> IndexColumnExprLike:
        """
        The Body Measurement datetime index (YYYY-mm-dd HH:mm:ss).
        """
        return IndexColumnExprLike(index="body")


class Profile:
    @staticmethod
    def col(name: ProfileColumnT) -> ProfileColumnExprLike:
        return ProfileColumnExprLike(profile=name)

    @staticmethod
    def index() -> IndexColumnExprLike:
        """
        The Profile Last Updated At UTC datetime index (YYYY-mm-dd HH:mm:ss +0000).
        """
        return IndexColumnExprLike(index="profile")


def group_key(offset: int | Literal["*"]) -> GroupKeyColumnExpr:
    """
    The group key columns created by the GroupBy expressions. The offset corresponds
    to the expression declaration order.

    Specify `*` to select all group key columns.
    """
    return GroupKeyColumnExpr(group_key=offset)


@overload
def date_trunc(argument: IndexColumnExpr, period: Period, /) -> DateTruncExpr:
    """
    Truncate the `argument` at the granularity of `period`.

    For example, given these inputs:
    * `argument` is `2024-08-10 12:34:56`
    * `period` is `period(30, "minute")`

    The output is `2024-08-10 12:30:00`.
    """
    ...


@overload
def date_trunc(
    argument: IndexColumnExpr, value: int, unit: DateTimeUnit, /
) -> DateTruncExpr:
    """
    Truncate the `argument` at the granularity of a period length specified by
    `value` and `unit`.

    For example, given these inputs:
    * `argument` is `2024-08-10 12:34:56`
    * Period length is 30 minutes (`value` is 30, and `unit` is `"minute"`)

    The output is `2024-08-10 12:30:00`.
    """
    ...


def date_trunc(argument: IndexColumnExpr, *args: Any) -> DateTruncExpr:
    if len(args) == 1:
        assert isinstance(args[0], Period)
        return DateTruncExpr(arg=argument, date_trunc=args[0])

    if len(args) == 2:
        return DateTruncExpr(
            arg=argument, date_trunc=Period(value=args[0], unit=args[1])
        )

    raise ValueError(f"unsupported input: {args}")


def date_part(argument: IndexColumnExpr, part: DatePartT) -> DatePartExpr:
    """
    Extract a specific date or time component of the datetime `argument`.
    """
    return DatePartExpr(arg=argument, date_part=part)


class QueryPartial(NamedTuple):
    attributes: dict[str, Any]

    def group_by(self, *exprs: GroupByExpr) -> "QueryPartial":
        return QueryPartial({**self.attributes, "group_by": exprs})

    def where(self, raw_sql_expr: str) -> "QueryPartial":
        return QueryPartial({**self.attributes, "where": raw_sql_expr})

    def finalize(self) -> Query:
        return Query.model_validate(self.attributes)


def select(*exprs: SelectExpr) -> QueryPartial:
    return QueryPartial({"select": exprs})
