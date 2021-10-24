from graphlang import get, QueryBuilder
from rply import ParserGenerator

from graphlang_parser.lexing import build_lexer

pg = ParserGenerator(
    ['NAME', 'OPEN_PAREN', 'COMMA', 'STRING', 'CLOSE_PAREN', 'DOT']
)


@pg.production('expr : STRING')
def statement_expr(p):
    return p[0]


@pg.production('expr : NUMBER')
def statement_expr(p):
    return p[0]


@pg.production('list : expr COMMA expr')
def left_list(p):
    p[0].append(p[2])
    return p[0]


@pg.production('list : expr COMMA list')
def right_list(p):
    p[2].append(p[0])
    return p[2]


@pg.production('list : expr COMMA expr')
def right_list(p):
    print('yo')
    return p[0], p[2]


#
# @pg.production('main : func')
# def statement_expr(p):
#     return p[0]
#
#
#
# @pg.production('object : NAME OPEN_PAREN list CLOSE_PAREN')
# def statement_assignment(p):
#     func = p[0]
#     if func.value == 'get':
#         return get(p[2].value[1:-1])

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
expression = '"one", "two"'
print(list(build_lexer().lex(expression)))
result = parser.parse(build_lexer().lex(expression))
print(result)
# print(result.get_query())
