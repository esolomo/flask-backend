from __future__ import with_statement
from pymongo import MongoClient
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.exceptions import NetworkError
import warnings
import crypt


warnings.simplefilter(action="ignore", category=FutureWarning)

class Settings:
    def __init__(self,username):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.username = username

    def remove_user_id(self, data):
        db = self.client.betterdevops
        login_user = db.users.find_one({'name' : self.username})
        result = []
        print(data)
        for entry in login_user['user_id']:
            if not entry['name'] == data:
                result.append(entry) 
        db.users.update({'name' : self.username},{ '$set' : {  'user_id' : result } })

    def update_user_id(self, data):
        db = self.client.betterdevops
        login_user = db.users.find_one({'name' : self.username})
        result = []
        for entry in login_user['user_id']:
            if entry['name'] == data['name']:
                result.append(data)
            else:
                result.append(entry) 
        db.users.update({'name' : self.username},{ '$set' : {  'user_id' : result } })
        return(dict(status='Success')) 

    def set_dns_settings(self, type, value):
        print("Settings DNS SSH Config for user_id")
        db = self.client.betterdevops
        login_user = db.users.find_one({'name' : self.username})
        dns_settings = login_user['dns_settings']
        if type == 'ssh':
            for entry in login_user['user_id']:
                if entry['name'] == value:
                    db.users.update({'name' : self.username},{'$set':{  'dns_user_id' : entry  } })
        if type == 'bind_config_dir' or type == 'bind_include_file' or type == 'bind_zone_file_dir' or type == 'primary_dns' or type == 'secondary_dns' or type == 'reload_dns_command' or type == 'ssh_key':
            dns_settings[type] = value
            db.users.update({'name' : self.username},{'$set':{  'dns_settings' : dns_settings  } })
        return(dict(status='Success'))  

    def get_dns_settings(self):
        print("Settings DNS SSH Config for user_id")
        db = self.client.betterdevops
        login_user = db.users.find_one({'name' : self.username})
        login_user['dns_settings' ]['ssh_key']  = login_user['dns_user_id' ]['name']
        return(login_user['dns_settings' ])  

    def get_ftp_settings(self):
        print("Settings DNS SSH Config for user_id")
        db = self.client.betterdevops
        login_user = db.users.find_one({'name' : self.username})
        return(login_user['ftp_settings' ])

    def set_ftp_settings(self, value):
        print("Settings FTP SSH Config for user_id")
        db = self.client.betterdevops
        login_user = db.users.find_one({'name' : self.username})
        ftp_settings = login_user['ftp_settings']
        for entry in login_user['user_id']:
            if entry['name'] == value:
                ftp_settings['ssh_key_name'] = value
                ftp_settings['ssh_user'] = entry['ssh_user']
                ftp_settings['ssh_key'] = entry['ssh_key']
                db.users.update({'name' : self.username},{'$set':{  'ftp_settings' : ftp_settings  } })
        return(dict(status='Success'))  


    def set_ftp_user_id(self, name):
        db = self.client.betterdevops
        login_user = db.users.find_one({'name' : self.username})
        for entry in login_user['user_id']:
            if entry['name'] == name:
                db.users.update({'name' : self.username},{'$set':{  'ftp_user_id' : entry  } }) 
        return(dict(status='Success')) 

    def create_user_id(self, data):
        db = self.client.betterdevops
        if 'ssh_user' in  data and 'ssh_key' in data:
            print("Setting SSH User for user" + self.username )
            user_data = db.users.find_one({'name' : self.username})
            if 'user_id' in user_data:
                print("Found user_id already")
                user_id = user_data['user_id']
            else:
                print("Can't find user_id already")
                user_id = []
            for entry in user_id:
                if 'name' in entry:
                    if entry['name'] == data['name']:
                        print("Error entry already exist")
                        return(dict(status='Failure', message="user_id name already exist : " + data['name']))
            user_id.append({'name':data['name'], 'ssh_user':data['ssh_user'],'ssh_key':data['ssh_key']})
            db.users.update({'name' : self.username},{'$set': {  'user_id' : user_id } })
            user_data = db.users.find_one({'name' : self.username})
            print(user_data)
            return(dict(status='Success'))

    def get_user_id(self, name):
        db = self.client.betterdevops
        login_user = db.users.find_one({'name' : self.username})
        if name == False:
            if 'user_id' in login_user:
                data = login_user['user_id']
            return(data)
        result = []
        for entry in login_user['user_id']:
            if 'name' in entry:
                if entry['name'] == name:
                    result.append(entry)
        return(result)

