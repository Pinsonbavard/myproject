# -*- coding: utf-8 -*-
"""
Created on Sat Jul 16 01:04:58 2016

@author: Oladapo

@email: oladapoadebowale@gmail.com

@mobile: +2348165149476
"""

from DB import Users, db, Destinations, Calls, System, User, Did
from flask import Flask, flash, redirect, url_for, jsonify, request,render_template, make_response, session, abort
from flask.ext.restless import APIManager
from flask.ext.mail import Mail,Message
from sqlalchemy import create_engine
from flask.ext.cors import CORS
from sqlalchemy.sql import exists
import json, datetime
from threading import Thread
from sqlalchemy.orm import relationship, backref
from time import strftime, gmtime, localtime
import os
#from path import path
from werkzeug import secure_filename
import iptc
from geoip import geolite2


    

#e = create_engine("mysql://sql8128062:xW9TErGiJF@sql8.freemysqlhosting.net/sql8128062", pool_recycle=280)

#e = create_engine("mysql://firsvat:Firsvat@2016@98.102.204.204:3306/firsvat", pool_recycle=3600)

app = Flask(__name__)
app.secret_key = "moyinoluwa1999"

def ensure_dir(d):

    if not os.path.exists(d):

        os.makedirs(d)

app.config['SQLALCHEMY_POOL_SIZE'] = 100
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config["MAIL_SERVER"] = "smtp.pepipost.com"
app.config["MAIL_PORT"] = 25
#app.config["MAIL_USE_TLS"] = True
#app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "guest"
app.config["MAIL_PASSWORD"] = "FunmiFatimo"
app.config["DEFAULT_MAIL_SUBJECT"] = "SinLimites"
app.config["DEFAULT_MAIL_SENDER"] = "SinLimites<no-reply@sci.ng>"
##app.config['UPLOAD_FOLDER'] = 'http://crestovista.com/guest-admin/www/img/'
CORS(app)

mail = Mail(app)

manager = APIManager(app,flask_sqlalchemy_db=db)


manager.create_api(Users, methods=["GET","POST","DELETE"])

manager.create_api(Calls)

manager.create_api(Destinations)

@app.template_filter('User')
def _jinja2_filter_user(id):

    system = System()
    user = system.getUserById(id)
    if user is None:
        return "SYSTEM"
    return user.first_name + ' '+ user.last_name


@app.template_filter('IpCountry')
def _jinja2_filter_user(ip):

    match = geolite2.lookup(ip)
    if match is None:
        return "Not found"
    return match.country

@app.template_filter('IpContinent')
def _jinja2_filter_user(ip):

    match = geolite2.lookup(ip)
    if match is None:
        return "Not found"
    return match.continent

@app.template_filter('Iptimezone')
def _jinja2_filter_user(ip):

    match = geolite2.lookup(ip)
    if match is None:
        return "Not found"
    return match.timezone


@app.template_filter('Ipsubdivisions')
def _jinja2_filter_user(ip):

    match = geolite2.lookup(ip)
    if match is None:
        return "Not found"
    return match.subdivisions


@app.template_filter('DestinationUserId')
def _jinja2_filter_destination(did):

    system = System()
    destination = system.getDestinationByDid(did)
    if destination is None:
        return "Nobody"
    return destination.user_id

@app.template_filter('humandatetime')
def _jinja2_filter_humandatetime(date):
    date = date.replace(tzinfo=None)
    return date.strftime('%a&nbsp;%d&nbsp;%b&nbsp;%Y&nbsp;%H:%M')

@app.route("/")
def Index():
    system = System()
    disk = system.disk_usage()
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hourUTC = strftime('%I:%M:%S %p', gmtime()) #UTC time
    localTime = strftime('%I:%M:%S %p', localtime()) # localtime
    hourdiff = int(localTime[1]) - int(hourUTC[1])
    return render_template('main.html', disk=disk, date=date, hourUTC = hourUTC, localTime = localTime, hourdiff = hourdiff)


