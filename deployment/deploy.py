#!/usr/bin/env python3

import argparse
import pypandoc
import yaml
import re
import time
from getpass import getpass
from random import randint
from io import BytesIO
from pathlib import Path
from paramiko import SSHClient, AutoAddPolicy, Ed25519Key
from datetime import datetime
import shlex

def getArgs():

    parser = argparse.ArgumentParser(
            prog = "oskhen-deploy",
            description = "Publishes input (md) file to oskhen-website",
            epilog = "Input e.g \n deploy file.md --project 'dailies' --section 'December 2024'")
    
    parser.add_argument('filename')
    parser.add_argument('-p', '--project', required=True)
    parser.add_argument('-s', '--section')
    parser.add_argument('-d', '--date', help="eg. '240903 21:00' - all parts are optional")
    parser.add_argument('-c', '--config', default='config.yml')
    
    args = parser.parse_args()
    return args

def createHTML(f):

    title = Path(f).stem
    
    metadata = { 'title': title }
    metadata_string = shlex.split("--metadata pagetitle='{title}'".format(**metadata))

    pandoc_args = ["-s", "-M", "document-css=false"] + metadata_string

    output = pypandoc.convert_file(f, "html", format='md', extra_args=pandoc_args) 
    HTML = re.sub(r"(<style>([\s\S]*)<\/style>)", "", output) #strips output from css

    return HTML

def parseConfig(f):

    config = yaml.safe_load(open(f))
    return config

def getClientSession(config):

    local = config['local']
    server = config['server']

    keyfile_password = getpass(f"Enter passphrase for key '{local['KEYFILE']}': ")

    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(server['HOST'], port=server['PORT'], username=server['USER'], pkey=Ed25519Key.from_private_key_file(local['KEYFILE'], keyfile_password)) 

    return client

def parseTime(date):
    if " " not in date:
        date += " 12:00:00"
    elif ":" not in date:
        date += ":00:00"
    elif date.count(":") != 2:
        date += ":00"

    obj = datetime.strptime(date, "%y%m%d %H:%M:%S")
    return int(obj.timestamp())


def getSQLCommand(root, args):

    id = randint(1, 2**32)

    date = int(time.time())
    if args.date:
        date = parseTime(args.date)

    title = Path(args.filename).stem
    section = str(args.section or '')
    viewcount = 0

    db = f"{root}/{args.project}/entries.db"

    # SQL injection?
    statement = f"INSERT INTO entries (id, date, title, section, viewcount) VALUES ({id}, {date}, \'{title}\', \'{section}\', {viewcount});"
    execution = f"sqlite3 {db} \"{statement}\""

    return execution


def deploy(config, f, args):

    root = config['server']['ROOT']
    filename = Path(args.filename).stem + ".html"
    section = str(args.section or '')

    remote_path = root + f"/{args.project}/entries/{section}/{filename}"


    with getClientSession(config) as client:

        with client.open_sftp() as sftp:
            sftp.putfo(BytesIO(f.encode()), remote_path)
   
        sql_command = getSQLCommand(root, args) 
        client.exec_command(sql_command)

if __name__ == "__main__":
    
    args = getArgs()
    HTML = createHTML(args.filename)
    config = parseConfig(args.config)
    deploy(config, HTML, args)
    


