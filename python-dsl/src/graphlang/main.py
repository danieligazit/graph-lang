import orjson

from graphlang import get
from graphlang_compiler import deserialize_query

if __name__ == '__main__':

    person = get('Person').match(name='keanu_reeves')

    print(person.get_query())
    blob = orjson.dumps(person.get_query())
    query = deserialize_query(blob)
    query.root.inline = False
