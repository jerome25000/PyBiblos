import re
import io
import requests
import json
import firebase_admin
from firebase_admin import firestore, credentials


headers = {'Content-type': 'application/json'} 

def readFile(filename):
    with io.open(filename, 'r', encoding='utf-8') as f:
        txt = f.read().splitlines()

    books = []
    counter = 1
    year = ''
    for line in txt:
        print(line)
        if line.startswith('-'):
            year = line[1::]
        else:
            resp = re.search('^(.*?) (par|de) (.*?)$', line)
            names = re.compile(', | et ').split(resp.group(3))
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
                authorKey = lastname + "_" + firstname
                authors.append({'key': authorKey, 'firstname': firstname, 'lastname': lastname})

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


def fireBaseInit():
    cred = credentials.Certificate('key/biblos-1331d-0836bc81e8f1.json')
    app = firebase_admin.initialize_app(cred)
    return firestore.client()
    
def insertBookIntoFireBase(db, book):
    doc_ref = db.collection('foliosf').document()
    doc_ref.set(book)


db = fireBaseInit()
books = readFile('foliosf.txt')
for book in books:
    # postBook(book)
    print(book)
    insertBookIntoFireBase(db, book)
    