@app.route("/register", methods=['POST','GET'])
def Register():

    error = None

    if not session.get('username'):


        if request.method == 'POST':

            firstname = request.form['firstname']
            lastname = request.form['lastname']
            email = request.form['email']
            number = request.form['number']
            

            if len(email) < 5:
                error = 'The email is invalid'
            elif len(firstname) < 1:
                error = 'The firstname cannot be empty'
            elif len(lastname) < 1:
                error = 'The lastname cannot be empty'
            else:
                system = System()
                account = system.account()

                response = User(email).register(firstname,lastname,email,account,number)
                if response == 1:
                    error = 'No record inserted, the email ('+email+') already exist'
                    
                else:

                    session['username'] = email
                    msg = Message("Registration successfull, your registration details ",sender=app.config["DEFAULT_MAIL_SENDER"],recipients=[email])
                    msg.html = render_template("reg-email.html",firstname=firstname,lastname=lastname,account=account,email=email)
                    thr = Thread(target=send_async_email_test, args=[app, msg])
                    thr.start()
                    flash("Logged In")
                    login_user = system.getUser(session.get('username'))
                    return redirect(url_for('Home', login_user=login_user))
        return render_template('register.html', error=error)
    system = System()
    login_user = system.getUser(session.get('username'))
    return render_template('home.html', login_user=login_user)


@app.route("/login", methods=['GET', 'POST'])
def Login():    

    if not session.get('username'):

        if request.method == 'POST':

            error = None
            email = request.form['email']
            account = request.form['account']
            if len(email) < 5:
                abort(400,'The email address is too short')
            elif len(account) < 1:
                abort(400,'No account number specified')
            response = User(email).login(account)
            if response == 1:
                flash("Logged In")
                session['username'] = email
                login_user = System().getUser(session.get('username'))
                return redirect(url_for('Home', login_user=login_user))
            error = 'Invalid login credentials'
            return render_template('login.html', error=error)
        return render_template('login.html')
    system = System()
    login_user = system.getUser(session.get('username'))
    return render_template('home.html', login_user=login_user)

@app.route('/customers')
def users():

    if session.get('username'):
        system = System()
        login_user = system.getUser(session.get('username'))
        customers = system.customers()
        return render_template('users.html', login_user=login_user, customers=customers)
    return redirect('/')

@app.route('/customers/create', methods=['POST','GET'])
def user_create():

    
    if session.get('username'):
        system = System()
        login_user = system.getUser(session.get('username'))
        error = None

        if request.method == 'POST':

            firstname = request.form['firstname']
            lastname = request.form['lastname']
            email_cust = request.form['email_cust'] or None
            origin = request.form['number']

            if len(firstname) < 1:
                abort(400, 'Enter firstname')
            elif len(lastname) < 1:
                abort(400, 'Enter lastname')
            elif len(origin) < 1:
                abort(400, 'Enter phone number')

            email = session.get('username')
            response = User(email).createCustomer(firstname,lastname,email_cust,origin)
            if response == 0:

                error = firstname + ' ' + lastname + ' is added Successfully'
                flash("Customer added Successfully")
                if email_cust is not None:

                    msg = Message("Registration successfull, your registration details ",sender=app.config["DEFAULT_MAIL_SENDER"],recipients=[email_cust])
                    msg.html = render_template("reg-email.html",firstname=firstname,lastname=lastname,email=email_cust)
                    thr = Thread(target=send_async_email_test, args=[app, msg])
                    thr.start()
                return render_template('user-create.html', login_user=login_user, error=error)

            if response == 1:

                error = origin + ' already exist, so no record created'
                return render_template('user-create.html', login_user=login_user, error=error)

        return render_template('user-create.html', login_user=login_user)
    return redirect('/')


@app.route('/customers/<int:user_id>')
def user(user_id=None):

    if session.get('username'):
        system = System()
        login_user = system.getUser(session.get('username'))
        user = system.getUserById(user_id)
        if not user:
            return redirect('/customers')
        return render_template('user.html', login_user=login_user, user=user)

    return redirect('/') 

@app.route('/customers/<int:user_id>/edit', methods=['GET','POST'])
@app.route('/customers/edit')
def user_edit(user_id=None):

    if session.get('username'):

        system = System()
        login_user = system.getUser(session.get('username'))
        user = system.getUserById(user_id)
        error = None
        if not user:
            return redirect('/customers')
        if request.method == 'POST':

            firstname = request.form['first_name']
            lastname = request.form['last_name']
            origin = request.form['number']
            user.first_name =firstname
            user.last_name =lastname
            user.number =origin
            try:
                db.session.commit()
                error = "Update successfull"
            except:
                error = "No update made, check Internet connectivity"
            return render_template('user-edit.html', login_user=login_user, user=user, error=error)
        return render_template('user-edit.html', login_user=login_user, user=user, error=error)

    return redirect('/')
    
