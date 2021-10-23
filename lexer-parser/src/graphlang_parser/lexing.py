from rply import LexerGenerator


def build_lexer():
    lexer = LexerGenerator()

    lexer.add('OPEN_PAREN', r'\(')
    lexer.add('CLOSE_PAREN', r'\)')
    lexer.add('NUMBER', r'\d+')
    lexer.add('NAME', r'[a-zA-Z_]+')
    lexer.add('STRING', r'\"(\\.|[^\"])*\"')
    lexer.add('DOT', r'\.')
    lexer.ignore(r'\s+')

    return lexer.build()