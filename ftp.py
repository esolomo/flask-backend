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

def add_user(data):
    """Add user to FTP domain"""
    print("Adding ftp user")
    backend.createUser(data['domain'], data['username'], data['password'], data['datadir'])
    return True

def remove_user(domain, username):
    """Remove FTP user"""
    backend.RemoveUser(domain, username)
    return True

def update_password(data):
    """Update password for FTP user"""
    backend.UpdateUserPwd(data['ftpsite'], data['username'], data['password'])
    return True

def update_datadir(data):
    """Update datadir for FTP user """
    backend.UpdateUserDatadir(data['ftpsite'], data['username'], data['datadir'])
    return True

###
### Update FTP user methods
###

def get(domain):
    """Return FTP domain data """
    data = backend.list_users(domain)
    return data

def remove_domain(domain,username):
    """Return FTP domain"""
    domains = mongo.db.domains
    data = domains.find_one({"name":domain, "owner":username})
    if data:
        domains.remove({"name":domain, "owner":username})
        return True
    return False


def get_domains(username):
    """Return FTP domain"""
    domains = mongo.db.domains
    domain_list = []
    for domain in domains.find({"owner":username}):
        alias = domain['alias'] if 'alias' in domain.keys()  else 'undefined'
        data = dict(name=domain['name'], alias=alias, owner=domain['owner'])
        domain_list.append(data)
    return domain_list

def add_domain(name,username, alias):
    """Add FTP domain"""
    domains = mongo.db.domains
    domains.insert({"name":name, "owner":username, "alias":alias})
    return True