@app.route('/customers/<int:user_id>/destinations', methods=['GET','POST'])
def destination_new(user_id):

    if session.get('username'):

        system = System()
        dids = system.available_dids()
        owns = system.owns()
        login_user = system.getUser(session.get('username'))
        user = system.getUserById(user_id)
        error = None
        if not user:
            return redirect('/customers')

        if request.method == 'POST':

            did = request.form['did']
            own = request.form['own']
            record = request.form['record']
            auth_gw = request.form['auth_gw']
            auth_did = request.form['auth_did']
            gateway = request.form['gateway']
            channel = request.form['channel']
            number = request.form['number']
            day = request.form['day']
            month = request.form['month']
            year = request.form['year']
            string_date = year + '-' + month + '-' + day + ' 12:00:00'
            end_date = datetime.datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S")
            email = session.get('username')
            response = User(email).destination_new(user_id,did,number,record,auth_did,auth_gw,gateway,channel,own,end_date)
            if response == 0:
                
                error = "Destination created for origin "
            if response == 1:
                error = " Destination number already exist with origin " 
            return render_template('destination-new.html', login_user=login_user, user=user, error=error, dids=dids, owns=owns)
        return render_template('destination-new.html', login_user=login_user, user=user, error=error, dids=dids, owns=owns)

    return redirect('/')


@app.route("/home")
def Home():

    if session.get('username'):

        #ip = gethostbyname(gethostname()) 
        ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR') 
        system = System()
        system.defaultAction()
        login_user = system.getUser(session.get('username'))
        return render_template('home.html', login_user=login_user, ip=ip)
    return redirect(url_for("Index"))


@app.route("/ipfilters")
def Ipfilters():

    if session.get('username'):

        ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR') 
        system = System()
        ipfilters = system.ipfilters()
        login_user = system.getUser(session.get('username'))
        return render_template('ipfilters.html', login_user=login_user, ip=ip, ipfilters=ipfilters)
    return redirect(url_for("Index"))


@app.route("/pin", methods=['POST','GET']) 
def Pin():


    if session.get('username'):

        system = System()
        pins = system.pins()
        login_user = system.getUser(session.get('username'))
        error = None

        if request.method == "POST":

            
            email = session.get('username')
            response = User(email).createPins()

            if type(response) is int:

                error = 'Error ' + str(response)
                return render_template('pin.html', login_user=login_user, error=error, pins=pins)
            else:

                error = response
                return render_template('pin.html', login_user=login_user, error=error, pins=pins)
        return render_template('pin.html', login_user=login_user, error=error, pins=pins)


    return redirect(url_for("Index"))


@app.route("/countries", methods=['POST','GET'])
def countries():
    if session.get('username'):

        system = System()
        countries = system.countries()
        login_user = system.getUser(session.get('username'))
        error = None
        if request.method == 'POST':

            country = request.form['country']
            region = request.form['region']

            if len(country) < 1:
                abort(400, 'No country entered')
            elif len(region) < 1:
                abort(400, 'No region selected')

            email = session.get('username')
            response = User(email).createCountry(region,country)
            if response == 0:
                error = country + ' added to region ' + region+', refresh browser to see update'
                flash("Country added Successfully")
                return render_template('country.html', login_user=login_user, error=error,countries=countries)
            if response == 506:

                abort(400,'No data insertion was made, please check Internet connectivity')
            if response == 1:
                error = country + ' already exist'
                return render_template('country.html', login_user=login_user, error=error,countries=countries)
        return render_template('country.html', login_user=login_user, error=error,countries=countries)

    return redirect(url_for("Index"))

