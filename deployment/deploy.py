#!/usr/bin/env python3

import argparse
import pypandoc
import re
from pathlib import Path

def getArgs():

    parser = argparse.ArgumentParser(
            prog = "oskhen-deploy",
            description = "Publishes input (md) file to oskhen-website",
            epilog = "Input e.g \n deploy add file.md --project 'dailies' --section 'December 2024'")
    
    parser.add_argument('filename')
    parser.add_argument('-p', '--project', required=True)
    parser.add_argument('-s', '--section')
    
    args = parser.parse_args()
    return args

def createHTML(f):

    title = Path(f).stem

    metadata = ["--metadata", f"pagetitle={title}"]
    pandoc_args = ["-s", "-M", "document-css=false"] + metadata

    output = pypandoc.convert_file(f, "html", format='md', extra_args=pandoc_args) 
    HTML = re.sub(r"(<style>([\s\S]*)<\/style>)", "", output) #strips output from css

    return HTML


if __name__ == "__main__":
    
    args = getArgs()
    print(createHTML(args.filename))


