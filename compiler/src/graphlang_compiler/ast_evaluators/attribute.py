from dataclasses import dataclass
from typing import Dict

from graphlang_compiler.ast_evaluators import Evaluator
from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import Projection, ValueProjection
from graphlang_compiler.utility import unique_name


@dataclass
class Attribute(Evaluator):
    ob: Evaluator
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