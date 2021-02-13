# horizen-alert-discord

## Overview
[Horizen](https://www.horizen.io/), née Zencash, is a fork of [Zcash](https://z.cash), which introduces a masternode system 
that incentivizes participants to operate what they call [SecureNodes](https://www.horizen.io/securenodes/) and [SuperNodes](https://www.horizen.io/supernodes/) on the network.

These nodes do not mine, but are incentivized to expose TCP listeners to other users (with valid TLS certs), relay and validate transactions, and also perform a Sprout shielded transaction about once a day.

This script uses the [Horizen Secure Node API](https://securenodes2.na.zensystem.io/about/api) to enumerate any downtimes or exceptions that would exclude your nodes from being paid their rewards, and notifies via a Discord webhook, and is designed to be run from cron or as a cloud function.

![alt text](https://www.horizen.io/assets/img/icons/securenodes.png)

## Gratitude
* Thanks to [@rmeleromira](https://github.com/rmeleromira) for their [ansible-fu which](https://github.com/rmeleromira/ansible-zencash-nodes) makes it easy to deploy and manage an army of these nodes.
* Thanks to the [Zcash team](https://github.com/zcash) for creating Zcash, without which, none of this would be possible.

## Requirements
* Python3
* Discord server with an activated [webhook integration](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)
* [Horizen Secure Node API Key](https://securenodes2.na.zensystem.io/settings/)
* [Horizen Super Node API Key](https://supernodes1.na.zensystem.io/settings/)

## Installation (Linux or OSX)
1. Create a separate user named 'horizen'
```console
sudo adduser horizen
```
2. Change to the 'horizen' user
```console
sudo su - horizen
```

3. Clone the repo
```console
git clone https://github.com/alchemydc/horizen-alert-discord.git
```

4. Create and activate a python virtual environment
(recommended to keep deps separate from system python)
```console
cd horizen-alert-discord
python3 -m venv . && source bin/activate
```

5. Install python dependencies
(requests for making the https API calls, python-dotenv for keeping secrets out of the source)
 ```console
 python -m pip install -r requirements.txt
 ```

## Configuration
1. Copy the environment template
```console
cp .env-template .env
```

2. Populate the .env file with your Horizen API keys and Discord webhook URL.  Note that you can optionally add exception ID's to ignore, as it's not presently possible to tell the API to ignore decommisioned nodes. 


## Test run
```console
python3 zen_monitor.py
```

## Schedule it to run automatically
The included crontab will check your nodes twice a day. Note that this frequency could be increased significantly, but before doing that we'd probably want to add some logic to rate limit the notifications to Discord.

1. Make sure the wrapper bash script and python script is executable
```console
chmod u+x zen_monitor.sh zen_monitor.py
```
2. Install crontab to run script automatically
```console
/usr/bin/crontab zen_monitor.crontab
```

## Troubleshooting
If things aren't working as expected, ensure that your Horizen API key and Discord webhook are set correctly.

If the script works when run directly, but fails when run by cron, check to ensure your home directory is correct in zen_monitor.sh,
and that env vars are being properly imported by python-dotenv.