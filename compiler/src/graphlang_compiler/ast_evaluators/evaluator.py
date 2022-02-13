from abc import ABC, abstractmethod
from typing import Dict

from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import Projection


class Evaluator(ABC):
    def transform(self, context):
        ...

    @abstractmethod
    def project(self, projections: Dict[str, Projection]) -> Projection:
        ...

    @abstractmethod
    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        ...

    @abstractmethod
    def aliases(self):
        ...

    @abstractmethod
    def evaluate_arango(self) -> EvalResult:
        ...

    @abstractmethod
    def evaluate_cypher(self) -> EvalResult:
        ...
