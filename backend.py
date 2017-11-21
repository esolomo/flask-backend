from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.exceptions import NetworkError
import warnings
import crypt
from flask import jsonify

env.user="admin"
env.key_filename=['/Users/solomo/.ssh/id_rsa']


warnings.simplefilter(action="ignore", category=FutureWarning)

def list_users2(server):
    print("hello World")
    env.host_string = server
    with hide('everything'), settings(warn_only=True):    
        result = run('cat /etc/passwd | grep ftp | awk -F \':\' \'{print $1 " " $6}\'')
    print result

def list_users(server):
    env.host_string = server
    ftp_user_list=[]
    try:
        with hide('everything'), settings(warn_only=True):
            result = run('cat /etc/passwd | grep ftp | awk -F \':\' \'{print $1 " " $6}\'')
    except NetworkError as e:
        print(e.message)
        return ftp_user_list             
    for ftpdata in result.stdout.split('\n'):
        ftp_user_list.append(dict(servername=server,username=ftpdata.split(" ")[0].strip(),homedir=ftpdata.split(" ")[1].strip()))
    return ftp_user_list
                

def UpdateUserDatadir(server,username, datadir):
    env.host_string = server    
    cmd = "usermod -d "+ datadir  + " " +  username
    return  sudo(cmd)

def UpdateUserPwd(server,username, password):
    env.host_string = server    
    encPass = crypt.crypt(password,"22")
    cmd = "usermod -p "+encPass + " " + username
    return  sudo(cmd)

def RemoveUser(server,username):
    env.host_string = server    
    return  sudo("userdel " + username)

def createUser(server,username,password,datadir):
    env.host_string = server    
    encPass = crypt.crypt(password,"22")
    cmd = "useradd -p "+encPass+ "-G ftponly  -s "+ "/bin/false "+ "-d "+ datadir + " -c \" FTP user "+ username +"\" " + username
    return sudo("useradd -p "+encPass+ " -s "+ "/bin/false "+ "-d "+ datadir + " -c \" FTP user "+ username +"\" " + username)
