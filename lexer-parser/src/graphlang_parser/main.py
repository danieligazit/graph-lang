from graphlang_parser.lexing import build_lexer
from graphlang_parser.parsing import pg

if __name__ == '__main__':
    lexer = build_lexer()
    tokens = lexer.lex('print("something")')

    # for token in tokens:
    #     print(token)

    pg.parse(tokens)
