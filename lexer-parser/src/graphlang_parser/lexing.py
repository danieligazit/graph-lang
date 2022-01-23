from rply import LexerGenerator


def build_lexer():
    lexer = LexerGenerator()

    lexer.add('OPEN_PAREN', r'\(')
    lexer.add('CLOSE_PAREN', r'\)')
    lexer.add('NUMBER', r'\d+')
    lexer.add('NAME', r'[a-zA-Z_]+')
    lexer.add('COMMA', r'\,')
    lexer.add('STRING', r'\"(\\.|[^\"])*\"')
    lexer.add('DOT', r'\.')
    lexer.add('GT', r'>')
    lexer.add('LT', r'<')
    lexer.add('GTE', r'>=')
    lexer.add('LTE', r'<=')
    lexer.add('EQUALS', r'=')
    lexer.ignore(r'\n')
    lexer.ignore(r'\s+')

    return lexer.build()