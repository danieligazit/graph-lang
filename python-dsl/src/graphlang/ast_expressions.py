from abc import ABC
from dataclasses import dataclass, field
from typing import List, Any, Union, Dict, Optional

from graphlang.utility import unique_name


class Ast(ABC):
    pass


@dataclass
class Variable(Ast):
    name: Optional[str] = None
    kind: str = 'Variable'

    def __post_init__(self):
        self.name = self.name or unique_name()


@dataclass
class FunctionCall(Ast):
    function: str
    args: List[Ast]
    kind: str = 'FunctionCall'


@dataclass
class Collection(Ast):
    name: str
    kind: str = 'Collection'


@dataclass
class MultiExpression(Ast):
    expressions: List[Ast] = field(default_factory=list)
    kind: str = 'MultiExpression'


@dataclass
class CollectionList(Ast):
    collections: List[Collection]
    kind: str = 'CollectionList'


@dataclass
class Traverse(Ast):
    origin: Ast
    direction: str
    edge_collections: List[Collection] = field(default_factory=list)
    vertex_collections: List[Collection] = field(default_factory=list)
    kind: str = 'Traverse'


@dataclass
class Block(Ast):
    item: Ast
    returns: Ast
    do: MultiExpression = field(default_factory=lambda: MultiExpression())
    inline: bool = True
    kind: str = 'Block'


@dataclass
class Filter(Ast):
    x: Ast
    kind: str = 'Filter'


@dataclass
class Declare(Ast):
    x: Ast
    kind: str = 'Declare'


@dataclass
class AssignIter(Ast):
    left: List[Variable]
    right: Ast
    kind: str = 'AssignIter'


@dataclass
class Assign(Ast):
    left: List[Variable]
    right: Union[List[Ast], Ast]
    declare_all: bool = True
    kind: str = 'Assign'


@dataclass
class BinaryOp(Ast):
    op: str
    left: Ast
    right: Ast
    kind: str = 'BinaryOp'


@dataclass
class Attribute(Ast):
    ob: Ast
    name: str
    kind: str = 'Attribute'


@dataclass
class EmptyType(Ast):
    kind: str = 'EmptyType'


@dataclass
class Literal(Ast):
    value: Any
    kind: str = 'Literal'


@dataclass
class Mapping(Ast):
    mapping: Dict[str, Ast]
    kind: str = 'Mapping'


@dataclass
class Query(Ast):
    root: Block
    pos: Block
    kind: str = 'Query'
