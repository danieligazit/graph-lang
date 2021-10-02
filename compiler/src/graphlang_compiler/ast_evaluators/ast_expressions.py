import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from itertools import chain
from typing import List, Any, Type, Iterable, Union, Dict
from graphlang_compiler.consts import ARANGO_OPS, CYPHER_OPS, Functions, ARANGO_FUNCTIONS, CYPHER_FUNCTIONS, Direction, Ops
from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import ValueProjection, Projection, DocumentProjection, ArrayProjection, MappingProjection
from graphlang_compiler.user_var import Var
from graphlang_compiler.utility import some_util, unique_name







@dataclass
class Collection(Ast):
    name: str
    kind: str = 'Collection'

    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        return self.projections()

    def project(self, projections: Dict[str, Projection]) -> Projection:
        raise ValueError

    def aliases(self):
        return []

    def evaluate_arango(self):
        bind = unique_name()
        return EvalResult(
            expression=f'@@{bind}',
            binds={f'@{bind}': self.name}
        )

    def evaluate_cypher(self):
        return EvalResult(
            expression=self.name,
            binds={}
        )


@dataclass
class MultiExpression(Ast):
    expressions: List[Ast] = field(default_factory=list)
    kind: str = 'MultiExpression'

    def project(self, projections: Dict[str, Projection]) -> Projection:
        raise ValueError

    def projections(self, projections):
        for expression in self.expressions:
            projections.update(expression.projections(projections))

        return projections

    def aliases(self):
        return list(set(chain.from_iterable([expression.aliases() for expression in self.expressions])))

    def evaluate_arango(self) -> EvalResult:
        binds, *expressions = some_util((e.evaluate_arango() for e in self.expressions))
        return EvalResult(
            expression='\n'.join(expressions),
            binds=binds
        )

    def evaluate_cypher(self) -> EvalResult:
        and_ops = []
        reduced_expressions = []
        for expression in self.expressions:
            if isinstance(expression, Filter):
                and_ops.append(expression.x)
                continue

            if and_ops:
                reduced_expressions.append(Filter(FunctionCall(Functions.ALL, and_ops)))
                and_ops = []

            reduced_expressions.append(expression)

        if and_ops:
            reduced_expressions.append(Filter(FunctionCall(Functions.ALL, and_ops)))

        binds, *expressions = some_util((e.evaluate_cypher() for e in reduced_expressions))
        return EvalResult(
            expression='\n'.join(expressions),
            binds=binds
        )

    def dump(self):
        return [item.dump() for item in self.expressions]


@dataclass
class Collections(Ast):
    collections: List[Collection]
    kind: str = 'Collections'

    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        return projections

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return DocumentProjection()

    def aliases(self):
        return []

    def evaluate_arango(self):
        iterators = []

        binds, *collections = some_util(
            [collection.evaluate_arango() for collection in self.collections]
        )

        if len(collections) == 1:
            return EvalResult(
                expression=f'{collections[0]}',
                binds=binds
            )

        for collection in collections:
            iterators.append(collection)

        return EvalResult(
            expression=f'''FLATTEN([[{'], ['.join(iterators)}]])''',
            binds=binds
        )

    def evaluate_cypher(self):
        binds, *collections = some_util(
            [collection.evaluate_cypher() for collection in self.collections]
        )

        collections = '|'.join(collections)

        return EvalResult(
            expression=f'{collections}',
            binds=binds
        )


@dataclass
class Traverse(Ast):
    origin: Ast
    direction: str
    edge_collections: List[Collection] = field(default_factory=list)
    vertex_collections: List[Collection] = field(default_factory=list)
    kind: str = 'Traverse'

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return DocumentProjection(), DocumentProjection()

    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        return projections

    def aliases(self):
        return [self.origin]

    def evaluate_arango(self):
        binds, origin, *edge_collections = some_util(
            self.origin.evaluate_arango(),
            (edge_col.evaluate_arango() for edge_col in self.edge_collections),
        )

        iterators = [
            f'{self.direction} {origin} {", ".join(edge_collections)}',
        ]

        return EvalResult(
            expression='\n'.join(iterators),
            binds=binds
        )

    def evaluate_cypher(self):
        lhs_arrow, rhs_arrow = {
            Direction.INBOUND: ('<-', '-'),
            Direction.OUTBOUND: ('-', '->'),
        }[self.direction]

        binds, vertex, edge, origin, *edge_collections = some_util(
            self.vertex.evaluate_cypher(),
            self.edge.evaluate_cypher(),
            self.origin.evaluate_cypher(),
            (edge_col.evaluate_cypher() for edge_col in self.edge_collections),
        )

        v_col_binds, *vertex_collections = some_util(
            (vertex_col.evaluate_cypher() for vertex_col in self.vertex_collections)
        )

        binds.update(v_col_binds)

        e_col = ':' + '|'.join(edge_collections) if edge_collections else ''
        v_col = ':' + '|'.join(vertex_collections) if vertex_collections else ''

        return EvalResult(
            expression=f'({origin}) {lhs_arrow}[{edge}{e_col}]{rhs_arrow} ({vertex}{v_col})',
            binds=binds
        )


