from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict


class Projection(ABC):
    pass


@dataclass
class ValueProjection(Projection):
    kind: str = 'ValueProjection'


@dataclass
class DocumentProjection(Projection):
    kind: str = 'DocumentProjection'


@dataclass
class ArrayProjection(Projection):
    item: Projection
    kind: str = 'ArrayProjection'


@dataclass
class MappingProjection(Projection):
    mapping: Dict[str, Projection]
    kind: str = 'MappingProjection'
