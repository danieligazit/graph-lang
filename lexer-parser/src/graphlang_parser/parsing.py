from dataclasses import dataclass
from typing import Any, List

from graphlang_compiler.ast_evaluators import traverse
from orjson import dumps

from graphlang import get, QueryBuilder
from rply import ParserGenerator
from graphlang_compiler import deserialize_query
from graphlang_parser.lexing import build_lexer

pg = ParserGenerator(
    ['NAME', 'NUMBER', 'OPEN_PAREN', 'COMMA', 'STRING', 'CLOSE_PAREN', 'DOT', 'EQUALS', 'GT', 'LT', 'GTE', 'LTE'],
    precedence=[
        ('left', ['OPEN_PAREN', 'CLOSE_PAREN']),
        ('left', ['COMMA']),
        ('left', ['EQUALS'])
    ]
)


@dataclass
class KeyArg:
    key: str
    value: Any


@pg.production('main : object')
def statement_expr(p):
    return p[0]


@pg.production('operator : GT')
def string_expr(p):
    return p[0]


@pg.production('operator : LT')
def string_expr(p):
    return p[0]


@pg.production('operator : GTE')
def string_expr(p):
    return p[0]


@pg.production('operator : LTE')
def string_expr(p):
    return p[0]


@pg.production('object : func')
def func_expr(p):
    return p[0]


@pg.production('expr : NAME EQUALS expr')
def keyarg(p):
    return KeyArg(p[0].value, p[2])


@pg.production('expr : STRING')
def string_expr(p):
    return p[0].value[1:-1]


@pg.production('expr : object')
def object_expr(p):
    return p[0]


@pg.production('expr : NUMBER')
def number_expr(p):
    return p[0].value


@pg.production('expr : list')
def list_expr(p):
    return p[0]


@pg.production('list : expr COMMA expr')
def start_list(p):
    return [p[0], p[2]]


@pg.production('list : list COMMA expr')
def left_list(p):
    p[0].append(p[2])
    return p[0]


@pg.production('list : expr COMMA list')
def right_list(p):
    p[2].append(p[0])
    return p[2]


@pg.production('list : expr operator expr')
def bin_op(p):
    operator = p[1]

    if operator.name == 'GT':
        return p[0] > p[2]


def function_call(func_name: str, params: List[Any]):
    # TODO: catch KeyError
    return {
        'get': get,
        'traverse': traverse
    }[func_name](*params)


@pg.production('object : NAME OPEN_PAREN expr CLOSE_PAREN')
def function(p):
    func = p[0]

    params = p[2]
    if not isinstance(params, list):
        params = [params]

    return function_call(func.value, params)


@pg.production('object : NAME OPEN_PAREN CLOSE_PAREN')
def function_with_no_params(p):
    func = p[0]
    return function_call(func.value, [])


QUERY_FUNCTIONS = {
    'match': QueryBuilder.match,
    'traverse': QueryBuilder.traverse,
    'into': QueryBuilder.into,
    'count': QueryBuilder.count
}


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


@pg.production('func : object DOT NAME OPEN_PAREN CLOSE_PAREN')
def empty_method_call(p):
    # TODO: catch TypeError: 'NoneType' object is not callable
    query = p[0]
    return QUERY_FUNCTIONS.get(p[2].value)(query)


# @pg.production('statement : object PERIOD NAME OPEN_PAREN STRING CLOSE_PAREN')
# def another_statement(p):
#     print(p)


# if p[0]


parser = pg.build()
expression = 'get("Person").match(get("A").count() > 2, key="person", other="value")'

print(list(build_lexer().lex(expression)))
result = parser.parse(build_lexer().lex(expression))

blob = dumps(result.get_query())
query = deserialize_query(blob)
query.root.inline = False
print(query.arango())
