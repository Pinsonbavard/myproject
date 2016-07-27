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
import iptc

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
    created_by  = db.Column(db.Unicode(10), nullable=False, default='SYSTEM')
    destinations = db.relationship('Destinations',backref="user",lazy="dynamic")
    calls = db.relationship('Calls',backref="user",lazy="dynamic")
    pin = db.relationship('Pin',backref="user",lazy="dynamic")
    did = db.relationship('Did',backref="user",lazy="dynamic")

    def __init__(self,firstname,lastname,email,account,number,user_id=None,user_type=None):

        self.first_name = firstname
        self.last_name = lastname
        self.email = email
        self.account = account
        self.number = number
        self.created_by = user_id
        self.user_type = user_type
    

class Destinations(db.Model):
    __tablename__ = 'destinations'
    import datetime
    id = db.Column(db.Integer, primary_key = True)
    did = db.Column(db.Text, nullable=False)
    gateway = db.Column(db.Text, nullable=False)
    channel = db.Column(db.Text, nullable=False)
    own = db.Column(db.Text, nullable=False)
    number = db.Column(db.Unicode(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.Column(db.Integer,nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now())
    expire_date = db.Column(db.DateTime, nullable=False)
    record = db.Column(db.Integer, nullable=False)
    auth_did = db.Column(db.Integer, nullable=False)
    auth_gw  = db.Column(db.Integer, nullable=False)

    def __init__(self,user_id,did,number,record,auth_did,auth_gw,gateway,channel,own,end_date,created_by):

        self.did = did
        self.created_by = created_by
        self.user_id = user_id
        self.number = number
        self.record = record
        self.auth_gw = auth_gw
        self.auth_did = auth_did
        self.gateway = gateway
        self.channel = channel
        self.own = own
        self.expire_date = end_date


class Ipfilters(db.Model):
    __tablename__ = 'ipfilters'
    import datetime
    id = db.Column(db.Integer, primary_key = True)
    ip = db.Column(db.Unicode(50), nullable=False)
    location = db.Column(db.String(20), nullable=True)
    target = db.Column(db.String(10), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self,ip,target):

        self.ip = ip
        self.target = target
        #self.location = location

    

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
    mode = db.Column(db.String(30), nullable=False)
    pin = db.Column(db.String(10), nullable=False)
    available = db.Column(db.String(10), nullable=False, default='YES')

    def __init__(self,phone,user_id,provider,cost,country,capacity,mode,pin):

        self.phone = phone
        self.created_by = user_id
        self.provider = provider
        self.cost = cost
        self.country = country
        self.capacity = capacity
        self.mode = mode
        self.pin = pin


class Pin(db.Model):

    __tablename__ = 'pin'
    import datetime
    id = db.Column(db.Integer, primary_key = True)
    pin = db.Column(db.Unicode(30), nullable=False)
    created_by = db.Column(db.Unicode(30), db.ForeignKey('users.id'))
    created_date = db.Column(db.DateTime, default=datetime.datetime.now())
    mode = db.Column(db.Unicode(20), nullable=False)

    def __init__(self,pin,user_id):

        self.pin = pin
        self.created_by = user_id


class Own(db.Model):

    __tablename__ = 'own'
    import datetime
    id = db.Column(db.Integer, primary_key = True)
    sim = db.Column(db.Unicode(30), nullable=False)
    did = db.Column(db.Unicode(30), nullable=False)
    created_by = db.Column(db.Unicode(30), db.ForeignKey('users.id'))
    created_date = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self,sim,did,user_id):

        self.sim = sim
        self.did = did
        self.created_by = user_id

class Country(db.Model):

    __tablename__ = 'countries'
    import datetime
    id = db.Column(db.Integer, primary_key = True)
    country = db.Column(db.Unicode(30), nullable=False)
    region = db.Column(db.Unicode(30), nullable=False)
    created_by = db.Column(db.Unicode(30), db.ForeignKey('users.id'))
    created_date = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self,region,country,user_id):

        self.region = region
        self.country = country
        self.created_by = user_id


