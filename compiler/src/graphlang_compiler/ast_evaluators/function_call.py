from typing import Union, Dict, List

from dataclasses import dataclass

from graphlang_compiler import EvalResult, Projection, ValueProjection, ARANGO_FUNCTIONS, Functions, some_util, \
    CYPHER_FUNCTIONS
from graphlang_compiler.ast_evaluators.evaluator import Evaluator



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
        }[self.function]

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
