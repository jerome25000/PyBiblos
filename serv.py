#!/bin/sh
# coding=utf-8
from flask import Flask
#from flask_restplus 
from flask_restx import Api, Resource, fields, reqparse
import json
import argparse
import yaml
import hashlib
import jwt

from math import ceil
from dbManager import DbManager
from tableDataDao import TableDataDao

def cypherPassword(password):
    m = hashlib.sha256()
    m.update(config['user']['passwordKey'].encode())
    m.update(password.encode())
    return m.hexdigest()

def tokenize(userRow):
    print(str(config['user']))
    if 'password' in userRow :
        del userRow['password']
    del userRow['id']
    return jwt.encode(userRow, config['user']['jwtKey'], algorithm="HS256")

def readConf(fileName) :
    with open(fileName) as f:
        return yaml.load(f, Loader=yaml.FullLoader)

config = None

managerDb = None
daoAuth = TableDataDao('AUTHOR')
daoBook = TableDataDao('BOOK')
daoUser = TableDataDao('USER')

app = Flask(__name__, static_folder="static", static_url_path="")
#print("******************* config" + str(app.config))

api = Api(app, version='0.1', title='Biblos API', description='Biblos API')

authors_ns = api.namespace('authors', description='Authors operations')
books_ns = api.namespace('books', description='Books operations')
users_ns = api.namespace('users', description='Users operations')
login_ns = api.namespace('login', description='Login operations')

loginModel = api.model('LoginModel', {
    'userName' : fields.String(required=True, description='user name'),
    'password' : fields.String(required=True, description='Password')
})

userModel = api.model('UserModel', {
    'id' : fields.Integer(readOnly=True, description='User unique id'), 
    'name' : fields.String(required=True, description='User name'),
    'password' : fields.String(required=True, description='Password'),
    'adminRight' : fields.Boolean(required=False, description='User admin'),
    'writeRight' : fields.Boolean(required=False, description='User admin')
})

bookMiniModel = api.model('BookMiniModel', {
    'id': fields.Integer(readOnly=True, description='Book unique id'),
    'title': fields.String(required=True, description='Titre'),
})

authorMiniModel = api.model('AuthorMiniModel', {
    'id': fields.Integer(readOnly=True, description='Auteur unique id'),
    'name': fields.String(required=True, description='Nom'),
    'firstname': fields.String(required=False, description='Prenom') 
})

authorModel = api.model('Author', {
    'id': fields.Integer(readOnly=True, description='Auteur unique id'),
    'name': fields.String(required=True, description='Nom'),
    'firstname': fields.String(required=False, description='Prenom'),
    'yearOfBirth' : fields.String(required=False, description="Année de naissance", skip_none=True),
    'country' : fields.String(required=False, description="Nationalité", skip_none=True),
    'books' : fields.List(fields.Nested(bookMiniModel), description="Liste des livres", skip_none=True)
})

bookModel = api.model('Book', {
    'id': fields.Integer(readOnly=True, description='Book unique id'),
    'title': fields.String(required=True, description='Titre'),
    'collected': fields.Boolean(default=False, description='Collection'),
    'year': fields.Integer(required=True, description="Année d'écriture"),
    'authors': fields.List(fields.Nested(authorMiniModel), description="Liste des auteurs"),
    'number': fields.Integer(required=False, description="Numéro de série"),
    'editor' : fields.String(required=False, description="Editeur"),
    'collection' : fields.String(required=False, description="Nom de la collection de l'éditeur"),
    'serie' : fields.String(required=False, description="Nom de la série"),
    'numSerie' : fields.String(required=False, description="Numéro dans la série")
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
    daoUser.init(managerDb)

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

@login_ns.route('/')
@login_ns.response(403, 'Forbidden')
class Login(Resource):
     @login_ns.doc('login')     
     def post(self):        
        userName = api.payload['userName']
        password = api.payload['password']
        passwordCyphered = cypherPassword(password)       
        criteria = { "name" : userName, "password" : passwordCyphered }
        user = daoUser.getWithCriteria(criteria)        
        if not user:
            api.abort(403, "Forbidden")        
        token = tokenize(user)
        return {'token' : token.decode('UTF-8')}        

@users_ns.route('/<int:id>')
@users_ns.response(404, 'User not found')
@users_ns.param('id', 'The user id')
class User(Resource):    
    @users_ns.doc('get_user')
    @users_ns.marshal_with(userModel, skip_none=True)
    def get(self, id):
        '''Fetch a given resource'''
        user = daoUser.get(id)
        if not user:
            api.abort(404, "User {} doesn't exist".format(id))
        else:
            return user

    ''' Update a given author '''
    @users_ns.doc('update_user')
    @users_ns.marshal_with(userModel)
    def put(self, id):
        if ('password' in api.payload):
            api.payload['password'] = cypherPassword(api.payload['password'])
        return daoUser.update(id, api.payload)
    
    ''' Delete a given author '''
    @users_ns.doc('delete_user')
    def delete(self, id):
        daoUser.delete(id)

@users_ns.route('/')
class UserList(Paginator):
    def __init__(self, api):
        Paginator.__init__(self, api)        

    @users_ns.doc('Users list')    
    @pagination
    def get(self):
        Paginator.compute(self, daoUser.count())
        return daoUser.getAll(Paginator.getPageSize(self), Paginator.getOffset(self))

    ''' Create a given user '''
    @users_ns.doc('create_user')
    @users_ns.marshal_with(userModel)
    def post(self):
        print("*** create user")
        if ('password' in api.payload):
            api.payload['password'] = cypherPassword(api.payload['password'])
        else :
            return 'Missing password', 400
        return daoUser.create(api.payload), 201        

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
    #@authors_ns.marshal_with(authorModel, code=201)
    def post(self):        
        return daoAuth.create(api.payload), 201


@authors_ns.route('/<int:id>')
@authors_ns.response(404, 'Author not found')
@authors_ns.param('id', 'The author id')
class Author(Resource):
    '''Show a single author item and lets you delete them'''
    @authors_ns.doc('get_author')    
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
        print("book created, id = %s" %(bookCreated['id']))
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
    @books_ns.marshal_with(bookModel, skip_none=True)
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

    parser = argparse.ArgumentParser(description='Biblos')    
    parser.add_argument('conf', type=str, help="conf yaml file")
    arg = parser.parse_args()    
    config = readConf(arg.conf)

    dbName = config['dbName']
    test = config['test']

    if test:
        print('test mode')
    else:
        print('prod mode')

    
    print("Running with dbName = %s" % (dbName))

    managerDb = DbManager(dbName)
    initDao()
    if test:
        managerDb.createDb(config['sql'])
    app.run(host= '127.0.0.1', debug=True, port=5000)
