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




    

#e = create_engine("mysql://sql5108481:r5EncJbtBG@sql5.freemysqlhosting.net/sql5108481", pool_recycle=299)

#e = create_engine("mysql://firsvat:Firsvat@2016@98.102.204.204:3306/firsvat", pool_recycle=3600)

app = Flask(__name__)
app.secret_key = "moyinoluwa1999"

app.config['UPLOAD_FOLDER'] = 'uploads/'
CORS(app)


manager = APIManager(app,flask_sqlalchemy_db=db)


manager.create_api(Users, methods=["GET","POST","DELETE"])

manager.create_api(Calls)

manager.create_api(Destinations)





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

    system = System()
    login_user = system.getUser(session.get('username'))
    return render_template('home.html', login_user=login_user)

@app.route("/did", methods=['POST','GET']) 
def Did():


    system = System()
    login_user = system.getUser(session.get('username'))
    error = None

    if request.method == 'POST':

        file = request.files['did_file']

        if not file:

            phone = request.form['phone']
            cost = request.form['cost']
            country = request.form['country']
            capacity = request.form['capacity']
            provider = request.form['provider']
        
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

            email = session.get('username')
            response = User(email).createDid(phone,provider,cost,country,capacity)

            if response == 0:


                flash('DID Successfully created')
                error = 'DID Successfully created'

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
        return render_template('did.html', login_user=login_user, error=error, did_file=file)

    return render_template('did.html', login_user=login_user, error=error)




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