class DNS:
    def __init__(self,username):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client.betterdevops
        self.username = username
        self.set_settings()
        self.dns_servers = [dict(name=self.primary_dns, conf_suffix=".conf_master"), dict(name=self.secondary_dns, conf_suffix=".conf_slave")]

    def set_settings(self):
        login_user = self.db.users.find_one({'name' : self.username})
        if 'dns_settings'  in login_user:
            dns_settings = login_user['dns_settings']
            if 'bind_config_dir' in dns_settings:
                self.bind_config_dir = login_user['dns_settings']['bind_config_dir']
            else:
                dns_settings['bind_config_dir'] = "/etc/bind/named.conf.d.webfuturadmin"
                self.db.users.update({'name' : self.username},{'$set': {  'dns_settings' : dns_settings } })
            if 'bind_include_file' in dns_settings:
                self.bind_include_file = login_user['dns_settings']['bind_include_file']
            else:
                dns_settings['bind_include_file'] = "/etc/bind/named.conf.webfuturadmin"
                self.db.users.update({'name' : self.username},{'$set': {  'dns_settings' : dns_settings } })
            if 'bind_zone_file_dir' in dns_settings:
                self.bind_zone_file_dir = login_user['dns_settings']['bind_zone_file_dir']
            else:
                dns_settings['bind_zone_file_dir'] = "/tmp"
                self.db.users.update({'name' : self.username},{'$set': {  'dns_settings' : dns_settings } })
            if 'primary_dns' in dns_settings:
                self.primary_dns = login_user['dns_settings']['primary_dns']
            else:
                dns_settings['primary_dns'] = "ns1.webfutur.com"
                self.db.users.update({'name' : self.username},{'$set': {  'dns_settings' : dns_settings } })
            if 'secondary_dns' in dns_settings:
                self.secondary_dns = login_user['dns_settings']['secondary_dns']
            else:
                dns_settings['secondary_dns'] = "ns2.webfutur.com"
                self.db.users.update({'name' : self.username},{'$set': {  'dns_settings' : dns_settings } })
            if 'reload_dns_command' in dns_settings:
                self.reload_dns_command = login_user['dns_settings']['reload_dns_command']
            else:
                dns_settings['reload_dns_command'] = "/usr/local/sbin/reload_dns.sh"
                self.db.users.update({'name' : self.username},{'$set': {  'dns_settings' : dns_settings } })
            if 'ssh_key' in dns_settings:
                self.ssh_key = login_user['dns_settings']['ssh_key']
            else:
                dns_settings['ssh_key'] = ""
                self.db.users.update({'name' : self.username},{'$set': {  'dns_settings' : dns_settings } })
            if 'ssh_user' in dns_settings:
                self.ssh_user = login_user['dns_settings']['ssh_user']
            else:
                dns_settings['ssh_user'] = "admin"
                self.db.users.update({'name' : self.username},{'$set': {  'dns_settings' : dns_settings } })
        else:
            dns_settings = dict(bind_config_dir="/etc/bind/named.conf.d.webfuturadmin/",bind_include_file="/etc/bind/named.conf.webfuturadmin",bind_zone_file_dir="/tmp/",primary_dns="ns1.webfutur.com",secondary_dns="ns2.webfutur.com",reload_dns_command="/usr/local/sbin/reload_dns.sh")
            self.db.users.update({'name' : self.username},{'$set': {  'dns_settings' : dns_settings } })
            self.bind_config_dir = "/etc/bind/named.conf.d.webfuturadmin"
            self.bind_include_file = "/etc/bind/named.conf.webfuturadmin"
            self.bind_zone_file_dir = "/tmp/"
            self.primary_dns = "ns1.webfutur.com"
            self.secondary_dns = "ns2.webfutur.com"
            self.reload_dns_command = "/usr/local/sbin/reload_dns.sh"

    def set_user_id(self):
        login_user = self.db.users.find_one({'name' : self.username})
        ssh_key_name = login_user['dns_user_id']['name']
        Settings(self.username).set_dns_settings('ssh', ssh_key_name)
        data = self.db.users.find_one({'name' : self.username})
        print(data['dns_user_id'])
        self.ssh_user = data['dns_user_id']['ssh_user'] 
        self.ssh_key =  data['dns_user_id']['ssh_key']

    def set_dns_servers(self, primary,secondary):
        self.primary_dns = primary
        self.secondary_dns = secondary
        self.dns_servers = [dict(name=primary, conf_suffix=".conf_master"), dict(name=secondary, conf_suffix=".conf_slave")]
 
    def transfertZoneFile(self, zonefile):
        print("Sending  includes file to master and slave  server")
        env.user = self.ssh_user
        env.key = self.ssh_key 
        env.host_string =  self.primary_dns
        print("Zone files dir :  " + self.bind_zone_file_dir)
        with hide('everything'), settings(warn_only=True):    
            result = put('./output/' + zonefile , self.bind_zone_file_dir + '/' +  zonefile,use_sudo=True)
        print result


    def transfertIncludeFile(self, filename):
        print("Sending  includes file to master and slave  server")
        env.user = self.ssh_user
        env.key = self.ssh_key 
        for server in self.dns_servers:
            env.host_string = server['name']
            with hide('everything'), settings(warn_only=True):    
                result = put(filename , self.bind_include_file,use_sudo=True)
        print result

    def transfertConfFile(self, filename, conf_name):
        env.user = self.ssh_user
        env.key = self.ssh_key
        for server in self.dns_servers :
            print server
            print("Sending  config file  to " + server['name'] )
            env.host_string = server['name']
            with hide('everything'), settings(warn_only=True):    
                result = put(filename + server['conf_suffix'] , self.bind_config_dir +  conf_name,use_sudo=True)
        print result

    def transfertFileToDNS(self, server,filename):
        env.user = self.ssh_user
        env.key = self.ssh_key
        print("Sending file to primary dns server")
        env.host_string = server
        with hide('everything'), settings(warn_only=True):    
            result = put(filename ,self.bind_zone_file_dir ,use_sudo=True)
        print result

    def ReloadDNS(self, server):
        print("Reloading DNS")
        env.user = self.ssh_user
        env.key = self.ssh_key
        env.host_string = server
        with hide('everything'), settings(warn_only=True):    
            result = sudo(self.reload_dns_command)
        print result


