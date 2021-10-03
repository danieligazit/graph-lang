from dataclasses import dataclass, field
from itertools import chain
from typing import Dict, List

from graphlang_compiler.ast_evaluators import Evaluator, Filter
from graphlang_compiler.ast_evaluators.function_call import FunctionCall
from graphlang_compiler.consts import Functions
from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import Projection
from graphlang_compiler.utility import some_util


@dataclass
class MultiExpression(Evaluator):
    expressions: List[Evaluator] = field(default_factory=list)
    kind: str = 'MultiExpression'

    def project(self, projections: Dict[str, Projection]) -> Projection:
        raise ValueError

    def projections(self, projections):
        for expression in self.expressions:
            projections.update(expression.projections(projections))

        return projections

    def aliases(self):
        return list(set(chain.from_iterable([expression.aliases() for expression in self.expressions])))

    def evaluate_arango(self) -> EvalResult:
        binds, *expressions = some_util((e.evaluate_arango() for e in self.expressions))
        return EvalResult(
            expression='\n'.join(expressions),
            binds=binds
        )

    def evaluate_cypher(self) -> EvalResult:
        and_ops = []
        reduced_expressions = []
        for expression in self.expressions:
            if isinstance(expression, Filter):
                and_ops.append(expression.x)
                continue

            if and_ops:
                reduced_expressions.append(Filter(FunctionCall(Functions.ALL, and_ops)))
                and_ops = []

            reduced_expressions.append(expression)

        if and_ops:
            reduced_expressions.append(Filter(FunctionCall(Functions.ALL, and_ops)))

        binds, *expressions = some_util((e.evaluate_cypher() for e in reduced_expressions))
        return EvalResult(
            expression='\n'.join(expressions),
            binds=binds
        )

    def dump(self):
        return [item.dump() for item in self.expressions]
