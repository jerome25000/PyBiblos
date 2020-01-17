#!/bin/sh
# coding=utf-8
from flask import Flask
from flask_restplus import Api, Resource, fields, reqparse
import json
import argparse

from math import ceil
from dbManager import DbManager
from tableDataDao import TableDataDao

parser = argparse.ArgumentParser(description='Biblos')
parser.add_argument('dbName', type=str, help="database file name")
parser.add_argument('--test', action="store_true", default=False, help="test mode", dest="test")

managerDb = None
daoAuth = TableDataDao('AUTHOR')
daoBook = TableDataDao('BOOK')

app = Flask(__name__, static_folder="static", static_url_path="")
print("******************* config" + str(app.config))

api = Api(app, version='0.1', title='Biblos API', description='Biblos API')

authors_ns = api.namespace('authors', description='Authors operations')
books_ns = api.namespace('books', description='Books operations')

authorModel = api.model('Author', {
    'id': fields.Integer(readOnly=True, description='Auteur unique id'),
    'name': fields.String(required=True, description='Nom'),
    'firstname': fields.String(required=False, description='Prenom'),
    'yearOfBirth' : fields.String(required=False, description="Année de naissance"),
    'country' : fields.String(required=False, description="Nationalité"),
    #'books' : fields.List
})

bookModel = api.model('Book', {
    'id': fields.Integer(readOnly=True, description='Book unique id'),
    'title': fields.String(required=True, description='Titre'),
    'collected': fields.Boolean(default=False, description='Collection'),
    'year': fields.Integer(required=True, description="Année d'écriture"),
    'authors': fields.List(fields.Nested(authorModel), description="Liste des auteurs"),
    'number': fields.Integer(required=False, description="Numéro de série"),
    'editor' : fields.String(required=False, description="Editeur"),
    'collection' : fields.String(required=False, description="Nom de la collection de l'éditeur"),
    'serie' : fields.String(required=False, description="Nom de la série"),
    'numSerie' : fields.String(required=False, description="Numéro dans la série")
})

# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Cache-Control', 'no-store')
#     response.headers.add('Pragma', 'no-cache')
#     print('**********************\n')
#     print(str(response))
#     return response


def pagination(func):
    # print("pagination!")

    def wrapper(*args, **kwargs):
        response = func(*args)
        pageSize = 20
        pageNumber = 1
        parent = args[0]
        if hasattr(parent, 'args') and parent.pageNumber is not None and parent.pageSize is not None:
            pageSize = parent.pageSize
            pageNumber = parent.pageNumber
            pageTotal = ceil(parent.count / pageSize)
        page = {'data': response, 'pagination': {'pageNumber': pageNumber, 'pageSize': pageSize, 'pageTotal': pageTotal, 'totalRecords': parent.count}}                    
        return page
    return wrapper


def initDao():
    daoAuth.init(managerDb)
    daoBook.init(managerDb)

class Paginator(Resource):
    def __init__(self, api):
        Resource.__init__(self, api)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('pageSize', type=int, default=20, help='page size cannot be converted')
        self.parser.add_argument('pageNumber', type=int, default=1, help='page size cannot be converted')

    def getOffset(self):
        return self.offset

    def getPageSize(self):
        return self.pageSize

    def compute(self, count):
        self.args = self.parser.parse_args()
        self.count = count
        self.pageSize = self.args['pageSize']
        self.pageNumber = self.args['pageNumber']
        self.offset = self.pageSize * (self.pageNumber - 1)

        print('pageSize =%d' % self.pageSize)
        print('pageNumber =%d' % self.pageNumber)
        print('offset =%d' % self.offset)
        print('count =%d' % count)


@authors_ns.route('/')
class AuthorsList(Paginator):
    def __init__(self, api):
        Paginator.__init__(self, api)        

    ''' Gestion des auteurs! '''
    @authors_ns.doc('Liste des auteurs')
    # @authors_ns.marshal_list_with(authorModel) : remove because of pagination
    @pagination
    def get(self):
        print("get authors....")
        ''' Liste des auteurs '''        
        Paginator.compute(self, daoAuth.count())
        return daoAuth.getAll(Paginator.getPageSize(self), Paginator.getOffset(self))

    @authors_ns.doc('Creation auteur')
    @authors_ns.expect(authorModel)
    @authors_ns.marshal_with(authorModel, code=201)
    def post(self):        
        return daoAuth.create(api.payload), 201


