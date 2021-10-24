from graphlang import get, QueryBuilder
from rply import ParserGenerator
from graphlang_compiler.deseriazliation import deserialize
from graphlang_parser.lexing import build_lexer

pg = ParserGenerator(
    ['NAME', 'NUMBER', 'OPEN_PAREN', 'COMMA', 'STRING', 'CLOSE_PAREN', 'DOT'],
    precedence=[
        ('left', ['OPEN_PAREN', 'CLOSE_PAREN']),
        ('left', ['COMMA'])
    ]
)


@pg.production('main : object')
def statement_expr(p):
    return p[0]


@pg.production('expr : STRING')
def statement_expr(p):
    return p[0].value[1:-1]


@pg.production('expr : NUMBER')
def statement_expr(p):
    return p[0].value


@pg.production('expr : list')
def statement_expr(p):
    return p


@pg.production('list : expr COMMA expr')
def right_list(p):
    return [p[0], p[2]]


@pg.production('list : list COMMA expr')
def left_list(p):
    p[0].append(p[2])
    return p[0]


@pg.production('list : expr COMMA list')
def right_list(p):
    p[2].append(p[0])
    return p[2]


#
# @pg.production('main : func')
# def statement_expr(p):
#     return p[0]
#
#
#
@pg.production('object : NAME OPEN_PAREN expr CLOSE_PAREN')
def statement_assignment(p):
    func = p[0]

    params = p[2]
    if not isinstance(p[2], list):
        params = [params]

    if func.value == 'get':
        return get(*params)


#
# QUERY_FUNCTIONS = {
#     'match': QueryBuilder.match,
#     'traverse': QueryBuilder.traverse,
#     'into': QueryBuilder.into
# }
#
#
# @pg.production('func : object DOT NAME OPEN_PAREN STRING CLOSE_PAREN')
# def an(p):
#     query = p[0]
#     QUERY_FUNCTIONS.get(p[2].value)(query, *p[4].value)


# @pg.production('statement : object PERIOD NAME OPEN_PAREN STRING CLOSE_PAREN')
# def another_statement(p):
#     print(p)


# if p[0]


parser = pg.build()
expression = 'get("Person")'
print(list(build_lexer().lex(expression)))
result = parser.parse(build_lexer().lex(expression))


print(result)
# print(result.get_query())
