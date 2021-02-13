#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# constants
SEC_BASE_PATH         = 'https://securenodes2.na.zensystem.io/api'
SUP_BASE_PATH         = 'https://supernodes2.na.zensystem.io/api'
DOWNTIME_URI          = "/nodes/my/downtimes?page=1&rows=100&status=o&key="
EXCEPTION_URI         = "/nodes/my/exceptions?page=1&rows=100&status=o&key="
DISCORD_AVATAR        = "https://winklevosscapital.com/wp-content/uploads/2020/04/Jane-Profile.jpg"
DISCORD_NICK          = "3jane"
SEC_DETAIL_URI_BASE   = "https://securenodes2.na.zensystem.io/nodes/"
SUP_DETAIL_URI_BASE   = "https://supernodes1.na.zensystem.io/nodes/"
DETAIL_URI_SUFFIX     = "/detail"


# libs
import requests
from requests_toolbelt.utils import dump
import json
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# create a custom requests object, modifying the global module throws an error
# provides intrinic exception handling for requests without try/except
http = requests.Session()
assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
http.hooks["response"] = [assert_status_hook]

# dump verbose request and response data to stdout
def logging_hook(response, *args, **kwargs):
    data = dump.dump_all(response)
    print(data.decode('utf-8'))

#setup Requests to log request and response to stdout verbosely
#http.hooks["response"] = [logging_hook]

# read secrets from env vars
env_path                = Path('.') / '.env'
load_dotenv(dotenv_path = env_path)
SEC_KEY                 = os.getenv('SEC_KEY')
SUP_KEY                 = os.getenv('SUP_KEY')
DISCORD_WEBHOOK         = os.getenv('DISCORD_WEBHOOK')
# API will return 'open' exceptions for long dead nodes, so we ignore those in these lists
SECNODE_IGNORE          = json.loads(os.getenv('SECNODE_IGNORE'))
SUPNODE_IGNORE          = json.loads(os.getenv('SUPNODE_IGNORE'))

# fcns
def getData(url):
    #print("Pulling data from %s" % url)
    response = http.get(url)
    return(response.json())

def parseData(ignoredIDs, data, reasoncode):
    if data['records'] == 0:
        return False
    else:
        downtime = []
        for row in data['rows']:
            if row['id'] not in ignoredIDs:                 # exclude downtime & exception ID's for dead/zombie hosts
                downtime.append({
                    'node'      : row['fqdn'],
                    'nodeID'    : row['nid'],
                    'mins down' : row['duration']/60000,    # convert milliseconds to minutes
                    'reason'    : row[reasoncode]           # dtype for downtime reason, etype for exception reason
                })
    return(downtime)

def checkNodes(nodeType):  # nodeType == 'secure' || 'super'.
    print("Checking for open %s node downtime" % nodeType)
    if nodeType == "secure":
        detail_uri = SEC_DETAIL_URI_BASE
        data = getData(SEC_BASE_PATH + DOWNTIME_URI + SEC_KEY)
        downtimes = parseData(SECNODE_IGNORE, data, "dtype")
        if downtimes:
            print("Downtimes detected... alerting")
            discordEmbed(downtimes, DISCORD_WEBHOOK, detail_uri)
        else:
            print("No downtimes detected.  Keep calm and crypto on.")
    elif nodeType == "super":
        detail_uri = SUP_DETAIL_URI_BASE
        data = getData(SUP_BASE_PATH + DOWNTIME_URI + SUP_KEY)
        downtimes = parseData(SUPNODE_IGNORE, data, "dtype")
        if downtimes:
            print("Downtimes detected... alerting")
            discordEmbed(downtimes, DISCORD_WEBHOOK, detail_uri)
        else:
            print("No downtimes detected.  Keep calm and crypto on.")
    print("Checking for open %s node exceptions" % nodeType)
    if nodeType == "secure":
        detail_uri = SEC_DETAIL_URI_BASE
        data = getData(SEC_BASE_PATH + EXCEPTION_URI + SEC_KEY)
        downtimes = parseData(SECNODE_IGNORE, data, "etype")
        if downtimes:
            print("Exceptions detected... alerting")
            discordEmbed(downtimes, DISCORD_WEBHOOK, detail_uri)
        else:
            print("No exceptions detected.  Keep calm and crypto on.")
    elif nodeType == "super":
        detail_uri = SUP_DETAIL_URI_BASE
        data = getData(SUP_BASE_PATH + EXCEPTION_URI + SUP_KEY)
        downtimes = parseData(SUPNODE_IGNORE, data, "etype")
        if downtimes:
            print("Exceptions detected... alerting")
            discordEmbed(downtimes, DISCORD_WEBHOOK, detail_uri)
        else:
            print("No exceptions detected.  Keep calm and crypto on.")

def discordEmbed(data, discord_uri, detail_uri):
    print("Sending alert data to discord at %s" % (discord_uri))
    http_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    for downtime in data:
        description = "has been down for %.0f" % downtime['mins down'] + " mins due to failure of " + downtime['reason']
        full_node_detail_uri = detail_uri + str(downtime['nodeID']) + DETAIL_URI_SUFFIX
        payload = {
            "username": DISCORD_NICK,
            "avatar_url": DISCORD_AVATAR,

            "embeds": [
                {
                    "author": 
                        {
                            "name"      : downtime['node'],
                            "url"       : full_node_detail_uri,
                            "icon_url"  : "https://www.worldcryptoindex.com/wp-content/uploads/2018/10/horizen-logo.jpg"
                        },            

                    "title"      : downtime['node'],
                    "url"        : full_node_detail_uri,
                    "description": description,
                    "color"      :  15258703,
                    "thumbnail"  :
                        {
                            "url": "https://example.com"
                        },
                }
            ]
        }
        response = http.post(discord_uri, headers=http_headers, json=payload)
        #print(response.content)

def main():
    checkNodes("secure")
    checkNodes("super")

if __name__ == "__main__":
    main()