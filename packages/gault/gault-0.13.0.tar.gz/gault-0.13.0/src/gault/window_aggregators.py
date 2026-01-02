"""aggregators.

TODO: ensure all example here are implemented here https://www.mongodb.com/docs/manual/reference/operator/aggregation/setWindowFields/#mongodb-pipeline-pipe.-setWindowFields
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, TypeAlias

from .compilers import compile_expression, compile_expression_multi
from .interfaces import AsAlias, ExpressionOperator
from .sorting import normalize_sort
from .utils import nullfree_dict

if TYPE_CHECKING:
    from .sorting import SortPayload
    from .types import (
        AnyExpression,
        ArrayExpression,
        Context,
        DateUnit,
        FieldLike,
        Input,
        MongoExpression,
        NumberExpression,
    )

    RangeValue: TypeAlias = Literal["unbounded", "current"] | int


@dataclass
class WindowOperator(ExpressionOperator, AsAlias):
    """Described here https://www.mongodb.com/docs/manual/reference/mql/expressions/."""

    window_documents: tuple[RangeValue, RangeValue] | None = field(
        default=None, kw_only=True
    )
    window_range: tuple[RangeValue, RangeValue] | None = field(
        default=None, kw_only=True
    )
    window_unit: DateUnit | None = field(default=None, kw_only=True)

    @abstractmethod
    def compile_operation(self, *, context: Context) -> MongoExpression: ...

    def compile_expression(self, *, context: Context) -> MongoExpression:
        operation: dict = self.compile_operation(context=context)  # type: ignore[assignment]
        if documents := self.window_documents:
            operation = operation | {"documents": list(documents)}
        if range := self.window_range:
            operation = operation | {"range": list(range)}
        if unit := self.window_unit:
            operation = operation | {"unit": unit}
        return operation


@dataclass
class Bottom(WindowOperator):
    """Returns the bottom element within a group according to the specified sort order."""

    sort_by: SortPayload
    output: AnyExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$bottom": {
                "sortBy": normalize_sort(self.sort_by, context=context),
                "output": compile_expression(self.output, context=context),
            }
        }


@dataclass
class BottomN(WindowOperator):
    """Returns the bottom element within a group according to the specified sort order."""

    n: NumberExpression
    sort_by: SortPayload
    output: AnyExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$bottomN": {
                "n": compile_expression(self.n, context=context),
                "sortBy": normalize_sort(self.sort_by, context=context),
                "output": compile_expression(self.output, context=context),
            }
        }


@dataclass
class ConcatArrays(WindowOperator):
    """Returns the bottom element within a group according to the specified sort order."""

    field: FieldLike

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$concatArrays": compile_expression(self.field, context=context),
        }


@dataclass
class Count(WindowOperator):
    """Returns the number of documents in a group."""

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$count": {},
        }


@dataclass
class FirstN(WindowOperator):
    """Returns an aggregation of the first n elements within a group."""

    n: NumberExpression
    input: ArrayExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$firstN": {
                "n": compile_expression(self.n, context=context),
                "input": compile_expression(self.input, context=context),
            },
        }


@dataclass
class LastN(WindowOperator):
    """Returns an aggregation of the last n elements within a group."""

    n: NumberExpression
    input: ArrayExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$lastN": {
                "n": compile_expression(self.n, context=context),
                "input": compile_expression(self.input, context=context),
            },
        }


@dataclass
class Max(WindowOperator):
    """Returns the maximum value."""

    input: AnyExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$max": compile_expression(self.input, context=context),
        }


@dataclass
class MaxN(WindowOperator):
    """Returns an aggregation of the maximum value n elements within a group."""

    n: NumberExpression
    input: ArrayExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$maxN": {
                "n": compile_expression(self.n, context=context),
                "input": compile_expression(self.input, context=context),
            },
        }


@dataclass
class Min(WindowOperator):
    """Returns the minimum value."""

    input: AnyExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$min": compile_expression(self.input, context=context),
        }


