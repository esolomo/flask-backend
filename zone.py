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
import subprocess

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'targetweb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/betterdevops'
app.config["CACHE_TYPE"] = "null"

mongo = PyMongo(app)


###
### Return Zone Data
###

def get(args, owner):
    zones = mongo.db.dns_zone
    data = []
    if args.get("zone"):
        data = zones.find_one({"zone":args.get("zone"), "owner":owner})
        if data:
            del data['_id']
            return data
        return False
    for zone in zones.find({"owner":owner}):
        del zone['_id']
        data.append(zone)
    return data


###
### Update Zone Data
###

def update(data, username):
    zone = mongo.db.dns_zone
    owner = username
    ttl = data['ttl'] if 'ttl' in data else False
    record = zone.find_one({"owner":owner, "zone":data["zone"]})
    
    if data['type'] == 'A':
        print("TYPE A request")
        record['A'].append(dict(name=data['name'],ttl=ttl,destination=data['destination']))
        zone.update_one({"owner":owner, "zone":data["zone"]}, { "$set": { "A": record['A'] }  })
    elif data['type'] == 'AAAA':
        print("TYPE AAAA request")
        record['AAAA'].append(dict(name=data['name'],ttl=ttl,destination=data['destination']))
        zone.update_one({"owner":owner, "zone":data["zone"]}, { "$set": { "AAAA": record['AAAA'] } })
    elif data['type'] == 'ROOT_IPv4':
        print("TYPE ROOT_IPv4 request")
        record['ROOT_IPv4'].append(data['value'])
        zone.update_one({"owner":owner, "zone":data["zone"]}, { "$set": { "ROOT_IPv4": record['ROOT_IPv4'] }  })
    elif data['type'] == 'ROOT_IPv6':
        print("TYPE ROOT_IPv6 request")
        record['ROOT_IPv6'].append(data['value'])
        zone.update_one({"owner":owner, "zone":data["zone"]}, { "$set": { "ROOT_IPv6": record['ROOT_IPv6'] } })
    elif data['type'] == 'CNAME':
        print("TYPE CNAME request")
        record['CNAME'].append(dict(name=data['name'],ttl=ttl,destination=data['destination']))
        zone.update_one({"owner":owner, "zone":data["zone"]}, { "$set": { "CNAME": record['CNAME'] } })
    elif data['type'] == 'MX':
        print("TYPE MX request")
        record['MX'].append(dict(name=data['name'],priority=data['priority']))
        zone.update_one({"owner":owner, "zone":data["zone"]}, { "$set": { "MX": record['MX'] } })
    elif data['type'] == 'TXT':
        print("TYPE TXT request")
        record['TXT'].append(dict(name=data['name'],ttl=ttl,entry=data['entry']))
        zone.update_one({"owner":owner, "zone":data["zone"]}, { "$set": { "TXT": record['TXT'] } })
    elif data['type'] == 'SRV':
        print("TYPE SRV request")
        print(ttl)
        record['SRV'].append(dict(target=data['target'],ttl=ttl,port=data['port'],weight=data['weight'],priority=data['priority'],protocol=data['protocol']))
        zone.update_one({"owner":owner, "zone":data["zone"]}, { "$set": { "SRV": record['SRV'] } })
    elif data['type'] == 'SPF':
        print("TYPE SPF request")
        record['SPF'].append(dict(name=data['name'],ttl=ttl,entry=data['entry']))
        zone.update_one({"owner":owner, "zone":data["zone"]}, { "$set": { "SPF": record['SPF'] } })
    elif data['type'] == 'SOA':
        print("TYPE SOA request")
        record['SOA'].append(dict(name=data['name'],destination=data['destination']))
        zone.update_one({"owner":owner, "zone":data["zone"]}, { "$set": { "SOA": record['SOA'] } })
    elif data['type'] == 'NS':
        print("TYPE NS request")
        record['NS'].append(dict(name=data['name'],destination=data['destination']))
        zone.update_one({"owner":owner, "zone":data["zone"]}, { "$set": { "NS": record['NS'] } })
    elif data['type'] == 'TTL':
        zone.update_one({"owner":owner, "zone":data["zone"]}, { "$set": { "TTL": { 'base': data['ttl'] } } })
    elif data['type'] == 'managed_zones':
        record['managed_zones'].append(data['managed_zones'])
        zone.update_one({"owner":owner, "zone":data["zone"]}, { "$set": { "managed_zones":  record['managed_zones'] } })
    else:
        print("No type defined")
        return jsonify(status="Error")
    return jsonify(status="Success")

###
### Remove Zone Data
###

