from __future__ import print_function
from flask import Flask, render_template, url_for, request, session, redirect, jsonify, Response
from flask.ext.pymongo import PyMongo
from jinja2 import Template
import jinja2
import bcrypt
import backend
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
        print("Logging out")
        print(session['username'])
        session.pop('username', None)
        return jsonify(status="Success")
        

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


@app.route('/api/ftp/user', methods=['POST'])
def ftp_user_add():
    print("Adding ftp user")
    backend.createUser(request.json['domain'],request.json['username'],request.json['password'],request.json['datadir'])
    return jsonify(status="Success")           


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

@app.route('/api/ftp/password', methods=['PUT'])
def ftp_update_password():
        print(request.json)
        username = request.json['username'] 
        ftpsite = request.json['ftpsite'] 
        password = request.json['password'] 
        backend.UpdateUserPwd(ftpsite,username,password)
        return jsonify(status="Success", message="Updated password") 

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

@app.route('/api/ftp/datadir', methods=['PUT'])
def ftp_update_datadir():
        print(request.json)
        username = request.json['username'] 
        ftpsite = request.json['ftpsite'] 
        datadir = request.json['datadir'] 
        backend.UpdateUserDatadir(ftpsite,username,datadir)
        return jsonify(status="Success", message="Updated datadir")         


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

@app.route('/api/ftp', methods=['POST'])
def get_site():
    if request.json['site']:
        if 'username' in session:
            ftp_list = backend.list_users(request.json['site'])        
            print(ftp_list)
            return jsonify(status="Sucess", message="FTP User list", results=ftp_list)
        else:
           return jsonify(status="Error", message="Please login", results=[]) 
    else:
        return jsonify(status="Error", message="Empty server data", results=[])

@app.route('/api/ftp/<string:domain>', methods=['GET', 'POST'])
def ftp2_domain(domain):
    ftp_list = backend.list_users(domain)
    print("List :")
    print(ftp_list)
    return jsonify(ftp_list)

@app.route('/api/dns', methods=['GET'])
def get_dns():
    zones = mongo.db.dns_zone
    data = []
    if request.args.get("zone"):
        data = zones.find_one({"zone":request.args.get("zone"), "owner":session['username']})
        if data:
            del data['_id']
            return jsonify(status="Success",results=data)
        return jsonify(status="Error")
    for zone in zones.find({"owner":session['username']}):
        del zone['_id']
        data.append(zone)
    print(data)
    return jsonify(status="Success",results=data)

@app.route('/api/ftp/user', methods=['DELETE'])
def ftp_remove_user():
        username = request.args.get("username")
        ftpsite = request.args.get("ftpsite")
        backend.RemoveUser(ftpsite,username)
        return jsonify(status="Success",message="FTP user have been removed")
    


@app.route('/api/domain', methods=['DELETE'])
def delete_ftpsite():
        domains = mongo.db.domains
        ftpsite = request.args.get("ftpsite")
        print("Removing " + request.args.get("ftpsite"))
        if request.args.get("ftpsite"):
            data = domains.find_one({"name":request.args.get("ftpsite")})
            if data:
                del data['_id']
                domains.remove({ "name":request.args.get("ftpsite") }  )
                return jsonify(status="Success", message="FTP Site has been removed") 
            return jsonify(status="Error", message="No such ftp domain")
        return jsonify(status="Error", message="Missing argument")      

@app.route('/api/dns', methods=['PUT'])
def add_dns_records():
    print(request.json)
    zone = mongo.db.dns_zone
    username = session['username']
    #username = "mahny@mahny.com"
    record = zone.find_one({"owner":username, "zone":request.json["zone"]})
    
    if request.json['type'] == 'A':
        print("TYPE A request")
        record['A'].append(dict(name=request.json['name'],destination=request.json['destination']))
        zone.update_one({"owner":username, "zone":request.json["zone"]}, { "$set": { "A": record['A'] }  })
    elif request.json['type'] == 'AAAA':
        print("TYPE AAAA request")
        record['AAAA'].append(dict(name=request.json['name'],destination=request.json['destination']))
        zone.update_one({"owner":username, "zone":request.json["zone"]}, { "$set": { "AAAA": record['AAAA'] } })
    elif request.json['type'] == 'CNAME':
        print("TYPE CNAME request")
        record['CNAME'].append(dict(name=request.json['name'],destination=request.json['destination']))
        zone.update_one({"owner":username, "zone":request.json["zone"]}, { "$set": { "CNAME": record['CNAME'] } })
    elif request.json['type'] == 'MX':
        print("TYPE MX request")
        record['MX'].append(dict(name=request.json['name'],priority=request.json['priority']))
        zone.update_one({"owner":username, "zone":request.json["zone"]}, { "$set": { "MX": record['MX'] } })
    elif request.json['type'] == 'TXT':
        print("TYPE TXT request")
        record['TXT'].append(dict(name=request.json['name'],entry=request.json['entry']))
        zone.update_one({"owner":username, "zone":request.json["zone"]}, { "$set": { "TXT": record['TXT'] } })
    elif request.json['type'] == 'SRV':
        print("TYPE SRV request")
        record['SRV'].append(dict(name=request.json['name'],destination=request.json['destination']))
        zone.update_one({"owner":username, "zone":request.json["zone"]}, { "$set": { "SRV": record['SRV'] } })
    else:
        print("No type defined")
        return jsonify(status="Error")
    return jsonify(status="Success")