@dataclass
class Block(Ast):
    item: Ast
    returns: Ast
    do: MultiExpression = field(default_factory=lambda: MultiExpression())
    inline: bool = True
    kind: str = 'Block'

    def aliases(self):
        return self.item.aliases()

    def projections(self, projections):
        projections = self.item.projections(projections)
        projections.update(self.do.projections(projections))
        return projections

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return self.returns.project(projections)

    def evaluate_arango(self):
        for expression in self.do.expressions:
            if isinstance(expression, Block):
                expression.inline = False

        binds, item, returns, *do = some_util(
            self.item.evaluate_arango(),
            self.returns.evaluate_arango() if self.returns else EvalResult(),
            (expression.evaluate_arango() for expression in self.do.expressions)
        )

        if isinstance(self.item, AssignIter) and isinstance(self.item.right, Traverse):
            vertex = self.item.left[0]

            v_col_expressions = []

            for v_col in self.item.right.vertex_collections:
                bind = unique_name()
                binds[bind] = v_col.name
                v_col_expressions.append(f"is_same_collection({vertex.name}, @{bind})")

            if v_col_expressions:
                do.insert(0, f'''filter {" or ".join(v_col_expressions)}''')

        expression = '\n'.join([f'for {item}'] + do + ([f'return {returns}'] if returns else []))

        return EvalResult(
            expression=f'({expression})' if self.inline else expression,
            binds=binds
        )

    def evaluate_cypher(self):
        binds, item, returns, do = some_util(
            self.item.evaluate_cypher(),
            self.returns.evaluate_cypher() if self.returns else EvalResult(),
            self.do.evaluate_cypher()
        )

        expression = '\n'.join([
            item,
            do,
            f'| {returns}' if self.inline else f'return {returns}'
        ])

        return EvalResult(
            expression=f'[{expression}]' if self.inline else f'match {expression}',
            binds=binds
        )


@dataclass
class Filter(Ast):
    x: Ast
    kind: str = 'Filter'

    def aliases(self):
        return self.x.aliases()

    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        return self.x.projections(projections)

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return self.x.project(projections)

    def evaluate_arango(self):
        x = self.x.evaluate_arango()
        return EvalResult(
            expression=f'filter {x.expression}',
            binds=x.binds
        )

    def evaluate_cypher(self):
        x = self.x.evaluate_cypher()
        return EvalResult(
            expression=f'where {x.expression}',
            binds=x.binds
        )


@dataclass
class Declare(Ast):
    x: Ast
    kind: str = 'Declare'

    def aliases(self):
        return self.x.aliases()

    def evaluate_arango(self):
        return EvalResult()

    def evaluate_cypher(self):
        x = self.x.evaluate_cypher()

        if isinstance(self.x, (IterCollection, Traverse, Block)):
            return EvalResult(
                expression=f'match {x.expression}',
                binds=x.binds
            )

        return EvalResult(
            expression=f'with {x.expression}',
            binds=x.binds
        )


