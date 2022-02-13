from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict

from graphlang_compiler.ast_evaluators import MultiExpression, AssignIter
from graphlang_compiler.ast_evaluators.evaluator import Evaluator
from graphlang_compiler.ast_evaluators.traverse import Traverse
from graphlang_compiler.eval_result import EvalResult
from graphlang_compiler.projection import Projection
from graphlang_compiler.utility import some_util, unique_name


@dataclass
class Block(Evaluator):
    item: Evaluator
    returns: Evaluator
    do: MultiExpression = field(default_factory=lambda: MultiExpression())
    inline: bool = True
    kind: str = 'Block'

    def aliases(self):
        return self.item.aliases()

    def projections(self, projections):
        projections = self.item.projections(projections)
        projections.update(self.do.projections(projections))
        return projections

    def project(self, projections: Dict[str, Projection]) -> Projection:
        return self.returns.project(projections)

    def evaluate_arango(self):

        for expression in self.do.expressions:
            if isinstance(expression, Block):
                expression.inline = False

        binds, item, returns, *do = some_util(
            self.item.evaluate_arango(),
            self.returns.evaluate_arango() if self.returns else EvalResult(),
            (expression.evaluate_arango() for expression in self.do.expressions)
        )

        if isinstance(self.item, AssignIter) and isinstance(self.item.right, Traverse):
            vertex = self.item.left[0]

            v_col_expressions = []

            for v_col in self.item.right.vertex_collections:
                bind = unique_name()
                binds[bind] = v_col.name
                v_col_expressions.append(f"is_same_collection({vertex.name}, @{bind})")

            if v_col_expressions:
                do.insert(0, f'''filter {" or ".join(v_col_expressions)}''')

        expression = '\n'.join(
            [f'for {item}'] +
            [f'\t {row}' for row in do + ([f'return {returns}'] if returns else [])]
        )

        return EvalResult(
            expression=f'({expression})' if self.inline else expression,
            binds=binds
        )

    def evaluate_cypher(self):
        binds, item, returns, do = some_util(
            self.item.evaluate_cypher(),
            self.returns.evaluate_cypher() if self.returns else EvalResult(),
            self.do.evaluate_cypher()
        )

        expression = '\n'.join([
            item,
            do,
            f'| {returns}' if self.inline else f'return {returns}'
        ])

        return EvalResult(
            expression=f'[{expression}]' if self.inline else f'match {expression}',
            binds=binds
        )


class FederatedBlock(Block):
    def transform(self, context):
        joins = joins = defaultdict(list)

        for item in self.do.expressions:
            print(
                arg.key in ['name'],
                isinstance(self._query.pos.item, AssignIter),
                isinstance(self._query.pos.item.right, CollectionList),
                self._query.pos.item.right.collections[0].name == 'Person'
            )

            if isinstance(item, AssignIter) and isinstance(item.right, CollectionList) and \
                    self.collections[item.right.collections[0].name][arg.key].get('source'):
                joins[self.collections[item.right.collections[0].name][arg.key]['source']].append(arg)

            for source, joins in joins.items():
                self._query.pos.do.expressions.append(Filter(
                    x=BinaryOp(
                        op=Ops.IN,
                        left=Attribute(
                            ob=self._query.root.returns,
                            name='key'
                        ),
                        right=Federation(
                            query=get(item.right.collections[0].name).match(*joins).get_query(),
                            source=source
                        )
                    )
                ))

