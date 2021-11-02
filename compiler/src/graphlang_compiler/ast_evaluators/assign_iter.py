from dataclasses import dataclass
from itertools import chain
from typing import Dict, List, Iterable

from graphlang_compiler.ast_evaluators import Evaluator, Variable, Traverse, CollectionList
from graphlang_compiler.consts import Direction
from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import Projection
from graphlang_compiler.utility import some_util


@dataclass
class AssignIter(Evaluator):
    left: List[Variable]
    right: Evaluator
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

        is_right_block = self.right.__class__.__name__ == 'Block'
        return EvalResult(
            expression=f'''{", ".join(left)} in {f'({right})' if is_right_block else right}''',
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

        elif isinstance(self.right, CollectionList):
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

