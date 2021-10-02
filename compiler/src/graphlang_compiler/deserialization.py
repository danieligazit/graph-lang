import json
from typing import AnyStr

from graphlang_compiler.ast_evaluators.ast_expressions import Query, Variable, Block, Filter, Assign, BinaryOp, Collection, AssignIter, \
    EmptyType, Traverse, MultiExpression, Ast, FunctionCall, Attribute, Literal, Collections

AST_TYPES = {
    'Query': Query,
    'Variable': Variable,
    'Block': Block,
    'FunctionCall': FunctionCall,
    'Filter': Filter,
    'Assign': Assign,
    'BinaryOp': BinaryOp,
    'Collection': Collection,
    'Collections': Collections,
    'AssignIter': AssignIter,
    'EmptyType': EmptyType,
    'Traverse': Traverse,
    'MultiExpression': MultiExpression,
    'Attribute': Attribute,
    'Literal': Literal
}


def query_object_hook(obj):
    if 'kind' not in obj:
        return obj

    return AST_TYPES[obj['kind']](**obj)


def deserialize_query(data: AnyStr) -> Ast:
    return json.loads(data, object_hook=query_object_hook)