@app.route('/api/dns', methods=['DELETE'])
def delete_dns():
    zones = mongo.db.dns_zone
    data = []
    zone = request.args.get("zone")
    print("Before Printing")
    if request.args.get("zone"):
        data = zones.find_one({"owner":session['username'], "zone":zone })
        if data:
            del data['_id']
            if request.args.get("type") == 'full':
                zones.remove({"owner":session['username'], "zone":zone})
            else:
                type = request.args.get("type")
                name =request.args.get("name")
                update_data = []
                records = zones.find_one({"owner":session['username'], "zone": zone})
                if type == 'CNAME' or type == 'A' or type == 'AAAA':
                    destination =request.args.get("destination")
                    for record in records[type]:
                        if not (name == record['name'] and destination == record['destination']):
                            update_data.append(record)
                elif type == 'MX' or type == 'SRV':
                    priority = request.args.get("priority")
                    for record in records[type]:
                        print(record)
                        if not (name == record['name'] ):
                            update_data.append(record)
                elif type == 'TXT':
                    entry = request.args.get("entry")
                    for record in records[type]:
                        if not (name == record['name'] and entry == record['entry']):
                            update_data.append(record)
                records[type] = update_data
                zones.update_one({"owner":session['username'], "zone":zone}, { "$set": records  })
            return jsonify(status="Success",results=data)
        return jsonify(status="Error")
    return jsonify(status="Error",message="No such zone")


@app.route('/api/config/dns', methods=['POST'])
def apply_zone_config():
    print(request.json["zone"])
    zones = mongo.db.dns_zone
    zone  = zones.find_one({"owner":session['username'], "zone":request.json["zone"]})
    print("Ready to apply this config")
    del zone['_id']
    templateLoader = jinja2.FileSystemLoader( searchpath="./templates/")
    templateEnv = jinja2.Environment( loader=templateLoader,trim_blocks=True )
    TEMPLATE_FILE = "template.zone"
    template = templateEnv.get_template(TEMPLATE_FILE)
    print(zone['CNAME'])
    min_ttl = "1D"
    root_ipv4 = ["213.186.33.16", "213.186.33.50", "213.186.33.173"]
    root_ipv6 = ["2001:41d0:1:1b00:213:186:33:50"]
    soa = ["ns1.webfutur.com", "sysadmin.webfutur.net"]
    ns = ["ns1.webfutur.com", "ns2.webfutur.com"]
    serial = arrow.now().format('YYYYMMDDSS')
    output = template.render(root_ipv4=root_ipv4,root_ipv6=root_ipv6,min_ttl=min_ttl,soa=soa,ns=ns,serial=serial,cname_records=zone['CNAME'],a_records=zone['A'],aaaa_records=zone['AAAA'],mx_records=zone['MX'])

    #t = Template("Hello {{ something }}!") 
    #output = t.render(something=request.json["zone"])
    with open('./output/' + request.json["zone"] + ".zone", 'w') as f:
        f.write(output)
    #print(zone)
    return jsonify(status="Success")


@app.route('/api/dns', methods=['POST'])
def add_dns():
    if 'username' in session:
        zone = mongo.db.dns_zone
        organisation = "BetterDevOps"
        soa = ["ns1.webfutur.com", "sysadmin.webfutur.net"]
        ns = ["ns1.webfutur.com", "ns2.webfutur.com"]
        serial = arrow.now().format('YYYYMMDDSS')
        zone.insert(dict(soa=["ns1.webfutur.com", "sysadmin.webfutur.net"],ns=["ns1.webfutur.com", "ns2.webfutur.com"],owner=session["username"],organisation=organisation,zone=request.json["name"],MX=[],A=[],AAAA=[],CNAME=[],TXT=[],SRV=[]))
        return jsonify(status="Success")
    return jsonify(status="Error ", message="Insertion failed")

@app.route('/api/domains', methods=['GET'])
def list_domains():
    if 'username' in session:
        users = mongo.db.users
        domains = mongo.db.domains
        login_user = users.find_one({'name' : session['username']})
        domain_list =  []
        print(session['username'])
        for domain in domains.find({"owner":session['username']}):
            alias = domain['alias'] if 'alias' in domain.keys()  else 'undefined'
            domain_list.append(dict(name=domain['name'],alias=alias,owner=domain['owner'],status=int(domain['status']),group=int(domain['group'])   )     )
        print(jsonify(domain_list))
        return jsonify(status="Success",domains=domain_list)
    return jsonify(status="Error", message="Please login")

@app.route('/api/domain', methods=['PUT'])
def update_domain():
        domains = mongo.db.domains
        domain = domains.find({"name": request.json['domain_name'], "owner":session['username']})
        print(domain[0])
        domains.update_one({"name": request.json['domain_name'], "owner":session['username']}, { "$set": { "status": request.json['data']['status'], "group": request.json['data']['group'] }  })
        return "JSON Message: " + json.dumps(request.json)

@app.route('/api/domain', methods=['POST'])
def add_domain():
        domains = mongo.db.domains
        domain = domains.insert({"name": request.json['name'], "owner":session['username'], "alias": request.json['alias'], "status": request.json['status'], "group": request.json['group']})
        return jsonify(status="Success", message="Domain has been added")  

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    print(request.data)
    print("trying to log in in /login with user" +  request.form['username'] )
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'

@app.route('/api/login', methods=['POST'])
def api_login():
    users = mongo.db.users
    data = request.get_data()
    print(data) 
    user = ast.literal_eval(data)['username']
    password = ast.literal_eval(data)['password']
    print(password)     
    login_user = users.find_one({'name' : ast.literal_eval(data)['username']})
    
    if login_user:
        if bcrypt.hashpw(ast.literal_eval(data)['password'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            print('Valid username/password combination')
            session['username'] = ast.literal_eval(data)['username']
            return 'Valid username/password combination'

    print("Not found")
    return False

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
        return 'That username already exists!'

    return render_template('register.html')

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

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(port=5000,host='0.0.0.0',debug=True)
