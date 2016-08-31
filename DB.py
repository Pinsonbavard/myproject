# -*- coding: utf-8 -*-
"""
Created on Sat Jul 16 01:04:58 2016

@author: Oladapo

@email: oladapoadebowale@gmail.com

@mobile: +2348165149476
"""
from flask import Flask, jsonify,make_response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from sqlalchemy.orm import sessionmaker
import datetime, os
import psutil
from sqlalchemy import create_engine
#import iptc

app = Flask(__name__)
### mysql://username:password@serverhost/databasename
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://sql8128062:xW9TErGiJF@sql8.freemysqlhosting.net/sql8128062"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 100
app.config["SQLALCHEMY_POOL_RECYCLE"] = 280

app.config['ALLOWED_EXTENSIONS'] = set(['csv'])

db = SQLAlchemy(app)

#some_engine = create_engine("mysql://sql8128062:xW9TErGiJF@sql8.freemysqlhosting.net/sql8128062", pool_recycle=280)


# create a configured "Session" class
#Session = sessionmaker(bind=some_engine)

# create a Session
#session = Session()

    

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
    number = db.Column(db.Unicode(50), nullable=True)
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
    target = db.Column(db.String(10), nullable=False)
    mode_type = db.Column(db.String(30), nullable=True)
    interface = db.Column(db.String(10), nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self,ip,target, mode_type, interface):

        self.ip = ip
        self.target = target
        self.mode_type = mode_type
        self.interface = interface

    

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
    created_by = db.Column(db.Integer, nullable=False)


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
    pin = db.Column(db.String(10), nullable=True)
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



   
    def ipfilters(self):

        ipfilterslist = db.session.query(Ipfilters).all()
        return ipfilterslist

    def calls(self):

        calls = db.session.query(Calls).all()
        return calls

    
    def getUser(self,email):
        
        try:
            user = db.session.query(Users).filter_by(email=email).first()
            return user
        except:
            db.session.rollback()
        
        


    def getUserById(self,id):

        user = db.session.query(Users).filter_by(id=id).first()
        return user

    def getDestinationByDid(self,did):

        destination = Destinations.query.filter_by(did=did).first()
        return destination

    def getUserByPhone(self,phone):

        user = Users.query.filter_by(number=phone).first()
        return user

    def dids(self):

        #db.session.commit()
        dids = db.session.query(Did).all()
        #
        return dids

    def available_dids(self):

        dids = Did.query.filter_by(available='YES').all()
        return dids

    def count_available_dids(self):

        dids = Did.query.filter_by(available='YES').count()
        return dids

    def total_dids(self,did):
        total = db.session.query(Destinations).filter_by(did=did).count()
        total = total + 1
        return total


    def didsCount(self,did):
        total = db.session.query(Destinations).filter_by(did=did).count()
        return total


    def this_did(self,did):

        did = Did.query.filter_by(phone=did).first()
        return did

    def owns(self):

        owns = db.session.query(Own).all()
        return owns

    def customers(self):

        customers = Users.query.filter_by(user_type='USER').all()
        return customers


    def pins(self):

        pins = Pin.query.all()
        return pins

    def available_pins(self):

        pins = Pin.query.filter_by(mode='AVAILABLE').all()
        return pins

    def countries(self):

        countries = db.session.query(Country).all()

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
        i = 0
        for data in dataList:
            
            ##### check if did already exist, and ignore did
            exist = db.session.query(exists().where(Did.phone == data[0])).scalar()
            if not exist:
                #### INSERT INTO did table

                did = Did(data[0],"SYSTEM",data[3],data[2],data[1],data[4],data[5],data[6])
                db.session.add(did)
                db.session.commit()
                i += 1
      
        return {"insertnum":i, "total":data_list_length}

    def deleteCountry(self,country_id):
        country = db.session.query(Country).get(country_id)
        
        try:
            db.session.delete(country)
            db.session.commit()
            return 0
        except:
            db.session.rollback()
            return 1


    def deleteDestination(self,did,destination_id):

        destination = db.session.query(Destinations).get(destination_id)
        this_did = System().this_did(did)
        try:
            db.session.delete(destination)
            this_did.available = 'YES'
            db.session.commit()
            return 0
        except:
            db.session.rollback()
            return 1

    def deletePin(self,pin_id):
        pin = Pin.query.get(pin_id)
        
        try:
            db.session.delete(pin)
            db.session.commit()
            return 0
        except:
            db.session.rollback()
            return 1


    def deleteDid(self,did_id,act_did):
        did = db.session.query(Did).get(did_id)
        didsCount = System().didsCount(act_did)

        
        try:
            if didsCount <= 0:

                db.session.delete(did)
                db.session.commit()
                return 0
            return 2
        except:
            db.session.rollback()
            return 1


    def deleteOwn(self,own_id):
        own = Own.query.get(own_id)
        
        try:
            db.session.delete(own)
            db.session.commit()
            return 0
        except:
            db.session.rollback()
            return 1

    def deleteUser(self,user_id):
        user = Users.query.get(user_id)
        
        try:
            db.session.delete(user)
            db.session.commit()
            return 0
        except:
            db.session.rollback()
            return 1


    def deleteIp(self,ip_id):
        ip = Ipfilters.query.get(ip_id)
        
        try:
            db.session.delete(ip)
            db.session.commit()
            return 0
        except:
            db.session.rollback()
            return 1

    def insertOwns(self,dataList):
        data_list_length = len(dataList)
        i = 0
        for data in dataList:
             ##### check if own already exist, and ignore did
            exist = db.session.query(exists().where(Own.sim == data[0])).scalar()
            if not exist:

                #### INSERT INTO did table
                own = Own(data[0],data[1],"SYSTEM")
                db.session.add(own)
                db.session.commit()
                i += 1
       
        return {"insertnum":i, "total":data_list_length}

            


