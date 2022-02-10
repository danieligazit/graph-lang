class Direction:
    OUTBOUND = 'OUTBOUND'
    INBOUND = 'INBOUND'


class Functions:
    LENGTH = 'length'
    ALL = 'all'
    ANY = 'any'


class Ops:
    GT = 'GT'
    EQ = 'eq'
    IN = 'in'


ARANGO_FUNCTIONS = {
    Functions.LENGTH: 'length',
    Functions.ANY: 'or',
    Functions.ALL: 'and'
}

CYPHER_FUNCTIONS = {
    Functions.LENGTH: 'size',
    Functions.ANY: 'OR',
    Functions.ALL: 'AND'
}

ARANGO_OPS = {
    Ops.EQ: '==',
    Ops.IN: 'in',
    Ops.GT: '>'
}

CYPHER_OPS = {
    Ops.EQ: '=',
    Ops.GT: '>'
}
