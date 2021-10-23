from typing import Union, Dict, List

from dataclasses import dataclass

from graphlang_compiler.ast_evaluators import Block
from graphlang_compiler.ast_evaluators.evaluator import Evaluator
from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import ArrayProjection, Projection


@dataclass
class Query(Evaluator):
    root: Block
    pos: Block
    kind: str = 'Query'

    def aliases(self):
        return self.root.aliases()

    def projections(self, projections):
        return self.root.projections(projections)

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return ArrayProjection(item=self.pos.project(projections))

    def evaluate_arango(self) -> EvalResult:
        return self.root.evaluate_arango()

    def evaluate_cypher(self) -> EvalResult:
        return self.root.evaluate_cypher()

    def arango(self):
        return self.evaluate_arango().format_arango()

    def cypher(self):
        return self.evaluate_cypher().format_cypher()