from dataclasses import dataclass
from typing import Dict

from graphlang_compiler.ast_evaluators import Evaluator
from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import ValueProjection, Projection
from graphlang_compiler.utility import unique_name


@dataclass
class Literal(Evaluator):
    value: Evaluator
    kind: str = 'Literal'

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return ValueProjection()

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
