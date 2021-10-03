from dataclasses import dataclass
from typing import Dict

from graphlang_compiler.ast_evaluators import Evaluator
from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import ValueProjection, Projection


@dataclass
class EmptyType(Evaluator):
    kind: str = 'EmptyType'

    def aliases(self):
        return []

    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        return projections

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return ValueProjection()

    def evaluate_arango(self):
        return EvalResult('', {})

    def evaluate_cypher(self):
        return EvalResult('', {})