def remove(args,username):
    zones = mongo.db.dns_zone
    data = []
    zone = args.get("zone")
    print("Removing entry " + args.get("zone"))
    #owner = session['username']
    owner = username
    #print("Before Printing")
    if args.get("zone"):
        data = zones.find_one({"owner":owner, "zone":zone })
        if data:
            del data['_id']
            if args.get("type") == 'full':
                zones.remove({"owner":owner, "zone":zone})
            else:
                type = args.get("type")
                name =args.get("name")
                update_data = []
                records = zones.find_one({"owner":owner, "zone": zone})
                if type == 'CNAME' or type == 'A' or type == 'AAAA':
                    destination =args.get("destination")
                    for record in records[type]:
                        if not (name == record['name'] and destination == record['destination']):
                            update_data.append(record)
                elif type == 'MX':
                    priority = args.get("priority")
                    for record in records[type]:
                        if not (name == record['name'] ):
                            update_data.append(record)
                elif type == 'TXT':
                    entry = args.get("entry")
                    for record in records[type]:
                        if not (name == record['name'] and entry == record['entry']):
                            update_data.append(record)
                elif type == 'SRV':
                    target = args.get("target")
                    port = args.get("port")
                    weight = args.get("weight")
                    priority = args.get("priority")
                    protocol = args.get("protocol")
                    for record in records[type]:
                        if not (target == record['target'] and port == record['port'] and  weight == record['weight'] and priority == record['priority'] and protocol == record['protocol'] ):
                            update_data.append(record)
                elif type == 'SPF':
                    entry = args.get("entry")
                    for record in records[type]:
                        if not (name == record['name'] and entry == record['entry']):
                            update_data.append(record)
                elif type == 'ROOT_IPv4' or type == 'ROOT_IPv6' or  type == 'managed_zones' :
                    value = args.get("value")
                    for record in records[type]:
                        if not ( value == record ):
                            update_data.append(record)
                records[type] = update_data
                zones.update_one({"owner":owner, "zone":zone}, { "$set": records  })
            return jsonify(status="Success",results=data)
        return jsonify(status="Error")
    return jsonify(status="Error",message="No such zone")


###
### Create Zone Data
###

def create(data,username):
    owner = username
    customer = 'TargetWeb'
    dns = mongo.db.dns_zone
    zone = mongo.db.zone
    organisation = "BetterDevOps"
    soa = ["ns1.webfutur.com", "sysadmin.webfutur.net"]
    ns = ["ns1.webfutur.com", "ns2.webfutur.com"]
    serial = arrow.now().format('YYYYMMDDSS')
    zone_file=data["name"]+".zone"
    managed_zones=[]
    zone.insert(dict(owner=owner,organisation=organisation,customer=customer,managed_zones=managed_zones,main_zone=data["name"],zone_file=zone_file))
    dns.insert(dict(SOA=["ns1.webfutur.com", "sysadmin.webfutur.net"],NS=["ns1.webfutur.com", "ns2.webfutur.com"],managed_zones=managed_zones,customer=customer,main_zone=data["name"],zone_file=zone_file,owner=owner,organisation=organisation,zone=data["name"],ROOT_IPv4=[],ROOT_IPv6=[],TTL=dict(base=300),MX=[],A=[],AAAA=[],CNAME=[],TXT=[],SRV=[], SPF=[]))
    return jsonify(status="Success")


###
### Apply Zone Config 
###