class System():

    def dropAllInbound(self):

        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), 'INPUT')
        rule = iptc.Rule()
        rule.in_interface = 'eth+'
        rule.target = iptc.Target(rule, 'DROP')
        chain.insert_rule(rule)
        ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')
        iprecord = Ipfilters(ip,"DROP")
        db.session.add(iprecord)
        db.session.commit()

    def allowLoopback(self):
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), 'INPUT')
        rule = iptc.Rule()
        rule.in_interface = 'lo'
        rule.target = iptc.Target(rule, 'ACCEPT')
        chain.insert_rule(rule)
        ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')
        iprecord = Ipfilters(ip,"ACCEPT")
        db.session.add(iprecord)
        db.session.commit()

    def allowEstablishedInbound(self):
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), 'INPUT')
        rule = iptc.Rule()
        match = rule.create_match('state')
        match.state = 'RELATED,ESTABLISHED'
        rule.target = iptc.Target(rule, 'ACCEPT')
        chain.insert_rule(rule)
        ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')
        iprecord = Ipfilters(ip,"ACCEPT")
        db.session.add(iprecord)
        db.session.commit()

    def allowHTTP(self):
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), 'INPUT')
        rule = iptc.Rule()
        rule.in_interface = 'eth+'
        rule.protocol = 'tcp'
        match = rule.create_match('tcp')
        match.dport = '80'
        rule.target = iptc.Target(rule, 'ACCEPT')
        chain.insert_rule(rule)
        ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')
        iprecord = Ipfilters(ip,"ACCEPT")
        db.session.add(iprecord)
        db.session.commit()

    def allowHTTPS(self):
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), 'INPUT')
        rule = iptc.Rule()
        rule.in_interface = 'eth+'
        rule.protocol = 'tcp'
        match = rule.create_match('tcp')
        match.dport = '443'
        rule.target = iptc.Target(rule, 'ACCEPT')
        chain.insert_rule(rule)
        ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')
        iprecord = Ipfilters(ip,"ACCEPT")
        db.session.add(iprecord)
        db.session.commit()

    def allowSSH(self):

        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), 'INPUT')
        rule = iptc.Rule()
        rule.in_interface = 'eth+'
        rule.protocol = 'tcp'
        match = rule.create_match('tcp')
        match.dport = '22'
        rule.target = iptc.Target(rule, 'ACCEPT')
        chain.insert_rule(rule)
        ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')
        iprecord = Ipfilters(ip,"ACCEPT")
        db.session.add(iprecord)
        db.session.commit()

    def allowEstablishedOutbound(self):
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), 'OUTPUT')
        rule = iptc.Rule()
        match = rule.create_match('state')
        match.state = 'RELATED,ESTABLISHED'
        rule.target = iptc.Target(rule, 'ACCEPT')
        chain.insert_rule(rule)
        ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')
        iprecord = Ipfilters(ip,"ACCEPT")
        db.session.add(iprecord)
        db.session.commit()

    def dropAllOutbound(self):

        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), 'OUTPUT')
        rule = iptc.Rule()
        rule.in_interface = 'eth+'
        rule.target = iptc.Target(rule, 'DROP')
        chain.insert_rule(rule)
        ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')
        iprecord = Ipfilters(ip,"DROP")
        db.session.add(iprecord)
        db.session.commit()

    def defaultAction(self):

        self.dropAllOutbound()
        self.dropAllInbound()
        self.allowLoopback()
        self.allowEstablishedInbound()
        self.allowEstablishedOutbound()

    
    def getUser(self,email):

        user = Users.query.filter_by(email=email).first()
        return user


    def getUserById(self,id):

        user = Users.query.filter_by(id=id).first()
        return user

    def getDestinationByDid(self,did):

        destination = Destinations.query.filter_by(did=did).first()
        return destination

    def getUserByPhone(self,phone):

        user = Users.query.filter_by(number=phone).first()
        return user

    def dids(self):

        dids = Did.query.all()
        return dids

    def available_dids(self):

        dids = Did.query.filter_by(available='YES').all()
        return dids

    def this_did(self,did):

        did = Did.query.filter_by(phone=did).first()
        return did

    def owns(self):

        owns = Own.query.all()
        return owns

    def customers(self):

        customers = Users.query.filter_by(user_type='USER').all()
        return customers


    def pins(self):

        pins = Pin.query.all()
        return pins

    def countries(self):

        countries = Country.query.all()
        return countries

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


    def generatePin(self):
         
         
         import datetime
         pin_list = []
         for i in range(0,50):
            get_pin = int(datetime.datetime.strftime(datetime.datetime.now(), '%H%M%S'))
            get_pin = get_pin + i
            six_digit = str(get_pin)
            four_digit = six_digit[2:] 
            pin_list.append(four_digit)
    
         return pin_list
    
         
    
        # now print the results!
         return four_digit

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
            did = Did(data[0],"SYSTEM",data[3],data[2],data[1],data[4],data[5],data[6])
            db.session.add(did)
            db.session.commit()

        
        #db.session.close()        
        return data_list_length

    def insertOwns(self,dataList):
        data_list_length = len(dataList)
        for data in dataList:

            #### INSERT INTO did table
            own = Own(data[0],data[1],"SYSTEM")
            db.session.add(own)
            db.session.commit()

        
        #db.session.close()        
        return data_list_length

            


