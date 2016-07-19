# -*- coding: utf-8 -*-
"""
Created on Sat Jul 16 01:04:58 2016

@author: Oladapo

@email: oladapoadebowale@gmail.com

@mobile: +2348165149476
"""
from flask import Flask, jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
import datetime, os
import psutil

app = Flask(__name__)
### mysql://username:password@serverhost/databasename
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://sql8128062:xW9TErGiJF@sql8.freemysqlhosting.net/sql8128062"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_POOL_RECYCLE"] = 30

app.config['ALLOWED_EXTENSIONS'] = set(['csv'])

db = SQLAlchemy(app)

    

class Users(db.Model):
    
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    email  = db.Column(db.Unicode(50), nullable=False)
    account  = db.Column(db.Unicode(10), nullable=False)
    number  = db.Column(db.String(30), nullable=False)
    user_type  = db.Column(db.String(10), nullable=False, default='ADMIN')
    destinations = db.relationship('Destinations',backref="user",lazy="dynamic")
    calls = db.relationship('Calls',backref="user",lazy="dynamic")

    def __init__(self,firstname,lastname,email,account,number):

        self.first_name = firstname
        self.last_name = lastname
        self.email = email
        self.account = account
        self.number = number
    

class Destinations(db.Model):
    __tablename__ = 'destinations'
    import datetime
    id = db.Column(db.Integer, primary_key = True)
    did = db.Column(db.Text, nullable=False)
    gateway = db.Column(db.Text, nullable=False)
    channel = db.Column(db.Text, nullable=False)
    own = db.Column(db.Text, nullable=False)
    number = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_date = db.Column(db.DateTime, default=datetime.datetime.now())
    expire_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    record = db.Column(db.Integer, nullable=False)
    auth_did = db.Column(db.Integer, nullable=False)
    auth_gw  = db.Column(db.Integer, nullable=False)
    

class Calls(db.Model):
    __tablename__ = 'calls'
    import datetime
    id = db.Column(db.Integer, primary_key = True)
    channel = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_date = db.Column(db.DateTime, default=datetime.datetime.now())
    status = db.Column(db.Text, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    has_recording = db.Column(db.Integer, nullable=False)
    source = db.Column(db.Text, nullable=False)
    destination  = db.Column(db.Text, nullable=False) 


class Did(db.Model):

    __tablename__ = 'did'
    import datetime
    id = db.Column(db.Integer, primary_key = True)
    phone = db.Column(db.Unicode(30), nullable=False)
    created_by = db.Column(db.Unicode(30), db.ForeignKey('users.id'))
    created_date = db.Column(db.DateTime, default=datetime.datetime.now())
    provider = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Numeric(10,2), nullable=False)
    country = db.Column(db.String(30), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    def __init__(self,phone,user_id,provider,cost,country,capacity):

        self.phone = phone
        self.created_by = user_id
        self.provider = provider
        self.cost = cost
        self.country = country
        self.capacity = capacity


class System():
    
    def getUser(self,email):

        user = Users.query.filter_by(email=email).first()
        return user

    def disk_usage(self):
        
        
        """Return disk usage statistics about the given path.

        Will return the namedtuple with attributes: 'total', 'used' and 'free',
        which are the amount of total, used and free space, in bytes.
        """
        
        space = psutil.disk_usage('/')
        return space
    
    def account(self):
         
         
         import datetime
    
         six_digit = datetime.datetime.strftime(datetime.datetime.now(), '%H%M%S')
    
         five_digit = six_digit[1:]
    
        # now print the results!
         return five_digit

    def allowed_file(self,filename):

        return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

    def readCSV(self,fileUrl):
        import csv
        f = open(fileUrl, 'r')
        csvreader = csv.reader(f)
        data = list(csvreader)
        ### REMOVE THE HEADER
        data = data[1:]
        return data

    def insertDids(self,dataList):
        data_list_length = len(dataList)
        for data in dataList:

            #### INSERT INTO did table
            did = Did(data[0],"SYSTEM",data[3],data[2],data[1],data[4])
            db.session.add(did)

        db.session.commit()        
        return data_list_length

            


class User(Users):

    def __init__(self,email):

        self.email = email

    def find(self):

        exist = db.session.query(Users).filter_by(email=self.email).first()
        return exist

    def checkDid(self, phone):

        exist = db.session.query(exists().where(Did.phone == phone)).scalar()
        return exist

    def createDid(self,phone,provider,cost,country,capacity):


        if not self.checkDid(phone):


            ## INSERT DID INTO THE did table
            user = self.find()
            user_id = user.id
            did = Did(phone,user_id,provider,cost,country,capacity)
            db.session.add(did)
            db.session.commit()
            return 0

        return 1


    def verify(self, account):

        exist = db.session.query(Users).filter_by(email=self.email,account=account).first()

        return exist

    def login(self,account):

        if not self.verify(account):

            return 0
        return 1

    def register(self,firstname,lastname,email,account,number):

        if not self.find():

            ## INSERT INTO USER TABLE
            ##created_date = datetime.datetime.now()
            user = Users(firstname,lastname,email,account,number)
            db.session.add(user)
            db.session.commit()
            return 0
        return 1




