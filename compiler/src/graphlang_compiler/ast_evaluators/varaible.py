from typing import Union, Dict

from dataclasses import dataclass

from graphlang_compiler import EvalResult, Projection
from graphlang_compiler.ast_evaluators.evaluator import Evaluator


@dataclass
class Variable(Evaluator):
    name: str
    kind: str = 'Variable'

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return projections[self.name]

    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        return projections

    def aliases(self):
        return [self]

    def type(self):
        return self.value.type()

    def evaluate_arango(self):
        return EvalResult(
            expression=self.name
        )

    def evaluate_cypher(self):
        return EvalResult(
            expression=self.name
        )
