from abc import ABC, abstractmethod
from typing import Dict, List

from dataclasses import field, dataclass

from graphlang_compiler.ast_evaluators import Evaluator
from graphlang_compiler.consts import Direction
from graphlang_compiler.projection import DocumentProjection
from graphlang_compiler.ast_evaluators.collection import Collection
from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import Projection
from graphlang_compiler.utility import some_util


@dataclass
class Traverse(Evaluator):
    origin: Evaluator
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
