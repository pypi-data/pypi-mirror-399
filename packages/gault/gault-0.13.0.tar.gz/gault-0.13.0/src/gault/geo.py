from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, NotRequired, TypeAlias

from .shapes import Coordinates, Shape

if TYPE_CHECKING:
    from typing_extensions import TypedDict

    from .types import Context, MongoExpression

    class PointDict(TypedDict):
        type: Literal["Point"]
        coordinates: Any
        crs: NotRequired[Any]

    PointLike: TypeAlias = "PointDict" | "Point"

    class LineStringDict(TypedDict):
        type: Literal["LineString"]
        coordinates: Any
        crs: NotRequired[Any]

    LineStringLike: TypeAlias = "LineStringDict" | "LineString"

    class PolygonDict(TypedDict):
        type: Literal["Polygon"]
        coordinates: Any
        crs: NotRequired[Any]

    PolygonLike: TypeAlias = "PolygonDict" | "Polygon"

    class MultiPointDict(TypedDict):
        type: Literal["MultiPoint"]
        coordinates: Any
        crs: NotRequired[Any]

    MultiPointLike: TypeAlias = "MultiPointDict" | "MultiPoint"

    class MultiLineStringDict(TypedDict):
        type: Literal["MultiLineString"]
        coordinates: Any
        crs: NotRequired[Any]

    MultiLineStringLike: TypeAlias = "MultiLineStringDict" | "MultiLineString"

    class MultiPolygonDict(TypedDict):
        type: Literal["MultiPolygon"]
        coordinates: Any
        crs: NotRequired[Any]

    MultiPolygonLike: TypeAlias = "MultiPolygonDict" | "MultiPolygon"

    class GeometryCollectionDict(TypedDict):
        type: Literal["GeometryCollection"]
        coordinates: Any
        crs: NotRequired[Any]

    GeometryCollectionLike: TypeAlias = "GeometryCollectionDict" | "GeometryCollection"

    GeoJSONDict: TypeAlias = (
        "PointDict"
        | "LineStringDict"
        | "PolygonDict"
        | "MultiPointDict"
        | "MultiLineStringDict"
        | "MultiPolygonDict"
        | "GeometryCollectionDict"
    )

    GeoJSONLike: TypeAlias = "GeoJSON" | "GeoJSONDict"


def compile_geo(
    value: GeoJSONLike | MongoExpression | Shape | Coordinates, *, context: Context
) -> Any:
    match value:
        case {"$box": _} | {"$center": _} | {"$centerSphere": _} | {"$polygon": _}:
            # https://www.mongodb.com/docs/manual/reference/operator/query/box/
            # https://www.mongodb.com/docs/manual/reference/operator/query/center/
            # https://www.mongodb.com/docs/manual/reference/operator/query/centerSphere/
            return value
        case {"$geometry": _}:
            # https://www.mongodb.com/docs/manual/reference/operator/query/geometry/
            return value
        case {
            "type": "Point"
            | "LineString"
            | "Polygon"
            | "MultiPoint"
            | "MultiLineString"
            | "MultiPolygon"
            | "GeometryCollection"
        }:
            return {"$geometry": value}

        case GeoJSON():
            return value.compile_expression(context=context)
        case Shape():
            return value.compile_expression(context=context)
        case Coordinates():
            return {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [value.x, value.y],
                }
            }
        case _:
            raise NotImplementedError


class GeoJSON(ABC):
    @abstractmethod
    def compile_expression(self, *, context: Context) -> MongoExpression: ...

    @abstractmethod
    def get_coordinates(self) -> Any: ...


@dataclass
class Point(GeoJSON):
    x: float
    y: float

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$geometry": {
                "type": "Point",
                "coordinates": self.get_coordinates(),
            }
        }

    def get_coordinates(self) -> Any:
        return [self.x, self.y]


@dataclass
class LineString(GeoJSON):
    points: list[Point]

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$geometry": {
                "type": "LineString",
                "coordinates": self.get_coordinates(),
            }
        }

    def get_coordinates(self) -> Any:
        return [point.get_coordinates() for point in self.points]


@dataclass
class Polygon(GeoJSON):
    line_strings: list[LineString]
    crs: Literal["urn:x-mongodb:crs:strictwinding:EPSG:4326"] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression:
        if name := self.crs:
            custom = {
                "crs": {
                    "type": "name",
                    "properties": {"name": name},
                },
            }
        else:
            custom = {}
        return {
            "$geometry": {
                "type": "Polygon",
                "coordinates": self.get_coordinates(),
            }
            | custom
        }

    def get_coordinates(self) -> Any:
        return [line_string.get_coordinates() for line_string in self.line_strings]


@dataclass
class MultiPoint(GeoJSON):
    points: list[Point]

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$geometry": {
                "type": "MultiPoint",
                "coordinates": self.get_coordinates(),
            }
        }

    def get_coordinates(self) -> Any:
        return [point.get_coordinates() for point in self.points]


@dataclass
class MultiLineString(GeoJSON):
    line_strings: list[LineString]

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$geometry": {
                "type": "MultiLineString",
                "coordinates": self.get_coordinates(),
            }
        }

    def get_coordinates(self) -> Any:
        return [line_string.get_coordinates() for line_string in self.line_strings]


@dataclass
class MultiPolygon(GeoJSON):
    polygons: list[Polygon]
    crs: Literal["urn:x-mongodb:crs:strictwinding:EPSG:4326"] | None = None

    def compile_expression(self, *, context: Context) -> MongoExpression:
        if name := self.crs:
            custom = {
                "crs": {
                    "type": "name",
                    "properties": {"name": name},
                },
            }
        else:
            custom = {}
        return {
            "$geometry": {
                "type": "MultiPolygon",
                "coordinates": self.get_coordinates(),
            }
            | custom
        }

    def get_coordinates(self) -> Any:
        return [polygon.get_coordinates() for polygon in self.polygons]


@dataclass
class GeometryCollection(GeoJSON):
    geometries: list[GeoJSON]

    def compile_expression(self, *, context: Context) -> MongoExpression:
        return {
            "$geometry": {
                "type": "GeometryCollection",
                "geometries": [
                    geometry.compile_expression(context=context)["$geometry"]  # type: ignore[call-overload, index]
                    for geometry in self.geometries
                ],
            }
        }

    def get_coordinates(self) -> Any:
        return [geometry.get_coordinates() for geometry in self.geometries]
