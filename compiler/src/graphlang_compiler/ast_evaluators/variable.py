from typing import Union, Dict, Optional

from dataclasses import dataclass

from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import Projection
from graphlang_compiler.ast_evaluators.evaluator import Evaluator
from graphlang_compiler.utility import unique_name


@dataclass
class Variable(Evaluator):
    name: Optional[str] = None
    kind: str = 'Variable'

    def __post_init__(self):
        self.name = self.name or unique_name()

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
