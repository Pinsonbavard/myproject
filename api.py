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




    

e = create_engine("mysql://sql8128062:xW9TErGiJF@sql8.freemysqlhosting.net/sql8128062", pool_recycle=299)

#e = create_engine("mysql://firsvat:Firsvat@2016@98.102.204.204:3306/firsvat", pool_recycle=3600)

app = Flask(__name__)
app.secret_key = "moyinoluwa1999"

app.config['UPLOAD_FOLDER'] = 'C:/Users/pinso/Desktop/uploads/'
##app.config['UPLOAD_FOLDER'] = 'http://crestovista.com/guest-admin/www/img/'
CORS(app)


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



@app.route("/home")
def Home():

    if session.get('username'):


        system = System()
        login_user = system.getUser(session.get('username'))
        return render_template('home.html', login_user=login_user)
    return redirect(url_for("Index"))


@app.route("/pin", methods=['POST','GET']) 
def Pin():


    if session.get('username'):

        system = System()
        login_user = system.getUser(session.get('username'))
        error = None

        if request.method == "POST":

            
            email = session.get('username')
            response = User(email).createPins()

            if type(response) is int:

                error = 'Error ' + str(response)
                return render_template('pin.html', login_user=login_user, error=error)
            else:

                error = response
                return render_template('pin.html', login_user=login_user, error=error)
        return render_template('pin.html', login_user=login_user, error=error)


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
                    data_list_owns = System().readCSV(fileUrl)
                    insert_owns = System().insertOwns(data_list_owns)

                    error =  str(insert_owns) + ' OWN has been uploaded and saved'

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
                    return render_template('did.html', login_user=login_user, error=error, dids=dids)

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

            return render_template('did.html', login_user=login_user, error=error, did_file=file, dids=dids)

        return render_template('did.html', login_user=login_user, error=error, pins=pins, dids=dids)

    return redirect(url_for("Index"))




    




@app.route("/logout", methods=['GET'])
def Logout():

    ## REMOVE THE username SESSION
    session.clear()
    return redirect(url_for('Index'))




    
        
    
    
if __name__ == "__main__":
    
    
    
    ##db.session.rollback() 
    #db.session.commit()
    #app.run(debug=True,port=90)
    app.run()