class User():

    def __init__(self,email):

        self.email = email

    def find(self):
        #db.session.commit()
        exist = db.session.query(Users).filter_by(email=self.email).first()
        
        return exist

    def findCountry(self,country):
        db.session.commit()
        exist = db.session.query(exists().where(Country.country == country)).scalar()
        #
        return exist

    def check_destination(self,user_id,destination_phone):

        exist = db.session.query(Destinations).filter_by(number=destination_phone,user_id=user_id).first()
        
        #
        return exist


    def destination_new(self,user_id,did,number,record,auth_did,auth_gw,gateway,channel,own,end_date):

        if not self.check_destination(user_id,number):

            ### INSERT INTO Destinations table

            user = self.find()
            created_by = user.id

            total_dids = System().total_dids(did) ####### Get the total number of time this did has been used
            this_did = System().this_did(did)

            try:
                
                if total_dids == this_did.capacity:
                    this_did.available = 'NO'
                destination = Destinations(user_id,did,number,record,auth_did,auth_gw,gateway,channel,own,end_date,created_by)
                db.session.add(destination)
                db.session.commit()
                
                return 0
            except:
                return 506
        return 1




    def checkDid(self, phone):

        db.session.commit()
        exist = db.session.query(exists().where(Did.phone == phone)).scalar()
        return exist

    def checkSim(self, sim):
        db.session.commit()
        exist = db.session.query(exists().where(Own.sim == sim)).scalar()
        
        return exist

    def createCustomer(self,firstname,lastname,email,number,user_type='USER',account=None):

        if not System().getUserByPhone(number):

            ### INSERT INTO USER with customer
            user = self.find()
            user_id = user.id
            customer = Users(firstname,lastname,email,account,number,user_id,user_type)
            db.session.add(customer)
            db.session.commit()
            
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
            try:

                db.session.add(did)
                # update pin in the pin table to say "NOT-AVAILABLE"
                if mode == 'PIN-DIALING':
                    used_pin = Pin.query.filter_by(pin=pin).first()
                    used_pin.mode = 'NOT-AVAILABLE'
                db.session.commit()
                return 0
            except:
                return 506

        return 1


    def verify(self, account):

        try:

            exist = db.session.query(Users).filter_by(email=self.email,account=account).first()
            return exist
        except:
            db.session.rollback()
            return 2
        
        

    def login(self,account):

        response = self.verify(account)
        if response == 2:
            return 2
        elif response and response != 2:
            return 1
        else:
            return 0

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
            
            return 0
        return 1




