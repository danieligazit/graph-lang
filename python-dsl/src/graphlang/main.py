from graphlang import get

if __name__ == '__main__':

    person = get('Person').match(key='keanu_reeves')

    print(person)
