from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeAlias

if TYPE_CHECKING:
    from typing import TypedDict

    from .types import Context, MongoExpression

    ShapeLike: TypeAlias = "BoxLike" | "CenteLike" | "CenterSphereLike" | "PolygonLike"

    BoxDict = TypedDict("BoxDict", {"$box": Any})
    BoxLike: TypeAlias = "BoxDict" | "Box"

    CenterDict = TypedDict("CenterDict", {"$center": Any})
    CenteLike: TypeAlias = "CenterDict" | "Center"

    CenterSphereDict = TypedDict("CenterSphereDict", {"$centerSphere": Any})
    CenterSphereLike: TypeAlias = "CenterSphereDict" | "CenterSphere"

    PolygonDict = TypedDict("PolygonDict", {"$polygon": Any})
    PolygonLike: TypeAlias = "PolygonDict" | "Polygon"


class Shape(ABC):
    @abstractmethod
    def compile_expression(self, *, context: Context) -> MongoExpression:
        pass


@dataclass
class Box(Shape):
    bottom_left_coordinates: Coordinates
    upper_right_coordinates: Coordinates

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$box": [
                [self.bottom_left_coordinates.x, self.bottom_left_coordinates.y],
                [self.upper_right_coordinates.x, self.upper_right_coordinates.y],
            ],
        }


@dataclass
class Center(Shape):
    x: float
    y: float
    radius: float

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$center": [
                [self.x, self.y],
                self.radius,
            ],
        }


@dataclass
class CenterSphere(Shape):
    x: float
    y: float
    radius: float

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$centerSphere": [
                [self.x, self.y],
                self.radius,
            ],
        }


@dataclass
class Polygon(Shape):
    points: list[Coordinates]

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$polygon": [[point.x, point.y] for point in self.points],
        }


@dataclass
class Coordinates:
    x: float
    y: float
