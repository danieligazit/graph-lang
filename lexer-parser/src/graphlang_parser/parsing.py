from dataclasses import dataclass
from typing import Any, List

from orjson import dumps

from graphlang import get, QueryBuilder, traverse, gt, Query
from rply import ParserGenerator
from graphlang_compiler import deserialize_query
from graphlang_parser.lexing import build_lexer

pg = ParserGenerator(
    ['NAME', 'NUMBER', 'OPEN_PAREN', 'COMMA', 'STRING', 'CLOSE_PAREN', 'DOT', 'EQUALS', 'GT', 'LT', 'GTE', 'LTE'],
    precedence=[
        ('left', ['COMMA']),
        ('left', ['DOT']),
        ('left', ['EQUALS']),
        ('left', ['OPERATOR']),
        ('left', ['FUNC']),
        ('left', ['OPEN_PAREN', 'CLOSE_PAREN']),
    ]
)


@dataclass
class KeyArg:
    key: str
    value: Any


@pg.production('main : object')
def statement_expr(p):
    return p[0]


@pg.production('object : func', precedence='FUNC')
def func_expr(p):
    return p[0]


@pg.production('expr : NAME EQUALS expr')
def key_arg(p):

    return KeyArg(p[0].value, p[2])


@pg.production('expr : NAME operator expr', precedence='EQUALS')
def key_arg(p):
    operator = p[1]
    return {
        '>': gt,
    }[operator.value](p[0].value, p[2])


@pg.production('expr : STRING')
def string_expr(p):
    return p[0].value[1:-1]


@pg.production('expr : object')
def object_expr(p):
    return p[0]


@pg.production('expr : NUMBER')
def number_expr(p):
    return float(p[0].value)


@pg.production('operator : GT')
@pg.production('operator : LT')
@pg.production('operator : GTE')
@pg.production('operator : LTE')
def operator_expr(p):
    return p[0]


@pg.production('expr : expr operator expr', precedence='OPERATOR')
def bin_op(p):
    operator = p[1]

    if operator.name == 'GT':
        return p[0] > p[2]


@pg.production('expr : list')
def list_expr(p):
    return p[0]


@pg.production('list : expr COMMA expr')
def start_list(p):
    left, right = p[0], p[2]

    if isinstance(left, list):
        if isinstance(right, list):
            return left + right

        left.append(right)
        return left

    elif isinstance(right, list):
        return [left] + right

    return [left, right]


def function_call(func_name: str, params: List[Any]):
    # TODO: catch KeyError
    return {
        'get': get,
        'traverse': traverse
    }[func_name](*params)


@pg.production('object : NAME OPEN_PAREN CLOSE_PAREN')
def function_with_no_params(p):
    func = p[0]
    return function_call(func.value, [])


QUERY_FUNCTIONS = {
    'match': QueryBuilder.match,
    'traverse': QueryBuilder.traverse,
    'into': QueryBuilder.into,
    'count': QueryBuilder.count,
    'as_var': QueryBuilder.as_var
}


@pg.production('object : NAME OPEN_PAREN expr CLOSE_PAREN')
def function(p):
    func = p[0]

    params = p[2]
    if not isinstance(params, list):
        params = [params]

    return function_call(func.value, params)


@pg.production('func : object DOT NAME OPEN_PAREN expr CLOSE_PAREN')
def method_call(p):
    query = p[0]

    params = p[4]
    if not isinstance(params, list):
        params = [params]

    kwargs = {}
    args = []

    for param in params:
        if isinstance(param, KeyArg):
            kwargs[param.key] = param.value
            continue

        args.append(param)

    return QUERY_FUNCTIONS.get(p[2].value)(query, *args, **kwargs)


@pg.production('func : object DOT NAME OPEN_PAREN CLOSE_PAREN', precedence='FUNC')
def empty_method_call(p):
    # TODO: catch TypeError: 'NoneType' object is not callable
    query = p[0]
    return QUERY_FUNCTIONS.get(p[2].value)(query)


def parse(query: str) -> Query:
    parser = pg.build()
    result = parser.parse(build_lexer().lex(query))
    blob = dumps(result.get_query())
    query = deserialize_query(blob)
    query.root.inline = False
    return query


if __name__ == '__main__':
    query = f'''
        get("Person").match(
            traverse("ActedIn").count() > 0, 
            key="person", 
            some > 2,
            other="value"
        ).traverse("Directed").into("Movie")
    '''

    result = parse(query)

    print(f'ARANGO:\n{result.arango()}\n')
    print(f'NEO4J:\n{result.cypher()}\n')
