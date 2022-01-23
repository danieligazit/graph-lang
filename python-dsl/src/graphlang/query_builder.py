from dataclasses import dataclass
from typing import Type, Iterable, Union, Any

from graphlang.ast_expressions import Assign, Filter, BinaryOp, Attribute, Literal, Traverse, Variable, Collection, \
    AssignIter, Block, EmptyType, FunctionCall, Mapping, Query, CollectionList, Ast
from graphlang.consts import Direction, Ops, Functions
from graphlang.utility import unique_name


@dataclass
class Var:
    name: str


class QueryBuilder:
    def __init__(self, query: Query):
        self._query: Query = query

    def match(self, *args, **kwargs):
        for arg in args:
            if isinstance(arg, QueryBuilder):
                arg = arg._query

            if isinstance(arg, FieldArgument):
                arg = BinaryOp(
                    op=arg.op,
                    left=Attribute(
                        ob=self._query.root.returns,
                        name=arg.key
                    ),
                    right=Literal(arg.value)
                )

            # aliases = arg.aliases()
            # if aliases:
            #     self._query.pos.do.expressions += [
            #         Assign(aliases, [self.pos.returns] * len(aliases)),
            #         Filter(x=arg)
            #     ]
            # else:
            self._query.pos.do.expressions.append(Filter(x=arg))

        for key, value in kwargs.items():
            if isinstance(value, QueryBuilder):
                value = value._query

            self._query.pos.do.expressions.append(
                Filter(
                    x=BinaryOp(
                        op=Ops.EQ,
                        left=Attribute(
                            ob=self._query.root.returns,
                            name=key
                        ),
                        right=Literal(value)
                    )
                )
            )
        return self

    def traverse(self, *edges: Union[Iterable[Type], Type], direction: str = Direction.OUTBOUND):
        edges = edges if isinstance(edges, Iterable) else [edges]

        vertex, edge = Variable(), Variable()

        traversal = Traverse(
            origin=self._query.pos.returns,
            direction=direction,
            edge_collections=[Collection(edge) for edge in edges],
            vertex_collections=[]
        )

        block = Block(
            item=AssignIter([vertex, edge], traversal),
            returns=edge,
        )
        self._query.root.do.expressions.append(block)
        self._query.pos.returns = EmptyType()
        self._query.pos = block

        return self

    def traverse_out(self, *edges: Union[Iterable[Type], Type]):
        return self.traverse(*edges, direction=Direction.OUTBOUND)

    def traverse_in(self, *edges: Union[Iterable[Type], Type]):
        return self.traverse(*edges, direction=Direction.INBOUND)

    def into(self, *vertices):
        vertices = vertices if isinstance(vertices, Iterable) else [vertices]
        self._query.pos.returns = self._query.pos.item.left[0]
        self._query.pos.item.right.vertex_collections = [Collection(vertex) for vertex in vertices]
        return self

    def count(self):
        self._query.root = FunctionCall(Functions.LENGTH, args=[self._query.root])

        return self

    def _compare(self, op: str, other):

        if isinstance(other, Query):
            return BinaryOp(
                op, self._query.root, other._query.root
            )

        return BinaryOp(op, self._query.root, other if isinstance(other, Ast) else Literal(value=other))

    def array(self, sub_query: 'QueryBuilder'):
        sub_query = sub_query._query

        aliases = []  # sub_query.aliases()
        var = Variable()

        expressions = [
            Assign(aliases, [self._query.pos.returns] * len(aliases))
        ] if aliases else []

        expressions.append(
            Assign([var], sub_query)
        )

        self._query.pos.returns = var
        self._query.pos.do.expressions += expressions

        return self

    def as_var(self, var_name: str):
        var = Variable(var_name)
        self._query.pos.do.expressions.append(
            Assign([var], self.pos.returns)
        )

        return self

    def select(self, *args: Union[str, Var], **kwargs):
        mapping = {}

        for arg in args:
            if arg in kwargs:
                raise ValueError(f'duplicate mapping key {arg}')  # TODO: custom error

            kwargs[arg] = arg

        for arg, item in kwargs.items():
            if isinstance(item, str):
                mapping[arg] = Attribute(self._query.pos.returns, name=arg)

            if isinstance(item, Var):
                mapping[arg] = Variable(item.name)

        self._query.pos.returns = Mapping(mapping=mapping)
        return self

    def __getitem__(self, item: str):
        self._query.pos.returns = Attribute(self._query.pos.returns, name=item)
        return self

    def __gt__(self, other: 'QueryBuilder'):
        return self._compare(Ops.GT, other)

    def __eq__(self, other: 'QueryBuilder'):
        return self._compare(Ops.EQ, other._query)

    def get_query(self) -> Query:
        return self._query


def get(*vertices: str) -> QueryBuilder:
    vertices = vertices if isinstance(vertices, Iterable) else [vertices]
    item = Variable(unique_name())
    block = Block(
        item=AssignIter(
            left=[item],
            right=CollectionList(collections=[Collection(col) for col in vertices])
        ),
        returns=item
    )
    return QueryBuilder(
        query=Query(
            root=block,
            pos=block
        )
    )


def traverse(*edges: Union[Iterable[Type], Type], direction: str = Direction.OUTBOUND):
    edges = edges if isinstance(edges, Iterable) else [edges]

    vertex, edge = Variable(unique_name()), Variable(unique_name())
    origin = Variable(unique_name())

    traversal = Traverse(
        origin=origin,
        direction=direction,
        edge_collections=[Collection(e) for e in edges],
        vertex_collections=[]
    )

    block = Block(
        item=AssignIter([vertex, edge], traversal),
        returns=edge
    )

    return QueryBuilder(
        query=Query(
            root=block,
            pos=block
        )
    )


@dataclass
class FieldArgument:
    key: str
    op: str
    value: Any


def gt(field: str, value: Any):
    return FieldArgument(
        key=field,
        op=Ops.GT,
        value=value
    )
