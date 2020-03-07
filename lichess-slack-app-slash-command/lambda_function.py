import json
import os
import slack
import requests
import base64
import urllib.parse
import hashlib
import hmac
from time import time

def verify_slack_signature(slack_post_request, slack_signing_secret, body):
    slack_signing_secret = bytes(slack_signing_secret, 'utf-8')
    slack_signature = slack_post_request['headers']['x-slack-signature']
    slack_request_timestamp = slack_post_request['headers']['x-slack-request-timestamp']
    basestring = f"v0:{slack_request_timestamp}:{body}".encode('utf-8')
    my_signature = 'v0=' + hmac.new(slack_signing_secret, basestring, hashlib.sha256).hexdigest()
    return hmac.compare_digest(my_signature, slack_signature)

def lambda_handler(event, context):
    query_string = str(base64.b64decode(event['body']), encoding='utf-8')
    dict = urllib.parse.parse_qs(query_string)

    # Protect against replay attacks
    if int(time()) - int(event['headers']['x-slack-request-timestamp']) > 60 * 5:
        return {
            "statusCode": 401,
            "statusDescription": "401 Unauthorized",
            "isBase64Encoded": False,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": ""
        }
    
    # Verify the request is coming from Slack
    slack_signing_secret = os.environ['slack_signing_secret']
    if verify_slack_signature(event, slack_signing_secret, query_string):
        print('signature verified')
    else:
        return {
            "statusCode": 401,
            "statusDescription": "401 Unauthorized",
            "isBase64Encoded": False,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": ""
        }
    
    # Identify the daily puzzle and respond
    r = requests.get('https://lichess.org/training/daily', headers={'Accept': 'application/vnd.lichess.v5+json'})
    o = json.loads(r.content)
    url = "https://lichess.org/training/" + str(o['puzzle']['id'])
    imgurl = "https://lichess.org/training/export/png/" + str(o['puzzle']['id']) + ".png"
    response = {
       "response_type": "in_channel",
       "text": url,
       "blocks": [
            {
              "type": "image",
              "title": {
                 "type": "plain_text",
                 "text": imgurl
              },          
              "image_url": imgurl,
              "alt_text": "A chess puzzle from lichess.org"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": url
                }
            }
        ]
    } 
    return {
        "statusCode": 200,
        "statusDescription": "200 OK",
        "isBase64Encoded": False,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(response)
    }