@dataclass
class MinN(WindowOperator):
    """Returns an aggregation of the minimum value n elements within a group."""

    n: NumberExpression
    input: ArrayExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$minN": {
                "n": compile_expression(self.n, context=context),
                "input": compile_expression(self.input, context=context),
            },
        }


@dataclass
class Percentile(WindowOperator):
    """Returns an approximation of a percentile value."""

    input: FieldLike
    p: list[float]
    """The elements represent percentages and must evaluate to numeric values in the range 0.0 to 1.0, inclusive.
    """

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$percentile": {
                "input": compile_expression(self.input, context=context),
                "p": compile_expression_multi(self.p, context=context),
                "method": "approximate",
            },
        }


@dataclass
class Push(WindowOperator):
    """returns an array of all values that result from applying an expression to documents."""

    input: AnyExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$push": compile_expression(self.input, context=context),
        }


@dataclass
class SetUnion(WindowOperator):
    """returns a single array containing the unique elements that appear in any input array."""

    input: AnyExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$setUnion": compile_expression(self.input, context=context),
        }


@dataclass
class StdDevSamp(WindowOperator):
    """Calculates the sample standard deviation of the input values."""

    input: AnyExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$stdDevSamp": compile_expression(self.input, context=context),
        }


@dataclass
class StdDevPop(WindowOperator):
    """Calculates the population standard deviation of the input values."""

    input: AnyExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$stdDevPop": compile_expression(self.input, context=context),
        }


@dataclass
class Sum(WindowOperator):
    """Calculates and returns the collective sum of numeric values."""

    input: NumberExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$sum": compile_expression(self.input, context=context),
        }


@dataclass
class Top(WindowOperator):
    """Returns the top element within a group according to the specified sort order."""

    sort_by: SortPayload
    output: AnyExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$top": {
                "sortBy": normalize_sort(self.sort_by, context=context),
                "output": compile_expression(self.output, context=context),
            }
        }


@dataclass
class TopN(WindowOperator):
    """Returns an aggregation of the top n elements within a group, according to the specified sort order."""

    sort_by: SortPayload
    output: AnyExpression
    n: NumberExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$topN": {
                "sortBy": normalize_sort(self.sort_by, context=context),
                "output": compile_expression(self.output, context=context),
                "n": compile_expression(self.n, context=context),
            }
        }


@dataclass
class AddToSet(WindowOperator):
    """Returns an array of unique expression values for each group."""

    input: AnyExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {"$addToSet": compile_expression(self.input, context=context)}


@dataclass
class Avg(WindowOperator):
    """Returns the average of numeric values."""

    input: NumberExpression

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {"$avg": compile_expression(self.input, context=context)}


@dataclass
class CovariancePop(WindowOperator):
    """Returns the population covariance of two numeric expressions that are evaluated using documents in the `$setWindowFields` stage window."""

    value1: Input
    """any valid expression that resolves to a number, measured in radians"""

    value2: Input
    """any valid expression that resolves to a number, measured in radians"""

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$covariancePop": [
                compile_expression(self.value1, context=context),
                compile_expression(self.value2, context=context),
            ],
        }


@dataclass
class CovarianceSamp(WindowOperator):
    """Returns the sample covariance of two numeric expressions that are evaluated using documents in the `$setWindowFields` stage window."""

    value1: Input
    """any valid expression that resolves to a number, measured in radians"""

    value2: Input
    """any valid expression that resolves to a number, measured in radians"""

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$covarianceSamp": [
                compile_expression(self.value1, context=context),
                compile_expression(self.value2, context=context),
            ],
        }


@dataclass
class DenseRank(WindowOperator):
    """Returns the document position (known as the rank) relative to other documents in the $setWindowFields stage partition."""

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {"$denseRank": {}}