class FTP:
    def __init__(self,username):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client.betterdevops
        self.username = username
        self.ssh_user = "admin"
        self.key_filename= ['/Users/solomo/.ssh/id_rsa']
        self.set_settings()

    def set_settings(self):
        login_user = self.db.users.find_one({'name' : self.username})
        if 'ftp_settings'  in login_user:
            ftp_settings = login_user['ftp_settings']
            if 'ssh_key_name' in ftp_settings:
                self.ssh_user = login_user['ftp_settings']['ssh_key_name']
            else:
                ftp_settings['ssh_key_name'] = "admin"
                self.db.users.update({'name' : self.username},{'$set': {  'ftp_settings' : ftp_settings } })
            if 'ssh_user' in ftp_settings:
                self.ssh_user = login_user['ftp_settings']['ssh_user']
            else:
                ftp_settings['ssh_user'] = "admin"
                self.db.users.update({'name' : self.username},{'$set': {  'ftp_settings' : ftp_settings } })
            if 'ssh_key' in ftp_settings:
                self.ssh_key = login_user['ftp_settings']['ssh_key']
            else:
                ftp_settings['ssh_key'] = ""
                self.db.users.update({'name' : self.username},{'$set': {  'ftp_settings' : ftp_settings } })
        else:
            ftp_settings = dict(ssh_user="admin",ssh_key="",ssh_key_name="default")
            self.db.users.update({'name' : self.username},{'$set': {  'ftp_settings' : ftp_settings } })
            self.ssh_key_name = "default"
            self.ssh_user = "admin"
            self.ssh_key = ""

    def get_user_id(self):
        self.user = "admin"
        self.key_filename= ['/Users/solomo/.ssh/id_rsa']

    def list_users(self, server):
        ftp_users = self.db.ftp_users.find({'owner' : self.username,'domain':server})
        results = []
        for user in  ftp_users:
            del user['_id']
            results.append(user)
        print(results)
        return results

    def list_users2(self, server):
        env.host_string = server
        env.user = self.ssh_user
        #env.key = self.ssh_key
        env.key_filename = ['/Users/solomo/.ssh/id_rsa']
        with hide('everything'), settings(warn_only=True):    
            result = run('cat /etc/passwd | grep ftp | awk -F \':\' \'{print $1 " " $6}\'')
        print result

    def list_users3(self,server):
        env.host_string = server
        env.timeout = 20
        env.connection_attempts = 3
        env.user = self.ssh_user
        #env.key = self.ssh_key
        env.key_filename = self.key_filename
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
                    
    def UpdateUserDatadir(self, server,username, datadir):
        self.db.ftp_users.update({'owner' : self.username,'domain':server, 'username' : username}, { '$set' : { 'homedir' : datadir } })
        return True 

    def UpdateUserDatadir2(self, server,username, datadir):
        env.host_string = server    
        cmd = "usermod -d "+ datadir  + " " +  username
        return  sudo(cmd)

    def UpdateUserPwd(self, server,username, password):
        self.db.ftp_users.update({'owner' : self.username,'domain':server, 'username' : username}, { '$set' : { 'password' : password } })
        return True 

    def UpdateUserPwd2(self, server,username, password):
        env.host_string = server    
        encPass = crypt.crypt(password,"22")
        cmd = "usermod -p "+encPass + " " + username
        return  sudo(cmd)

    def RemoveUser(self, server,username):
        self.db.ftp_users.remove({'owner' : self.username,'domain':server, 'username' : username})
        return True

    def RemoveUser2(self, server,username):
        env.host_string = server    
        return  sudo("userdel " + username)

    def createUser(self, server,username,password,datadir):
        ftp_users = self.db.ftp_users.insert({'owner' : self.username,'domain':server, 'username' : username, 'homedir':datadir, 'password' : password })
        return True       

    def createUser2(self, server,username,password,datadir):
        env.host_string = server    
        encPass = crypt.crypt(password,"22")
        cmd = "useradd -p "+encPass+ "-G ftponly  -s "+ "/bin/false "+ "-d "+ datadir + " -c \" FTP user "+ username +"\" " + username
        return sudo("useradd -p "+encPass+ " -s "+ "/bin/false "+ "-d "+ datadir + " -c \" FTP user "+ username +"\" " + username)
