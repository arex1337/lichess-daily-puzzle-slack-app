import json
import requests
import boto3
from botocore.config import Config
import sys
from time import gmtime, strftime
import base64
import os

def lambda_handler(event, context):
    # Exchanging a temporary authorization code for an access token
    query_string = str(base64.b64decode(event['body']), encoding='utf-8')
    r = requests.post('https://slack.com/api/oauth.v2.access', data={'client_id': os.environ['client_id'], 'client_secret': os.environ['client_secret'], 'code': event['queryStringParameters']['code'], 'redirect_uri': 'https://lichess-slack-app.org/lambda/lichess-slack-app-authorize'})
    o = json.loads(r.content)
    
    # Persisting installation information
    config = Config(
        connect_timeout=2, 
        read_timeout=2,
        retries={'max_attempts': 3}
    )
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1', config=config)
    table = dynamodb.Table('LichessSlackAppInstallations')
    response = table.put_item(
       Item = {
            'team_id': o['team']['id'],
            'channel_id': o['incoming_webhook']['channel_id'],
            'webhook_url': o['incoming_webhook']['url'],
            'object': o,
            'preferred_time': strftime("%H:%M", gmtime())
        }
    )
    
    return {
        "statusCode": 200,
        "statusDescription": "200 OK",
        "isBase64Encoded": False,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": "You've successfully installed Daily Chess Puzzle by Lichess! You can close this window."
    }