class User():

    def __init__(self,email):

        self.email = email

    def find(self):

        exist = db.session.query(Users).filter_by(email=self.email).first()
        db.session.close()
        return exist

    def findCountry(self,country):
        exist = db.session.query(exists().where(Country.country == country)).scalar()
        db.session.close()
        return exist

    def check_destination(self,user_id,destination_phone):

        exist = db.session.query(Destinations).filter_by(number=destination_phone,user_id=user_id).first()
        db.session.close()
        return exist


    def destination_new(self,user_id,did,number,record,auth_did,auth_gw,gateway,channel,own,end_date):

        if not self.check_destination(user_id,number):

            ### INSERT INTO Destinations table

            user = self.find()
            created_by = user.id

            destination = Destinations(user_id,did,number,record,auth_did,auth_gw,gateway,channel,own,end_date,created_by)
            
            try:

                this_did = System().this_did(did)
                this_did.available = 'NO'
                db.session.add(destination)
                db.session.commit()
                db.session.close()
                return 0
            except:
                return 506
        return 1




    def checkDid(self, phone):

        exist = db.session.query(exists().where(Did.phone == phone)).scalar()
        db.session.close()
        return exist

    def checkSim(self, sim):

        exist = db.session.query(exists().where(Own.sim == sim)).scalar()
        db.session.close()
        return exist

    def createCustomer(self,firstname,lastname,email,number,user_type='USER',account=None):

        if not System().getUserByPhone(number):

            ### INSERT INTO USER with customer
            user = self.find()
            user_id = user.id
            customer = Users(firstname,lastname,email,account,number,user_id,user_type)
            db.session.add(customer)
            db.session.commit()
            db.session.close()
            return 0

        return 1

        

    def createSim(self,sim,did):

        if not self.checkSim(sim):

            ### INSERT INTO THE own table
            user = self.find()
            user_id = user.id
            own = Own(sim,did,user_id)
            try:

                db.session.add(own)
                db.session.commit()
                db.session.close()
                return 0
            except:
                return 506
        return 1


    def createCountry(self,region,country):

        if not self.findCountry(country):

            ### INSERT INTO THE own table
            user = self.find()
            user_id = user.id
            country = Country(region,country,user_id)
            try:

                db.session.add(country)
                db.session.commit()
                db.session.close()
                return 0
            except:
                return 506
        return 1


    def createDid(self,phone,provider,cost,country,capacity,mode,pin):


        if not self.checkDid(phone):


            ## INSERT DID INTO THE did table
            user = self.find()
            user_id = user.id
            did = Did(phone,user_id,provider,cost,country,capacity,mode,pin)
            db.session.add(did)
            db.session.commit()
            db.session.close()
            return 0

        return 1


    def verify(self, account):

        exist = db.session.query(Users).filter_by(email=self.email,account=account).first()
        db.session.close()
        return exist

    def login(self,account):

        if not self.verify(account):

            return 0
        return 1

    def createPins(self):

        data_list = System().generatePin()

        user = self.find()
        user_id = user.id

        for data in data_list:

            #### INSERT INTO pin table
            pin = Pin(data,user_id)
            try:

                db.session.add(pin)
            except:

                return 505 ### Error 505 is Data not compiled, check connection error

        try:
            db.session.commit()
            db.session.close()
        except:
            return 506 ### Data insertion error

        return data_list



    def register(self,firstname,lastname,email,account,number):

        if not self.find():

            ## INSERT INTO USER TABLE
            ##created_date = datetime.datetime.now()
            user = Users(firstname,lastname,email,account,number)
            db.session.add(user)
            db.session.commit()
            db.session.close()
            return 0
        return 1




