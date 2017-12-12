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

###
### Update FTP user methods
###

def add_user(owner, data):
    """Add user to FTP domain"""
    print("Adding ftp user")
    backend.FTP(owner).createUser(data['domain'], data['username'], data['password'], data['datadir'])
    return True

def remove_user(owner,domain, username):
    """Remove FTP user"""
    backend.FTP(owner).RemoveUser(domain, username)
    return True

def update_password(owner, data):
    """Update password for FTP user"""
    backend.FTP(owner).UpdateUserPwd(data['ftpsite'], data['username'], data['password'])
    return True

def update_datadir(owner, data):
    """Update datadir for FTP user """
    backend.FTP(owner).UpdateUserDatadir(data['ftpsite'], data['username'], data['datadir'])
    return True

###
### Update FTP user methods
###

def get(owner, domain):
    """Return FTP domain data """
    data = backend.FTP(owner).list_users(domain)
    return data

def remove_domain(domain,owner):
    """Return FTP domain"""
    domains = mongo.db.domains
    data = domains.find_one({"name":domain, "owner":owner})
    if data:
        domains.remove({"name":domain, "owner":owner})
        return True
    return False


def get_domains(owner):
    """Return FTP domain"""
    domains = mongo.db.domains
    domain_list = []
    for domain in domains.find({"owner":owner}):
        alias = domain['alias'] if 'alias' in domain.keys()  else 'undefined'
        data = dict(name=domain['name'], alias=alias, owner=domain['owner'])
        domain_list.append(data)
    return domain_list

def add_domain(name,owner, alias):
    """Add FTP domain"""
    domains = mongo.db.domains
    domains.insert({"name":name, "owner":owner, "alias":alias})
    return True











