from __future__ import print_function
from flask import Flask, render_template, url_for, request, session, redirect, jsonify
from flask.ext.pymongo import PyMongo
import bcrypt
import backend
import sys


app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'targetweb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/betterdevops'
app.config["CACHE_TYPE"] = "null"

mongo = PyMongo(app)

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
        

@app.route('/ftp', methods=['GET', 'POST'])
def ftp_mgnt():    
    domains = ["www.latitude360.fr","private.reals.fr", "obm.maisonsmca.fr", "passpro.gregoire.fr", "www.cartotheque.com", "www.robeez.eu", "www.aequalis-prevention.com", "wfsv135.webfutur.com", "wfsv100.webfutur.com", "www.partsandgo.fr", "www.kelquartier.com", "www.sobio-etic.com","plombservice.fr","www.leroidelafete.fr", "www.grandangle.com","demo.gregoiregroup.com", "www.laboratoire-leanature.com", "www.geoscopie.fr"]    
    if 'username' in session:
        #return 'You are logged in as ' + session['username']
        return render_template('ftp_management.html', username=session['username'],domains=domains)
    return render_template('index.html')

@app.route('/remove', methods=['POST'])
def ftp_remove():

    if request.method == 'POST':
        print(request.form['username'])
        print(request.form['domain'])
        backend.RemoveUser(request.form['domain'],request.form['username'])
        return redirect('/ftp/' + request.form['domain'])            
    else:    
        return 'You are logged in as XXX'         
    
    if 'username' in session:
        return 'You are logged in as ' + session['username']

    return render_template('index.html')

@app.route('/add', methods=['POST'])
def ftp_add():
    print("Adding ....")
    if request.method == 'POST':
        print(request.form['username'])
        print(request.form['domain'])
        print(request.form['password'])
        print(request.form['datadir'])
        print("Creating ...")
        backend.createUser(request.form['domain'],request.form['username'],request.form['password'],request.form['datadir'])
        return redirect('/ftp/' + request.form['domain'])            
    else:    
        return 'You are logged in as XXX'         
    
    if 'username' in session:
        return 'You are logged in as ' + session['username']

    return render_template('index.html')

@app.route('/password', methods=['GET', 'POST'])
def ftp_updatepwd():

    if request.method == 'POST':
        print(request.form['username'])
        print(request.form['domain'])
        print(request.form['password'])
        backend.UpdateUserPwd(request.form['domain'],request.form['username'],request.form['password'])
        return redirect('/ftp/' + request.form['domain'])            
    else:    
        return 'You are logged in as XXX'         
    
    if 'username' in session:
        return 'You are logged in as ' + session['username']

    return render_template('index.html')

@app.route('/datadir', methods=['GET', 'POST'])
def ftp_updatedatadir():

    if request.method == 'POST':
        print(request.form['username'])
        print(request.form['domain'])
        print(request.form['datadir'])
        backend.UpdateUserDatadir(request.form['domain'],request.form['username'],request.form['datadir'])
        return redirect('/ftp/' + request.form['domain'] )
    else:    
        return 'You are logged in as XXX'         
    
    if 'username' in session:
        return 'You are logged in as ' + session['username']
    
    return render_template('index.html')


@app.route('/ftp/<string:domain>', methods=['GET', 'POST'])
def ftp_domain(domain):
    print("in domain")
    print(domain)
    #ftp_list = backend.list_users("www.latitude360.fr")
    ftp_list = backend.list_users(domain)        
    if 'username' in session:
        #return 'You are logged in as ' + session['username']
        print('This error output', file=sys.stderr)
        print('This standard output', file=sys.stdout)
        print("In FTP Domain")
        print(ftp_list)
        return render_template('ftp_domain.html', username=session['username'],list=ftp_list,domain=domain)
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'

#@app.route('/register', methods=['POST', 'GET'])
#def register():
#    if request.method == 'POST':
#        users = mongo.db.users
#        existing_user = users.find_one({'name' : request.form['username']})
#
#        if existing_user is None:
#            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
#            users.insert({'name' : request.form['username'], 'password' : hashpass})
#            session['username'] = request.form['username']
#            return redirect(url_for('index'))
#        
#        return 'That username already exists!'
#
#    return render_template('register.html')

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(port=443,host='0.0.0.0',debug=True,ssl_context=('ssl/targetweb.betterdevops.co.uk.crt', 'ssl/targetweb.betterdevops.co.uk.key'))
