from typing import TypeVar, Dict, Any, Callable

# Generic type variables
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

# Common aliases
JSONDict = Dict[str, Any]
Predicate = Callable[[Any], bool]
