#!/usr/bin/env python3

import argparse
import pypandoc
import yaml
import re
from getpass import getpass
from pathlib import Path
from paramiko import SSHClient, AutoAddPolicy, Ed25519Key, ed25519key, SFTPClient

def getArgs():

    parser = argparse.ArgumentParser(
            prog = "oskhen-deploy",
            description = "Publishes input (md) file to oskhen-website",
            epilog = "Input e.g \n deploy file.md --project 'dailies' --section 'December 2024'")
    
    parser.add_argument('filename')
    parser.add_argument('-p', '--project', required=True)
    parser.add_argument('-s', '--section')
    parser.add_argument('-c', '--config', default='config.yml')
    
    args = parser.parse_args()
    return args

def createHTML(f):

    title = Path(f).stem
    
    metadata = { 'title': title }
    metadata_string = "--metadata pagetitle={title}".format(**metadata).split(" ") 

    pandoc_args = ["-s", "-M", "document-css=false"] + metadata_string

    output = pypandoc.convert_file(f, "html", format='md', extra_args=pandoc_args) 
    HTML = re.sub(r"(<style>([\s\S]*)<\/style>)", "", output) #strips output from css

    return HTML

def parseConfig(f):

    config = yaml.safe_load(open(f))
    return config

def deploy(config, f, args):

    local = config['local']
    server = config['server']

    keyfile_password = getpass(f"Input password for encrypted keyfile {local['KEYFILE']}: ")

    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(server['HOST'], port=server['PORT'], username=server['USER'], pkey=Ed25519Key.from_private_key_file(local['KEYFILE'], keyfile_password)) 


if __name__ == "__main__":
    
    args = getArgs()
    HTML = createHTML(args.filename)
    config = parseConfig(args.config)
    deploy(config, HTML, args)
    