@authors_ns.route('/<int:id>')
@authors_ns.response(404, 'Author not found')
@authors_ns.param('id', 'The author id')
class Author(Resource):
    '''Show a single author item and lets you delete them'''
    @authors_ns.doc('get_author')
    @authors_ns.marshal_with(authorModel)
    def get(self, id):
        '''Fetch a given resource'''
        author = daoAuth.get(id)
        if not author:
            api.abort(404, "Author {} doesn't exist".format(id))
        else:
            return author

    ''' Update a given author '''
    @authors_ns.doc('update_author')
    @authors_ns.marshal_with(authorModel)
    def put(self, id):
        return daoAuth.update(id, api.payload)

    ''' Delete a given author '''
    @authors_ns.doc('delete_author')
    def delete(self, id):
        daoAuth.delete(id)


@books_ns.route('/')
class BooksList(Paginator):
    def __init__(self, api):
        Paginator.__init__(self, api)        

    ''' Gestion des livres! '''
    @books_ns.doc('Book list')
    # @books_ns.marshal_list_with(bookModel) : remove because of pagination
    @pagination
    def get(self):
        print("get books....")
        ''' Liste des livres '''
        Paginator.compute(self, daoBook.count())
        return daoBook.getAll(Paginator.getPageSize(self), Paginator.getOffset(self))

    @books_ns.doc('Create book')
    @books_ns.expect(bookModel)
    @books_ns.marshal_with(bookModel, code=201)
    def post(self):
        print(api.payload)
        bookCreated = daoBook.create(api.payload)
        #create author if needed
        if bookCreated.get('authors') :
            for author in bookCreated['authors']:
                criteria = { "name" : author['name'], "firstname" : author['firstname'] }
                authorFound = daoAuth.getWithCriteria(criteria)
                bookToAppend = { "title" : bookCreated['title'], "id" : bookCreated['id'] }
                if authorFound :
                    authorToUpdate = authorFound.copy()               
                    print("Found existing author %s %s add book" %(authorToUpdate['name'], authorToUpdate['firstname']))
                    if not authorToUpdate.get('books'):
                        authorToUpdate['books'] = []
                    authorToUpdate['books'].append(bookToAppend)
                    daoAuth.update(authorToUpdate['id'], authorToUpdate)
                    print('author updated!')
                    author['id'] = authorFound['id']
                else :
                    newAuthor = { "books" : [] }
                    newAuthor['books'].append(bookToAppend)
                    newAuthor.update(criteria)
                    authorCreated = daoAuth.create(newAuthor)
                    author['id'] = authorCreated['id']
                    print('author created!')            
            daoBook.update(bookCreated['id'], bookCreated), 201
        return bookCreated, 201
        

@books_ns.route('/<int:id>')
@books_ns.response(404, 'Book not found')
@books_ns.param('id', 'The book id')
class Book(Resource):
    '''Show a single book item and lets you delete them'''
    @books_ns.doc('Get_book')
    @books_ns.marshal_with(bookModel)
    def get(self, id):
        '''Fetch a given resource'''
        book = daoBook.get(id)
        if not book:
            api.abort(404, "Book {} doesn't exist".format(id))
        else:
            return book

    ''' Update a given book '''
    @books_ns.doc('Update_book')
    @books_ns.marshal_with(bookModel)
    def put(self, id):
        return daoBook.update(id, api.payload)

    ''' Delete a given book '''
    @books_ns.doc('Delete_book')
    def delete(self, id):
        daoBook.delete(id)


if __name__ == '__main__':
    arg = parser.parse_args()
    if arg.test:
        print('test mode')
    else:
        print('no test')

    print("Running with dbName = %s" % (arg.dbName))

    managerDb = DbManager(arg.dbName)
    initDao()
    if arg.test:
        managerDb.createDb('test.sql')
    app.run(host= '127.0.0.1', debug=True, port=5000)
