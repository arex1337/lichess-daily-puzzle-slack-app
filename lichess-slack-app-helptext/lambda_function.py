import json
import hashlib
import hmac
import base64
from time import time
import os

def verify_slack_signature(slack_post_request, slack_signing_secret, body):
    slack_signing_secret = bytes(slack_signing_secret, 'utf-8')
    slack_signature = slack_post_request['headers']['x-slack-signature']
    slack_request_timestamp = slack_post_request['headers']['x-slack-request-timestamp']
    basestring = f"v0:{slack_request_timestamp}:{body}".encode('utf-8')
    my_signature = 'v0=' + hmac.new(slack_signing_secret, basestring, hashlib.sha256).hexdigest()
    return hmac.compare_digest(my_signature, slack_signature)
    
def lambda_handler(event, context):
    
    query_string = str(base64.b64decode(event['body']), encoding='utf-8')
    
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
    
    # Successful response
    response = {
       "response_type": "in_channel",
       "text": "Here's how you can use the 'Daily Chess Puzzles by Lichess' app",
       "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "By default, the 'Daily Chess Puzzles by Lichess' app will post a chess puzzle from Lichess to the channel in which it was installed every day (same time of day it was installed). Use the */puzzletime* command to change this setting, e.g. */puzzletime 14:45*. To post the daily puzzle on demand, use the */puzzle* command."
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
