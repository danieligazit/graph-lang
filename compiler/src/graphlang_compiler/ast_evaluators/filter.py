from dataclasses import dataclass
from typing import Dict

from graphlang_compiler.ast_evaluators.evaluator import Evaluator
from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import Projection


@dataclass
class Filter(Evaluator):
    x: Evaluator
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
