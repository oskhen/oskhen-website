#!/usr/bin/env python3

# Input: path to .md file
# Convert to .html - output in html folder
# Move through ssh copy to raspberry pi /blog folder - rename as appropriate
# Update Index
# later also fix css

import subprocess
from paramiko import SSHClient, AutoAddPolicy, Ed25519Key
from scp import SCPClient
from getpass import getpass
import sys
import os
from random import randint
import time
from datetime import datetime

HOST = "94.254.87.132"
PORT = 7777
USER = 'dietpi'
HOME = os.environ['HOME']
outputFolder = HOME + "/Documents/pkm/html" # Do I really need to save this?

def getTimeStamp(date):

    if " " not in date:
        date += " 12:00:00"
    elif ":" not in date:
        date += ":00:00"
    elif date.count(":") != 2:
        date += ":00"

    obj = datetime.strptime(date, "%y%m%d %H:%M:%S")
    return int(obj.timestamp())


def createHTML(f):
    
    if f[-3:] != ".md":
        print(".md file required!")
        exit(1)

    inFile = f
    title = f[:-3].split("/")[-1]

    outFile = f"{outputFolder}/{title}.html"

    command = ["pandoc", "-s", inFile, "-o", outFile, "--metadata", f"pagetitle={title}", "-M", "document-css=false"]
    x = subprocess.run(command, capture_output=True)
    
    if x.returncode != 0:
        print(x.stderr)
        exit(1)
    
    return outFile

def deployToPi(file, PASS, section="", date=0):

    currentTime = int(time.time())

    if date:
        stamp = getTimeStamp(date)
    else:
        stamp = currentTime
    
    name = file.split("/")[-1]
    blogHome = "/var/www/oskhen/blog"
    BLOG_PATH = f"{blogHome}/blogentries/{section}/"
    DAILIES_PATH = f"{blogHome}/dailies/entries/"


    section = f'"{section}"' #OBS SEE FNUTTAR

    id = randint(1, 2**32)
    title = f'"{name.removesuffix(".html")}"'

    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USER, pkey=Ed25519Key.from_private_key_file(f"{HOME}/.ssh/id_ed25519", PASS))

    client.exec_command(f"mkdir -p '{DAILIES_PATH}'")

    with SCPClient(client.get_transport()) as scp:
        scp.put(file, DAILIES_PATH+name)

    COMMAND_JOURNALS = f"sqlite3 {blogHome}/blog.db 'INSERT INTO blogentries (id, written_date, title, section, upload_date) VALUES ({id}, {stamp}, {title}, {section}, {currentTime})'"
    COMMAND_DAILIES = f"sqlite3 {blogHome}/dailies/dailies.db 'INSERT INTO entries (id, date, title, viewcount) VALUES ({id}, {currentTime}, {title}, 0)'"
    client.exec_command(COMMAND_DAILIES) #OBS SEE FNUTTAR
    
    client.close()

if __name__ == "__main__":

    PASS = getpass("Password: ")
    file = sys.argv[1]
    #section = sys.argv[2]
    #date = ""
    #if len(sys.argv) == 5:
    #    if sys.argv[3] == "--date":
    #        date = sys.argv[4]
    output = createHTML(file)
    #deployToPi(output, section, PASS, date)
    deployToPi(output, PASS)
