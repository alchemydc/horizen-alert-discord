#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# constants
SEC_BASE_PATH = 'https://securenodes2.na.zensystem.io/api'
SUP_BASE_PATH = 'https://supernodes2.na.zensystem.io/api'
DOWNTIME_URI = "/nodes/my/downtimes?page=1&rows=100&status=o&key="
EXCEPTION_URI = "/nodes/my/exceptions?page=1&rows=100&status=o&key="

# libs
import requests
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

# read secrets from env vars
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
SEC_KEY = os.getenv('SEC_KEY')
SUP_KEY = os.getenv('SUP_KEY')
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
# API will return 'open' exceptions for long dead nodes, so we ignore those in these lists
SECNODE_IGNORE = json.loads(os.getenv('SECNODE_IGNORE'))
SUPNODE_IGNORE = json.loads(os.getenv('SUPNODE_IGNORE'))

# fcns
def getData(url):
    print("Pulling data from %s" % url)
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
                    'node' : row['fqdn'],
                    'mins down' : row['duration']/60000,    # convert milliseconds to minutes
                    'reason' : row[reasoncode]              # dtype for downtime reason, etype for exception reason
                })
    return(downtime)

def discordAlert(data, uri):
    print("Sending alert data to discord at %s" % (uri))
    http_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    alert_content = ""
    for downtime in data:
        alert_content += downtime['node'] + " has been down for %.0f" % downtime['mins down'] + " mins due to failure of " + downtime['reason'] + "\n"
    payload = {
        #'content': 'Zen Downtime Detected',
        'embeds' : [
            {
            'title': 'Zen Downtime',
            'url': 'https://securenodes2.na.zensystem.io/nodes/mydowns',
            'description': (alert_content[:1997] + "...")   # can't send > 2000 chars to discord, so trimming it here (todo: fixme w/ multiple embeds)
        }]
    }
    print(alert_content)
    response = http.post(uri, headers=http_headers, json=payload)
    print("Discord API returns status: %d" % response.status_code)

def checkNodes(nodeType):       # nodeType == 'secure' || 'super'.
    print("Checking for open %s node downtime" % nodeType)
    if nodeType == "secure":
        data = getData(SEC_BASE_PATH + DOWNTIME_URI + SEC_KEY)
        downtimes = parseData(SECNODE_IGNORE, data, "dtype")
        if downtimes:
            print("Downtimes detected... alerting")
            discordAlert(downtimes, DISCORD_WEBHOOK)
        else:
            print("No downtimes detected.  Keep calm and crypto on.")
    elif nodeType == "super":
        data = getData(SUP_BASE_PATH + DOWNTIME_URI + SUP_KEY)
        downtimes = parseData(SUPNODE_IGNORE, data, "dtype")
        if downtimes:
            print("Downtimes detected... alerting")
            discordAlert(downtimes, DISCORD_WEBHOOK)
        else:
            print("No downtimes detected.  Keep calm and crypto on.")
    print("Checking for open %s node exceptions" % nodeType)
    if nodeType == "secure":
        data = getData(SEC_BASE_PATH + EXCEPTION_URI + SEC_KEY)
        downtimes = parseData(SECNODE_IGNORE, data, "etype")
        if downtimes:
            print("Exceptions detected... alerting")
            discordAlert(downtimes, DISCORD_WEBHOOK)
        else:
            print("No exceptions detected.  Keep calm and crypto on.")
    elif nodeType == "super":
        data = getData(SUP_BASE_PATH + EXCEPTION_URI + SUP_KEY)
        downtimes = parseData(SUPNODE_IGNORE, data, "etype")
        if downtimes:
            print("Exceptions detected... alerting")
            discordAlert(downtimes, DISCORD_WEBHOOK)
        else:
            print("No exceptions detected.  Keep calm and crypto on.")

def main():
    checkNodes("secure")
    checkNodes("super")

if __name__ == "__main__":
    main()