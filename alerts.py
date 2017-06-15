import requests
import logging
import json
import sys
from urllib import parse
from akamai.edgegrid import EdgeGridAuth
import boto3
import os

section_name = "alerts"
session = requests.Session()
slackSession = requests.Session()

# Slack setup
SLACK_CHANNEL = os.environ['slackChannel']
HOOK_URL = os.environ['slackUrl']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

print ("Setting up function now")

# Use environment variables for credential management
env_prefix = '_'.join(['AKAMAI', section_name.upper()])
env = {}
for token in ('CLIENT_TOKEN', 'CLIENT_SECRET', 'ACCESS_TOKEN', 'HOST'):
    env_string = '_'.join([env_prefix, token])
    if env_string not in os.environ:
        print ("Need to set environment variables: %s" % env_string)
        continue
    env[token] = os.environ[env_string]

if len(env) < 4:
    exit(0)

# Setup session authentication for Akamai's API 
session.auth = EdgeGridAuth(
	client_token=env['CLIENT_TOKEN'],
	client_secret=env['CLIENT_SECRET'],
	access_token=env['ACCESS_TOKEN']
)

baseurl = '%s://%s/' % ('https', env['HOST'])

def handler(event, context):
	alert_result = session.get(parse.urljoin(
		baseurl, '/alerts/v2/alert-firings/active'))
	print (alert_result.text)
	alert_obj = json.loads(alert_result.text)
	data = alert_obj["data"]
	if len(data) < 1:
		return env

	slack_message = {
		'channel': SLACK_CHANNEL,
		'text': "%s" % (alert_result.text)
	}
	slack_result = slackSession.post(HOOK_URL, data=json.dumps(slack_message))
	logger.info("Message posted to %s: %s",
		slack_message['channel'], slack_result.text)
	return(env)
