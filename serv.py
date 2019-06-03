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

app = Flask(__name__)
api = Api(app, version='0.1', title='Biblos API', description='Biblos API')

authors_ns = api.namespace('authors', description='Authors operations')
books_ns = api.namespace('books', description='Books operations')

authorModel = api.model('Author', {
    'id': fields.Integer(readOnly=True, description='Auteur unique id'),
    'name': fields.String(required=True, description='Nom'),
    'firstname': fields.String(required=False, description='Prenom')
})

bookModel = api.model('Book', {
    'id': fields.Integer(readOnly=True, description='Book unique id'),
    'title': fields.String(required=True, description='Titre'),
    'collected': fields.Boolean(default=False, description='Collection'),
    'year': fields.Integer(required=True, description="Année d'écriture"),
    'authors': fields.List(fields.Nested(authorModel), description="Liste des auteurs"),
    'number': fields.Integer(required=False, description="Numéro de série")
})


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


@authors_ns.route('/')
class AuthorsList(Paginator):
    def __init__(self, api):
        Paginator.__init__(self, api)        

    ''' Gestion des auteurs! '''
    @authors_ns.doc('Liste des auteurs')
    # @authors_ns.marshal_list_with(authorModel) : remove because of pagination
    @pagination
    def get(self):
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
    @authors_ns.doc('get_author')
    @authors_ns.marshal_with(authorModel)
    def put(self, id):
        return daoAuth.update(id, api.payload)

    @authors_ns.doc('get_author')
    def delete(self, id):
        daoAuth.delete(id)


@books_ns.route('/')
class BooksList(Paginator):
    def __init__(self, api):
        Paginator.__init__(self, api)        

    ''' Gestion des livres! '''
    @books_ns.doc('Liste des livres')
    # @books_ns.marshal_list_with(bookModel) : remove because of pagination
    @pagination
    def get(self):
        ''' Liste des livres '''
        Paginator.compute(self, daoAuth.count())
        return daoBook.getAll(Paginator.getPageSize(self), Paginator.getOffset(self))

    @books_ns.doc('Creation livre')
    @books_ns.expect(bookModel)
    @books_ns.marshal_with(bookModel, code=201)
    def post(self):
        print(api.payload)
        return daoBook.create(api.payload), 201


@books_ns.route('/<int:id>')
@books_ns.response(404, 'Book not found')
@books_ns.param('id', 'The book id')
class Book(Resource):
    '''Show a single book item and lets you delete them'''
    @authors_ns.doc('get_book')
    @authors_ns.marshal_with(bookModel)
    def get(self, id):
        '''Fetch a given resource'''
        book = daoBook.get(id)
        if not book:
            api.abort(404, "Book {} doesn't exist".format(id))
        else:
            return book


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
    app.run(debug=True)
