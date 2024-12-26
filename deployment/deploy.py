#!/usr/bin/env python3

import argparse

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


if __name__ == "__main__":
    
    args = getArgs()
    print(vars(args))