@app.route("/own", methods=['POST','GET']) 
def Own():


    if session.get('username'):

        system = System()
        login_user = system.getUser(session.get('username'))
        dids = system.dids()
        owns = system.owns()
        error = None

        if request.method == 'POST':

            file = request.files['own_file']

            if not file:

                sim = request.form['sim']
                did = request.form['did']

                if len(sim) < 1:
                    abort(400, 'Please enter a SIM number')
                elif len(did) < 1:
                    abort(400,'Please select a did')

                email = session.get('username')
                response = User(email).createSim(sim,did)
                if response == 0:
                    flash('OWN Successfully created')
                    error = 'OWN Successfully created with did '+did
                    return render_template('own.html', login_user=login_user, error=error,owns=owns)

                elif response == 1:
                    abort(400, 'OWN %s already exist with SIM '%(sim))

                elif response == 506:
                    abort(400, 'Error:'+response+', Data insertion error')

            if System().allowed_file(file.filename):


                filename = secure_filename(file.filename)

                try:

                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    fileUrl = os.path.abspath(app.config['UPLOAD_FOLDER']+filename)
                    #fileUrl = path(app.config['UPLOAD_FOLDER']+filename).abspath()

                    error = 'File uploaded : Path -> ' + fileUrl
                    data_list_owns = system.readCSV(fileUrl)
                    insert_owns = system.insertOwns(data_list_owns)

                    error =  str(insert_owns) + ' OWN has been uploaded and saved'
                    #error =  data_list_owns

                except:


                    error = 'File not uploaded Successfully'
        
            else:

                error = 'File format is not allowed'

            return render_template('own.html', login_user=login_user, error=error, own_file=file, owns=owns)


        return render_template('own.html', login_user=login_user, error=error, dids=dids, owns=owns)


    return redirect(url_for("Index"))


@app.route("/did", methods=['POST','GET']) 
def Did():


    if session.get('username'):



        system = System()
        login_user = system.getUser(session.get('username'))
        pins = system.pins()
        countries = system.countries()
        dids = system.dids()
        error = None

        if request.method == 'POST':

            file = request.files['did_file']

            if not file:

                phone = request.form['phone']
                cost = request.form['cost']
                country = request.form['country']
                capacity = request.form['capacity']
                provider = request.form['provider']
                mode = request.form['mode']
                pin = request.form['pin']
        
                if len(phone) < 1:

                    abort(400, 'The phone number is invalid')
                elif len(cost) < 1:
                    abort(400,'Invalid cost specified')
                elif len(country) < 1:
                    abort(400, 'Invalid country code')
                elif len(capacity) < 1:
                    abort(400, 'Please select capacity')
                elif len(provider) < 1:
                    abort(400, 'Please select provider')
                elif len(mode) < 1:
                    abort(400, 'Please select mode')
                elif len(pin) < 1:
                    abort(400, 'Please select pin')

                email = session.get('username')
                response = User(email).createDid(phone,provider,cost,country,capacity,mode,pin)

                if response == 0:


                    flash('DID Successfully created')
                    error = 'DID Successfully created with pin '+pin
                    return render_template('did.html', login_user=login_user, error=error, dids=dids, pins=pins, countries=countries)

                elif response == 1:


                    abort(400, 'DID %s already exist'%(phone))
                else:
                    abort(400, 'DID is not created')
        
            if System().allowed_file(file.filename):


                filename = secure_filename(file.filename)

                try:

                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    fileUrl = os.path.abspath(app.config['UPLOAD_FOLDER']+filename)
                    #fileUrl = path(app.config['UPLOAD_FOLDER']+filename).abspath()

                    error = 'File uploaded : Path -> ' + fileUrl
                    data_list_dids = System().readCSV(fileUrl)
                    insert_dids = System().insertDids(data_list_dids)

                    error =  str(insert_dids) + ' DIDs has been uploaded and saved'

                except:


                    error = 'File not uploaded Successfully'
        
            else:

                error = 'File format is not allowed'

            return render_template('did.html', login_user=login_user, error=error, did_file=file, dids=dids,pins=pins,countries=countries)

        return render_template('did.html', login_user=login_user, error=error, pins=pins, dids=dids,countries=countries)

    return redirect(url_for("Index"))




    




@app.route("/logout", methods=['GET'])
def Logout():

    ## REMOVE THE username SESSION
    session.clear()
    return redirect(url_for('Index'))



def send_async_email_test(app,msg):
    
    with app.app_context():

        mail.send(msg)
        
    
        
    
    
if __name__ == "__main__":
    
    
    
    ##db.session.rollback() 
    #db.session.commit()
    #app.run(debug=True,port=90)
    #app.run()
    #system = System()
    #system.defaultAction()
    app.run(host='0.0.0.0')