@dataclass
class AssignIter(Ast):
    left: List[Variable]
    right: Ast
    kind: str = 'AssignIter'

    def project(self, projections: Dict[str, Projection]) -> Projection:
        raise ValueError

    def projections(self, projections: Dict[str, Projection]):
        if len(self.left) == 1:
            projections[self.left[0].name] = self.right.project(projections)
            return projections

        for i, right in enumerate(self.right.project(projections)):
            projections[self.left[i].name] = right

        return projections

    def aliases(self):
        if isinstance(self.right, Iterable):
            return list(chain.from_iterable([item.aliases() for item in self.right]))

        return self.right.aliases()

    def evaluate_arango(self):
        binds, *left, right = some_util(
            (item.evaluate_arango() for item in self.left),
            self.right.evaluate_arango()
        )

        return EvalResult(
            expression=f'''{", ".join(left)} in {f'({right})' if isinstance(self.right, Block) else right}''',
            binds=binds
        )

    def evaluate_cypher(self) -> EvalResult:

        if isinstance(self.right, Traverse):
            lhs_arrow, rhs_arrow = {
                Direction.INBOUND: ('<-', '-'),
                Direction.OUTBOUND: ('-', '->'),
            }[self.right.direction]

            binds, vertex, edge, origin, *edge_collections = some_util(
                self.left[0].evaluate_cypher(),
                self.left[1].evaluate_cypher(),
                self.right.origin.evaluate_cypher(),
                (edge_col.evaluate_cypher() for edge_col in self.right.edge_collections),
            )

            v_col_binds, *vertex_collections = some_util(
                (vertex_col.evaluate_cypher() for vertex_col in self.right.vertex_collections)
            )

            binds.update(v_col_binds)

            e_col = ':' + '|'.join(edge_collections) if edge_collections else ''
            v_col = ':' + '|'.join(vertex_collections) if vertex_collections else ''

            return EvalResult(
                expression=f'({origin}) {lhs_arrow}[{edge}{e_col}]{rhs_arrow} ({vertex}{v_col})',
                binds=binds
            )

        elif isinstance(self.right, Collections):
            binds, left, *collections = some_util(
                self.left[0].evaluate_cypher(),
                (collection.evaluate_cypher() for collection in self.right.collections)
            )

            collections = ':' + '|'.join(collections) if collections else ''

            return EvalResult(
                expression=f"({left}{collections})",
                binds=binds
            )

        raise ValueError


@dataclass
class Assign(Ast):
    left: List[Variable]
    right: Union[List[Ast], Ast]
    declare_all: bool = True
    kind: str = 'Assign'

    def project(self, projections: Dict[str, Projection]) -> Projection:
        raise ValueError

    def projections(self, projections: Dict[str, Projection]):
        if isinstance(self.right, Iterable):
            for i, left in enumerate(self.left):
                projections.update(self.right[i].projections(projections))
                projections[left.name] = self.right[i].project(projections)

            return projections

        if len(self.left) == 1:
            projections.update(self.right.projections(projections))
            projections[self.left[0].name] = self.right.project(projections)
            return projections

        for i, right in enumerate(self.right.projections(projections)):
            projections.update(self.right.projections(projections))
            projections[self.left[i].name] = right

        return projections

    def aliases(self):
        if isinstance(self.right, Iterable):
            return list(chain.from_iterable([item.aliases() for item in self.right]))

        return self.right.aliases()

    def evaluate_arango(self):
        if isinstance(self.right, list):
            binds_left, *left = some_util(
                (item.evaluate_arango() for item in self.left),
            )

            binds_right, *right = some_util(
                (item.evaluate_arango() for item in self.right),
            )

            rows = []
            for i, item in enumerate(left):
                rows.append(f'let {item} = {right[i]}')

            return EvalResult(
                expression='\n'.join(rows),
                binds=binds_left.update(binds_right) or binds_right
            )

        binds, *left, right = some_util(
            (item.evaluate_arango() for item in self.left),
            self.right.evaluate_arango()
        )

        return EvalResult(
            expression=f'''let {", ".join(left)} = {f'({right})' if isinstance(self.right, Block) else right}''',
            binds=binds
        )

    def evaluate_cypher(self) -> EvalResult:
        if isinstance(self.right, list):
            binds_left, *left = some_util(
                (item.evaluate_cypher() for item in self.left),
            )

            binds_right, *right = some_util(
                (item.evaluate_cypher() for item in self.right),
            )

            assert len(left) == len(right)

            rows = []
            for i, item in enumerate(left):
                rows.append(f'{right[i]} as {item}')

            return EvalResult(
                expression=f"with {'*,' if self.declare_all else ''} {', '.join(rows)}",
                binds=binds_left.update(binds_right) or binds_right
            )

        binds, *left, right = some_util(
            (item.evaluate_cypher() for item in self.left),
            self.right.evaluate_cypher()
        )

        return EvalResult(
            expression=f"with {'*, ' if self.declare_all else ''}{right} as {', '.join(left)}",
            binds=binds
        )


