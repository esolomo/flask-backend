from __future__ import print_function
from flask import Flask, render_template, url_for, request, session, redirect, jsonify, Response
from flask.ext.pymongo import PyMongo
from jinja2 import Template
import jinja2
import bcrypt
import backend
import ftp
import zone as Zone
import sys
import json
import ast
import arrow

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'targetweb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/betterdevops'
app.config["CACHE_TYPE"] = "null"

mongo = PyMongo(app)

@app.route('/api/session')
def check_session():
    if 'username' in session:
        #return 'You are logged in as ' + session['username']
        return  jsonify(status=True)       
        #return render_template('dashboard.html', username=session['username'])

    return jsonify(status=False)  

@app.route('/')
def index():
    if 'username' in session:
        #return 'You are logged in as ' + session['username']
        return redirect(url_for('ftp_mgnt'))        
        #return render_template('dashboard.html', username=session['username'])

    return render_template('index.html')


@app.route('/logout')
def logout():
        # remove the username from the session if it's there
        session.pop('username', None)
        return redirect(url_for('index'))

@app.route('/api/logout', methods=['GET', 'POST'])
def api_logout():
        # remove the username from the session if it's there
        session.pop('username', None)
        return jsonify(status="Success")

@app.route('/api/login', methods=['POST'])
def api_login():
    users = mongo.db.users
    data = request.get_data()
    user = ast.literal_eval(data)['username']
    password = ast.literal_eval(data)['password']    
    login_user = users.find_one({'name' : ast.literal_eval(data)['username']})
    if login_user:
        if bcrypt.hashpw(ast.literal_eval(data)['password'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            print('Valid username/password combination')
            session['username'] = ast.literal_eval(data)['username']
            return 'Valid username/password combination'
    print("Not found")
    return False

@app.route('/api/register', methods=['POST', 'GET'])
def api_register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.json['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.json['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.json['username'], 'password' : hashpass, 'fullname': request.json['fullname']})
            session['username'] = request.json['username']
            return jsonify(status="Success", message="user  has been created")  
        
        return jsonify(status="Success", message='That username already exists!')

    return jsonify(status="Error", message='not defined')


###
### FTP Service Management API
###

@app.route('/api/ftp', methods=['POST'])
def get_site():
    if request.json['site']:
        if 'username' in session:
            data = ftp.get(session['username'],request.json['site'])
            return jsonify(status="Sucess", message="FTP User list", results=data)
        return jsonify(status="Error", message="Please login", results=[])

@app.route('/api/ftp/user', methods=['POST'])
def ftp_user_add():
    ftp.add_user(session['username'], request.json)
    return jsonify(status="Success")

@app.route('/api/ftp/user', methods=['DELETE'])
def ftp_remove_user():
    ftp.remove_user(session['username'], request.args.get("ftpsite"), request.args.get("username"))
    return jsonify(status="Success", message="FTP user have been removed")

@app.route('/api/ftp/password', methods=['PUT'])
def ftp_update_password():
    ftp.update_password(session['username'], request.json)
    return jsonify(status="Success", message="Updated password")

@app.route('/api/ftp/datadir', methods=['PUT'])
def ftp_update_datadir():
    ftp.update_datadir(session['username'], request.json)
    return jsonify(status="Success", message="Updated datadir")

@app.route('/api/domain', methods=['POST'])
def add_domain():
    ftp.add_domain(request.json['name'], session['username'], request.json['alias'])
    return jsonify(status="Success", message="Domain has been added")

@app.route('/api/domain', methods=['DELETE'])
def delete_ftpsite():
    if 'username' in session:
        if request.args.get("ftpsite"):
            ftp.remove_domain(request.args.get("ftpsite"), session['username'])
        return jsonify(status="Success", message="FTP Site has been removed")
    return jsonify(status="Error", message="Please login")

@app.route('/api/domains', methods=['GET'])
def list_domains():
    if 'username' in session:
        domain_list = ftp.get_domains(session['username'])
        return jsonify(status="Success", domains=domain_list)
    return jsonify(status="Error", message="Please login")


###
### Gestion des DNS
###

@app.route('/api/dns', methods=['GET'])
def get_dns():
    data = Zone.get(request.args, session['username'])
    return jsonify(status="Success", results=data)


@app.route('/api/dns', methods=['PUT'])
def add_dns_records():
    Zone.update(request.json, session['username'])
    return jsonify(status="Success")

@app.route('/api/dns', methods=['DELETE'])
def delete_dns():
    Zone.remove(request.args, session['username'])
    return jsonify(status="Success")

@app.route('/api/dns', methods=['POST'])
def add_dns():
    if 'username' in session:
        Zone.create(request.json, session['username'])
        return jsonify(status="Success")
    return jsonify(status="Error ", message="Insertion failed")


@app.route('/api/config/dns', methods=['POST'])
def apply_zone_config():
    Zone.config_apply(request.json, session['username'])
    return jsonify(status="Success")

@app.route('/api/deploy/dns', methods=['POST'])
def deploy_config():
    #Zone.config_deploy(session['username'])
    Zone.config_deploy("mahny@mahny.com")
    return jsonify(status="Success")

###
### Gestion des Settings SSH 
###

@app.route('/api/settings/ssh', methods=['DELETE'])
def remove_ssh_id():
    #settings = backend.Settings(session['username'])
    settings = backend.Settings('mahny@mahny.com')
    name = request.args.get('name')
    if isinstance(name, unicode):
        print("No name argument to request , requesting all keys ")
        data = settings.remove_user_id(name)
        return jsonify(status="Success", message="Sucessfully remove user_id :" + name)
    return jsonify(status="Error")


@app.route('/api/settings/ssh', methods=['GET'])
def get_ssh_id():
    #settings = backend.Settings(session['username'])
    settings = backend.Settings('mahny@mahny.com')
    name = request.args.get('name')
    if not isinstance(name, unicode):
        print("No name argument to request , requesting all keys ")
        data = settings.get_user_id(False)
        return jsonify(status="Success", results=data)
    data = settings.get_user_id(name)
    return jsonify(status="Success", results=data)

@app.route('/api/settings/ssh', methods=['PUT'])
def update_ssh_id():
    #settings = backend.Settings(session['username'])
    if 'name' in request.json:
        settings = backend.Settings('mahny@mahny.com')
        data = settings.update_user_id(request.json)
        return jsonify(status="Success", message="update successfull for :" + request.json['name'])
    return jsonify(status="Error", message="name required")

@app.route('/api/settings/ssh', methods=['POST'])
def create_ssh_id():
    if 'name' in request.json:
        settings = backend.Settings('mahny@mahny.com')
        data = settings.create_user_id(request.json)
        return jsonify(status="Success", results=data)
    return jsonify(status="Error", results=[])

###
### Gestion des Settings DNS 
###

@app.route('/api/settings/dns', methods=['POST'])
def set_dns_settings():
    #settings = backend.Settings(session['username'])
    settings = backend.Settings('mahny@mahny.com')
    data = settings.set_dns_settings(request.json['type'], request.json['value'])
    return jsonify(status="Success", results=data)

@app.route('/api/settings/dns', methods=['GET'])
def get_dns_settings():
    #settings = backend.Settings(session['username'])
    dns = backend.DNS('mahny@mahny.com').set_settings()
    settings = backend.Settings('mahny@mahny.com')
    data = settings.get_dns_settings()
    return jsonify(status="Success", results=data)

###
### Gestion des Settings FTP 
###

@app.route('/api/settings/ftp', methods=['POST'])
def set_ftp_settings():
    #settings = backend.Settings(session['username'])
    settings = backend.Settings('mahny@mahny.com')
    data = settings.set_ftp_settings(request.json['value'])
    return jsonify(status="Success", results=data)

@app.route('/api/settings/ftp', methods=['GET'])
def get_ftp_settings():
    #settings = backend.Settings(session['username'])
    ftp = backend.FTP('mahny@mahny.com').set_settings()
    settings = backend.Settings('mahny@mahny.com')
    data = settings.get_ftp_settings()
    return jsonify(status="Success", results=data)

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(port=5000,host='0.0.0.0',debug=True)
