import json
from typing import AnyStr, Union

from graphlang_compiler.ast_evaluators import Query, Variable, Block, Filter, Assign, BinaryOp, Collection, AssignIter, \
    EmptyType, Traverse, MultiExpression, FunctionCall, Attribute, Literal, CollectionList, Evaluator
from graphlang_compiler.ast_evaluators.federation import Federation

AST_TYPES = {
    'Query': Query,
    'Variable': Variable,
    'Block': Block,
    'FunctionCall': FunctionCall,
    'Filter': Filter,
    'Assign': Assign,
    'BinaryOp': BinaryOp,
    'Collection': Collection,
    'CollectionList': CollectionList,
    'AssignIter': AssignIter,
    'EmptyType': EmptyType,
    'Traverse': Traverse,
    'MultiExpression': MultiExpression,
    'Attribute': Attribute,
    'Literal': Literal,
    'Federation': Federation
}


class Compiler:
    def __init__(
            self,
            ast_types
    ):
        self.ast_types = {
            'Query': Query,
            'Variable': Variable,
            'Block': Block,
            'FunctionCall': FunctionCall,
            'Filter': Filter,
            'Assign': Assign,
            'BinaryOp': BinaryOp,
            'Collection': Collection,
            'CollectionList': CollectionList,
            'AssignIter': AssignIter,
            'EmptyType': EmptyType,
            'Traverse': Traverse,
            'MultiExpression': MultiExpression,
            'Attribute': Attribute,
            'Literal': Literal,
            'Federation': Federation
        }
        self.ast_types.update(ast_types)

    def _query_object_hook(self, obj):
        if 'kind' not in obj:
            return obj

        return self.ast_types[obj['kind']](**obj)

    def _deserialize_query(self, data: AnyStr) -> Evaluator:
        return json.loads(data, object_hook=self._query_object_hook)

    def compile(self, query: Union[AnyStr, Evaluator]):
        if isinstance(query, str):
            query = self._deserialize_query(query)

        query.root.inline = False
        return query
