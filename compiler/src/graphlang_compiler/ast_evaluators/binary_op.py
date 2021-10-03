from dataclasses import dataclass
from typing import Dict

from graphlang_compiler.ast_evaluators import Evaluator
from graphlang_compiler.consts import CYPHER_OPS, ARANGO_OPS
from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import Projection, ValueProjection
from graphlang_compiler.utility import some_util


@dataclass
class BinaryOp(Evaluator):
    op: str
    left: Evaluator
    right: Evaluator
    kind: str = 'BinaryOp'

    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        projections.update(self.left.projections(projections))
        projections.update(self.right.projections(projections))
        return projections

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return ValueProjection()

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