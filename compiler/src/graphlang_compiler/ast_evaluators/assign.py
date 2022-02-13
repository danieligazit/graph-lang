from itertools import chain
from typing import Union, List, Iterable, Dict

from dataclasses import dataclass

from graphlang.ast_expressions import Block
from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import Projection
from graphlang_compiler.ast_evaluators import Evaluator, Variable
from graphlang_compiler.utility import some_util


@dataclass
class Assign(Evaluator):
    left: List[Variable]
    right: Union[List[Evaluator], Evaluator]
    declare_all: bool = True
    kind: str = 'Assign'

    def project(self, projections: Dict[str, Projection]) -> Projection:
        raise ValueError

    def projections(self, projections: Dict[str, Projection]):
        if isinstance(self.right, Iterable):
            for i, left in enumerate(self.left):
                projections.update(self.right[i].projections(projections))
                projections[left.name] = self.right[i].project(projections)

            return projections

        if len(self.left) == 1:
            projections.update(self.right.projections(projections))
            projections[self.left[0].name] = self.right.project(projections)
            return projections

        for i, right in enumerate(self.right.projections(projections)):
            projections.update(self.right.projections(projections))
            projections[self.left[i].name] = right

        return projections

    def aliases(self):
        if isinstance(self.right, Iterable):
            return list(chain.from_iterable([item.aliases() for item in self.right]))

        return self.right.aliases()

    def evaluate_arango(self):
        if isinstance(self.right, list):
            binds_left, *left = some_util(
                (item.evaluate_arango() for item in self.left),
            )

            binds_right, *right = some_util(
                (item.evaluate_arango() for item in self.right),
            )

            rows = []
            for i, item in enumerate(left):
                rows.append(f'let {item} = {right[i]}')

            return EvalResult(
                expression='\n'.join(rows),
                binds=binds_left.update(binds_right) or binds_right
            )

        binds, *left, right = some_util(
            (item.evaluate_arango() for item in self.left),
            self.right.evaluate_arango()
        )

        return EvalResult(
            expression=f'''let {", ".join(left)} = {f'({right})' if isinstance(self.right, Block) else right}''',
            binds=binds
        )

    def evaluate_cypher(self) -> EvalResult:
        if isinstance(self.right, list):
            binds_left, *left = some_util(
                (item.evaluate_cypher() for item in self.left),
            )

            binds_right, *right = some_util(
                (item.evaluate_cypher() for item in self.right),
            )

            assert len(left) == len(right)

            rows = []
            for i, item in enumerate(left):
                rows.append(f'{right[i]} as {item}')

            return EvalResult(
                expression=f"with {'*,' if self.declare_all else ''} {', '.join(rows)}",
                binds=binds_left.update(binds_right) or binds_right
            )

        binds, *left, right = some_util(
            (item.evaluate_cypher() for item in self.left),
            self.right.evaluate_cypher()
        )

        return EvalResult(
            expression=f"with {'*, ' if self.declare_all else ''}{right} as {', '.join(left)}",
            binds=binds
        )
