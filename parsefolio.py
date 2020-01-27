import re
import io
import requests
import json

headers = {'Content-type': 'application/json'} 

def readFile(filename):
    with io.open(filename, 'r', encoding='utf-8') as f:
        txt = f.read().splitlines()

    books = []
    counter = 1
    year = ''
    for line in txt:
        if line.startswith('-'):
            year = line[1::]
        else:
            resp = re.search('^(.*?) par (.*?)$', line)
            names = re.compile(', | et ').split(resp.group(2))
            # print(names)
            authors = []
            firstname = ''
            lastname = ''
            for name in names:
                namesArr = name.split(' ')
                if len(namesArr) > 1:
                    firstname = ' '.join(namesArr[0:-1])
                    lastname = namesArr[-1]
                else:
                    firstname = namesArr[0]
                    lastname = ''
                authors.append({'firstname': firstname, 'name': lastname})

            book = {'title': resp.group(1), 'year': year, 'number': counter, 'authors': authors}
            counter = counter + 1
            books.append(book)
    return books


def postAuthors(author) :
    authorCreated = requests.post('http://127.0.0.1:5000/authors/', headers=headers, data=json.dumps(author))    
    return json.loads(authorCreated.content)['id']


def postBook(book):    
    bookCreated = requests.post('http://127.0.0.1:5000/books/', headers=headers, data=json.dumps(book))    
    #print(r)


books = readFile('foliosf.txt')
for book in books:
    postBook(book)
