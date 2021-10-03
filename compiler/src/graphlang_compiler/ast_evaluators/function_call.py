from dataclasses import dataclass
from itertools import chain
from typing import Dict, List

from graphlang_compiler.ast_evaluators.evaluator import Evaluator
from graphlang_compiler.consts import Functions, ARANGO_FUNCTIONS, CYPHER_FUNCTIONS
from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import Projection, ValueProjection
from graphlang_compiler.utility import some_util


@dataclass
class FunctionCall(Evaluator):
    function: str
    args: List[Evaluator]
    kind: str = 'FunctionCall'

    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        for arg in self.args:
            projections.update(arg.projections(projections))

        return projections

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return {
            Functions.LENGTH: ValueProjection,
            Functions.ALL: ValueProjection,
            Functions.ANY: ValueProjection
        }[self.function]()

    def aliases(self):
        return list(chain.from_iterable([arg.aliases() for arg in self.args]))

    def evaluate_arango(self):
        binds, *args = some_util(
            (arg.evaluate_arango() for arg in self.args)
        )

        if self.function in (Functions.ALL, Functions.ANY):
            return EvalResult(
                expression=f' {ARANGO_FUNCTIONS[self.function]} '.join(args),
                binds=binds
            )

        return EvalResult(
            expression=f'{ARANGO_FUNCTIONS[self.function]}({", ".join(args)})',
            binds=binds
        )

    def evaluate_cypher(self):
        binds, *args = some_util(
            (arg.evaluate_cypher() for arg in self.args)
        )

        if self.function in (Functions.ALL, Functions.ANY):
            return EvalResult(
                expression=f' {CYPHER_FUNCTIONS[self.function]} '.join(args),
                binds=binds
            )

        return EvalResult(
            expression=f'{CYPHER_FUNCTIONS[self.function]}({", ".join(args)})',
            binds=binds
        )
