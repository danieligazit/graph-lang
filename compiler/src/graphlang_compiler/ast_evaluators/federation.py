from itertools import chain
from typing import Union, List, Iterable, Dict

from dataclasses import dataclass

from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import Projection, ArrayProjection
from graphlang_compiler.ast_evaluators import Evaluator, Variable
from graphlang_compiler.utility import some_util


@dataclass
class Federation(Evaluator):
    query: 'Query'
    source: str
    kind: str = 'Federation'

    def aliases(self):
        return self.query.aliases()

    def projections(self, projections):
        return self.query.projections(projections)

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return ArrayProjection(item=self.query.project(projections))

    def evaulate_sql(self):
        self.query.evaluate_sql()

    def evaluate_arango(self) -> EvalResult:
        return self.query.evaluate_arango()

    def evaluate_cypher(self) -> EvalResult:
        return self.query.evaluate_cypher()