def config_apply(data,username):
    dns = backend.DNS(username)
    zones = mongo.db.dns_zone
    zone  = zones.find_one({"owner":username, "zone":data["zone"]})
    dns.set_user_id()
    del zone['_id']
    templateLoader = jinja2.FileSystemLoader( searchpath="./templates/")
    templateEnv = jinja2.Environment( loader=templateLoader,trim_blocks=True, lstrip_blocks=True )
    ZONE_TEMPLATE_FILE = "template.zone"
    CONF_MASTER_TEMPLATE_FILE = "conf_master_template.tpl"
    CONF_SLAVE_TEMPLATE_FILE = "conf_slave_template.tpl"
    ZONE_INCLUDE_TEMPLATE_FILE = "zone_include.tpl"
    zone_template = templateEnv.get_template(ZONE_TEMPLATE_FILE)
    conf_master_template = templateEnv.get_template(CONF_MASTER_TEMPLATE_FILE)
    conf_slave_template = templateEnv.get_template(CONF_SLAVE_TEMPLATE_FILE)
    zone_include_template = templateEnv.get_template(CONF_SLAVE_TEMPLATE_FILE)
    min_ttl = zone['TTL']['base']
    root_ipv4 = zone['ROOT_IPv4'] 
    root_ipv6 = zone['ROOT_IPv6'] 
    soa = zone['SOA'] 
    ns = zone['NS'] 
    cname_records = zone['CNAME']
    srv_records = zone['SRV']
    spf_records = zone['SPF']
    a_records = zone['A']
    aaaa_records = aaaa_records=zone['AAAA']
    mx_records = zone['MX']
    txt_records = zone['TXT']
    cname_no_ttl = []
    cname_ttl = []
    srv_no_ttl = []
    srv_ttl = []
    for mx_record in cname_records:
        if "." in mx_record['destination']:
            mx_record['destination'] = mx_record['destination'] + "."
        if mx_record['ttl'] == False:
            cname_no_ttl.append(mx_record)    
        else:
           cname_ttl.append(mx_record)
    for srv_record in srv_records:
        if "." in srv_record['target']:
            srv_record['target'] = srv_record['target'] + "."
        if srv_record['ttl'] == False:
            srv_no_ttl.append(srv_record)    
        else:
           srv_ttl.append(srv_record)
    records = []
    ref_ipv6 = []
    for aaaa_record in aaaa_records:
        for a_record in a_records:
            if a_record['name'] == aaaa_record['name']:
                merge = a_record
                if aaaa_record['destination'] not in ref_ipv6:
                    merge['destination_ipv6'] = aaaa_record['destination']
                    ref_ipv6.append(aaaa_record['destination'])
                records.append(merge)
            else:
                records.append(a_record)      
    serial = arrow.now().format('YYYYMMDDHHmmSS')

    zone_file_output = zone_template.render(root_ipv4=root_ipv4,root_ipv6=root_ipv6,min_ttl=min_ttl,soa=soa,ns=ns,serial=serial,cname_no_ttl=cname_no_ttl,cname_ttl=cname_ttl,records=a_records,aaaa_records=aaaa_records,mx_records=mx_records,txt_records=txt_records,spf_records=spf_records,srv_no_ttl=srv_no_ttl,srv_ttl=srv_ttl)
    with open('./output/' + zone["zone_file"], 'w') as f:
        f.write(zone_file_output)
    #backend.transfertZoneFile('ns1.webfutur.com', zone["zone_file"])
    dns.transfertZoneFile(zone["zone_file"])
    managed_domains = zone['managed_zones']
    managed_domains.append(zone["main_zone"])
    ns_server_ipv4 = '91.121.59.230'
    ns_server_ipv6 = '2001:41d0:d:35e2::163'
    conf_master_output = conf_master_template.render(managed_domains=managed_domains, zone_file=zone['zone_file'])
    conf_slave_output = conf_slave_template.render(managed_domains=managed_domains, zone_file=zone['zone_file'], primary_ns_ip_ipv4=ns_server_ipv4, primary_ns_ip_ipv6=ns_server_ipv6)
    with open('./output/' + zone["zone"] + ".conf_master", 'w') as f:
        f.write(conf_master_output)
    with open('./output/' + zone["zone"] + ".conf_slave", 'w') as f:
        f.write(conf_slave_output)
    #backend.transfertConfFile('ns1.webfutur.com', './output/' + zone["zone"] + ".conf_master", zone["zone"] + ".conf")
    #backend.transfertConfFile('ns2.webfutur.com', './output/' + zone["zone"] + ".conf_slave", zone["zone"] + ".conf")
    dns.transfertConfFile('./output/' + zone["zone"] , zone["zone"] + ".conf")
    #dns.transfertConfFile('ns2.webfutur.com', './output/' + zone["zone"] + ".conf_slave", zone["zone"] + ".conf")
    return True

###
### Deploy Zone Config 
###

def config_deploy(username):
    dns = backend.DNS(username)
    dns.set_user_id()
    zones = mongo.db.dns_zone
    all_zones  = zones.find({"owner":username})
    data = []
    for zone in all_zones:
        del zone['_id']
        data.append(zone)
        todeploy = { 'zone':zone['zone'] }
        config_apply(todeploy,username)
    templateLoader = jinja2.FileSystemLoader( searchpath="./templates/")
    templateEnv = jinja2.Environment( loader=templateLoader,trim_blocks=True )
    ZONE_INCLUDE_TEMPLATE_FILE = "zone_include.tpl"
    zone_include_template = templateEnv.get_template(ZONE_INCLUDE_TEMPLATE_FILE)
    zone_include_output = zone_include_template.render(zones=data,config_dir=dns.bind_config_dir)
    with open('./output/' + zone["zone"] + ".conf_include", 'w') as f:
        f.write(zone_include_output)
    dns.transfertIncludeFile( './output/' + zone["zone"] + ".conf_include")
    #ReloadDNS('ns1.webfutur.com')
    #ReloadDNS('ns2.webfutur.com')
    return True



