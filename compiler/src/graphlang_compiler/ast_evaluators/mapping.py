from typing import Union, Dict, List

from dataclasses import dataclass


from graphlang_compiler.ast_evaluators.evaluator import Evaluator
from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import Projection, MappingProjection
from graphlang_compiler.utility import unique_name, some_util


@dataclass
class Mapping(Evaluator):
    mapping: Dict[str, Evaluator]
    kind: str = 'Mapping'

    def aliases(self):
        return list(chain.from_iterable([arg.aliases() for arg in self.mapping.values()]))

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return MappingProjection(mapping={
            key: value.project(projections)
            for key, value in self.mapping.items()
        })

    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        for value in self.mapping.values():
            projections.update(value.projections(projections))

        return projections

    def evaluate_arango(self) -> EvalResult:
        binds = {}
        expressions = []

        for key, value in self.mapping.items():
            mapping_bind, expression = some_util(value.evaluate_arango())
            bind = unique_name()
            mapping_bind[bind] = key
            expressions.append(f'@{bind}: {expression}')
            binds.update(mapping_bind)

        return EvalResult(
            expression=f'{{{",".join(expressions)}}}',
            binds=binds
        )

    def evaluate_cypher(self) -> EvalResult:
        binds = {}
        expressions = []

        for key, value in self.mapping.items():
            mapping_bind, expression = some_util(value.evaluate_cypher())
            expressions.append(f'{key}: {expression}')
            binds.update(mapping_bind)

        return EvalResult(
            expression=f'{{{",".join(expressions)}}}',
            binds=binds
        )
