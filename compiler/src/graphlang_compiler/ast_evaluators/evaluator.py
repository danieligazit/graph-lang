from abc import ABC, abstractmethod
from typing import Dict

from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import Projection


class Evaluator(ABC):
    @abstractmethod
    def project(self, projections: Dict[str, Projection]) -> Projection:
        pass

    @abstractmethod
    def projections(self, projections: Dict[str, Projection]) -> Dict[str, Projection]:
        pass

    @abstractmethod
    def aliases(self):
        pass

    @abstractmethod
    def evaluate_arango(self) -> EvalResult:
        pass

    @abstractmethod
    def evaluate_cypher(self) -> EvalResult:
        pass
