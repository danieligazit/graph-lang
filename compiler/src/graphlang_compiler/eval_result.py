from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class EvalResult:
    expression: str = field(default='')
    binds: Dict[str, Any] = field(default_factory=dict)
    # projection: Projection = field(default_factory=lambda: ValueProjection())

    @staticmethod
    def _format_value_arango(key: str, value: Any) -> str:
        if key.startswith('@'):
            return f'{value}'

        if isinstance(value, str):
            return f'"{value}"'
        return str(value)

    @staticmethod
    def _format_value_cypher(_key: str, value: Any) -> str:
        if isinstance(value, str):
            return f"'{value}'"
        return str(value)

    def format_arango(self):
        expression = self.expression
        for key, value in self.binds.items():
            expression = expression.replace(f'@{key}', self._format_value_arango(key, value))

        return expression

    def format_cypher(self):
        expression = self.expression
        for key, value in self.binds.items():
            expression = expression.replace(f'${key}', self._format_value_cypher(key, value))

        return expression
