from typing import Dict, List

from dataclasses import dataclass

from graphlang_compiler.ast_evaluators import Evaluator
from graphlang_compiler.ast_evaluators.collection import Collection
from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import Projection, DocumentProjection
from graphlang_compiler.utility import some_util


@dataclass
class CollectionList(Evaluator):
    collections: List[Collection]
    kind: str = 'CollectionList'

    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        return projections

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return DocumentProjection()

    def aliases(self):
        return []

    def evaluate_arango(self):
        iterators = []

        binds, *collections = some_util(
            [collection.evaluate_arango() for collection in self.collections]
        )

        if len(collections) == 1:
            return EvalResult(
                expression=f'{collections[0]}',
                binds=binds
            )

        for collection in collections:
            iterators.append(collection)

        return EvalResult(
            expression=f'''FLATTEN([[{'], ['.join(iterators)}]])''',
            binds=binds
        )

    def evaluate_cypher(self):
        binds, *collections = some_util(
            [collection.evaluate_cypher() for collection in self.collections]
        )

        collections = '|'.join(collections)

        return EvalResult(
            expression=f'{collections}',
            binds=binds
        )