@dataclass
class Derivative(WindowOperator):
    """Returns the average rate of change within the specified window."""

    input: Input
    """any valid expression that resolves to a number.
    """

    unit: DateUnit

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$derivative": {
                "input": compile_expression(self.input, context=context),
                "unit": compile_expression(self.unit, context=context),
            },
        }


@dataclass
class DocumentNumber(WindowOperator):
    """Returns the position of a document (known as the document number) in the $setWindowFields stage partition."""

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {"$documentNumber": {}}


@dataclass
class ExpMovingAvg(WindowOperator):
    """Returns the exponential moving average of numeric expressions applied to documents in a partition defined in the $setWindowFields stage."""

    input: NumberExpression
    """any valid expression as long as it resolves to a number"""

    n: int | None = None
    """any valid expression as long as it resolves to a number"""

    alpha: float | None = None
    """any valid expression as long as it resolves to a number"""

    def __post_init__(self) -> None:
        if self.n is not None and self.alpha is not None:
            msg = "n or alpha, not both"
            raise TypeError(msg)

        if self.n is None and self.alpha is None:
            msg = "n or alpha required"
            raise TypeError(msg)

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$expMovingAvg": nullfree_dict(
                {
                    "input": compile_expression(self.input, context=context),
                    "N": compile_expression(self.n, context=context),
                    "alpha": compile_expression(self.alpha, context=context),
                }
            ),
        }


@dataclass
class First(WindowOperator):
    """Returns the result of an expression for the first document in a group of documents."""

    input: Input
    """The expression to evaluate."""

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$first": compile_expression(self.input, context=context),
        }


@dataclass
class Integral(WindowOperator):
    """Returns the approximation of the area under a curve."""

    input: Input
    """an expression that returns a number."""

    unit: DateUnit | None = None

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$integral": nullfree_dict(
                {
                    "input": compile_expression(self.input, context=context),
                    "unit": compile_expression(self.unit, context=context),
                }
            ),
        }


@dataclass
class Last(WindowOperator):
    """Returns the result of an expression for the last document in a group of documents."""

    input: Input
    """The expression to evaluate."""

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$last": compile_expression(self.input, context=context),
        }


@dataclass
class LinearFill(WindowOperator):
    """Fills null and missing fields in a window using linear interpolation based on surrounding field values."""

    input: Input
    """The expression to evaluate."""

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$linearFill": compile_expression(self.input, context=context),
        }


@dataclass
class Locf(WindowOperator):
    """Last observation carried forward."""

    input: Input
    """Any valid expression"""

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {"$locf": compile_expression(self.input, context=context)}


@dataclass
class Median(WindowOperator):
    """Returns an approximation of the median value."""

    input: Input

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$median": {
                "input": compile_expression(self.input, context=context),
                "method": "approximate",
            },
        }


@dataclass
class MinMaxScaler(WindowOperator):
    """Normalizes a numeric expression within a window of values."""

    input: Input
    """An expression that resolves to the array"""

    min: Input = 0
    """An expression that resolves to a positive integer"""

    max: Input = 1
    """An expression that resolves to a positive integer"""

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$minMaxScaler": {
                "input": compile_expression(self.input, context=context),
                "min": compile_expression(self.min, context=context),
                "max": compile_expression(self.max, context=context),
            },
        }


@dataclass
class Rank(WindowOperator):
    """Returns the document position (known as the rank) relative to other documents in the $setWindowFields stage partition."""

    def compile_operation(self, *, context: Context) -> Input:
        return {
            "$rank": {},
        }


@dataclass
class Shift(WindowOperator):
    """Returns the value from an expression applied to a document in a specified position relative to the current document in the $setWindowFields stage partition."""

    output: Input
    by: Input
    default: Input

    def compile_operation(self, *, context: Context) -> MongoExpression:
        return {
            "$shift": {
                "output": compile_expression(self.output, context=context),
                "by": compile_expression(self.by, context=context),
                "default": compile_expression(self.default, context=context),
            },
        }
