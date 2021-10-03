from typing import Dict

from dataclasses import dataclass


from graphlang_compiler.ast_evaluators.evaluator import Evaluator
from graphlang_compiler.projection import Projection


@dataclass
class Collection(Evaluator):
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
