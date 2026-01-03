from django.urls.resolvers import URLPattern, URLResolver
from typing import (
    List,
    Optional,
    Tuple,
    Union,
    TypedDict,
)
from enum import Enum


class CapturedResolver(TypedDict):
    resolver: URLResolver
    namespace: Optional[str]
    children: List["CapturedNode"]
    

CapturedNode = Union[URLPattern, CapturedResolver]
RouteSpec = Tuple[str, Optional[str]]  # (view_name, route_name)


class ExperimentType(Enum):
    ABTEST = 1
    JOURNEY = 2