@dataclass
class BinaryOp(Ast):
    op: str
    left: Ast
    right: Ast
    kind: str = 'BinaryOp'

    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        projections.update(self.left.projections(projections))
        projections.update(self.right.projections(projections))
        return projections

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return ValueProjection

    def aliases(self):
        return self.left.aliases() + self.right.aliases()

    def evaluate_arango(self):
        binds, left, right = some_util(
            self.left.evaluate_arango(),
            self.right.evaluate_arango()
        )

        return EvalResult(
            expression=f'{left} {ARANGO_OPS[self.op]} {right}',
            binds=binds
        )

    def evaluate_cypher(self):
        binds, left, right = some_util(
            self.left.evaluate_cypher(),
            self.right.evaluate_cypher()
        )

        return EvalResult(
            expression=f'{left} {CYPHER_OPS[self.op]} {right}',
            binds=binds
        )


@dataclass
class Attribute(Ast):
    ob: Ast
    name: str
    kind: str = 'Attribute'

    def aliases(self):
        return self.ob.aliases()

    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        return projections

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return ValueProjection

    def evaluate_arango(self):
        ob = self.ob.evaluate_arango()

        bind = unique_name()
        ob.binds[bind] = self.name

        return EvalResult(
            expression=f'{ob.expression}[@{bind}]',
            binds=ob.binds
        )

    def evaluate_cypher(self):
        ob = self.ob.evaluate_cypher()

        return EvalResult(
            expression=f'{ob.expression}.{self.name}',
            binds=ob.binds
        )


@dataclass
class EmptyType(Ast):
    kind: str = 'EmptyType'

    def aliases(self):
        return []

    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        return projections

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return ValueProjection

    def evaluate_arango(self):
        return EvalResult('', {})

    def evaluate_cypher(self):
        return EvalResult('', {})


@dataclass
class Literal(Ast):
    value: Any
    kind: str = 'Literal'

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return ValueProjection

    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        return projections

    def aliases(self):
        return []

    def evaluate_arango(self):
        bind = unique_name()
        return EvalResult(
            expression=f'@{bind}',
            binds={bind: self.value}
        )

    def evaluate_cypher(self):
        bind = unique_name()
        return EvalResult(
            expression=f'${bind}',
            binds={bind: self.value}
        )


@dataclass
class Mapping(Ast):
    mapping: Dict[str, Ast]
    kind: str = 'Mapping'

    def aliases(self):
        return list(chain.from_iterable([arg.aliases() for arg in self.mapping.values()]))

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return MappingProjection(mapping={
            key: value.project(projections)
            for key, value in self.mapping.items()
        })

    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        for value in self.mapping.values():
            projections.update(value.projections(projections))

        return projections

    def evaluate_arango(self) -> EvalResult:
        binds = {}
        expressions = []

        for key, value in self.mapping.items():
            mapping_bind, expression = some_util(value.evaluate_arango())
            bind = unique_name()
            mapping_bind[bind] = key
            expressions.append(f'@{bind}: {expression}')
            binds.update(mapping_bind)

        return EvalResult(
            expression=f'{{{",".join(expressions)}}}',
            binds=binds
        )

    def evaluate_cypher(self) -> EvalResult:
        binds = {}
        expressions = []

        for key, value in self.mapping.items():
            mapping_bind, expression = some_util(value.evaluate_cypher())
            expressions.append(f'{key}: {expression}')
            binds.update(mapping_bind)

        return EvalResult(
            expression=f'{{{",".join(expressions)}}}',
            binds=binds
        )


@dataclass
class DeclareAll(Ast):
    kind: str = 'DeclareAll'

    def aliases(self):
        return []

    def evaluate_arango(self) -> EvalResult:
        return EvalResult()

    def evaluate_cypher(self) -> EvalResult:
        return EvalResult(
            expression='with *',
            binds={}
        )


@dataclass
class Query(Ast):
    root: Block
    pos: Block
    kind: str = 'Query'

    def aliases(self):
        return self.root.aliases()

    def projections(self, projections):
        return self.root.projections(projections)

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return ArrayProjection(item=self.pos.project(projections))

    def evaluate_arango(self) -> EvalResult:
        return self.root.evaluate_arango()

    def evaluate_cypher(self) -> EvalResult:
        return self.root.evaluate_cypher()
