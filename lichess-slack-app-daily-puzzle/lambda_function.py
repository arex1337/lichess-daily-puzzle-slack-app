import json
import os
import requests
import base64
import urllib.parse
import boto3
from botocore.config import Config
from time import gmtime, strftime
from datetime import datetime
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

def lambda_handler(event, context):
    
    # Get the daily puzzle
    r = requests.get('https://lichess.org/training/daily', headers={'Accept': 'application/vnd.lichess.v5+json'})
    c = r.content
    o = json.loads(c)
    url = "https://lichess.org/training/" + str(o['puzzle']['realId'])
    imgurl = "https://lichess1.org/training/export/gif/thumbnail/" + str(o['puzzle']['realId']) + ".gif"
    
    # Broadcast
    config = Config(
        connect_timeout=0.7, 
        read_timeout=0.7,
        retries={'max_attempts': 3}
    )
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-3', config=config)
    table = dynamodb.Table('LichessSlackAppInstallations')
    response = table.scan()
    for i in response['Items']:
        if 'last_executed' not in i:
            i['last_executed'] = "2008-01-01 00:00:00"
        preferred_time = datetime.strptime(strftime("%Y-%m-%d "+i['preferred_time'], gmtime()), '%Y-%m-%d %H:%M')
        last_executed = datetime.strptime(i['last_executed'], '%Y-%m-%d %H:%M:%S')
        if datetime.strptime(strftime("%Y-%m-%d %H:%M", gmtime()), '%Y-%m-%d %H:%M') >= preferred_time and last_executed < preferred_time:
            # Log execution to DB
            keys = {
                'team_id': i['object']['team']['id'],
                'channel_id': i['object']['incoming_webhook']['channel_id']
            }
            response = table.update_item(
                Key = keys,
                UpdateExpression="set last_executed = :l",
                ExpressionAttributeValues = {
                    ':l': strftime("%Y-%m-%d %H:%M:%S", gmtime())
                },
                ReturnValues="UPDATED_NEW"
            )
            
            # Post to channel
            print("Posting to " + i['object']['team']['id'] + " - " + i['object']['incoming_webhook']['channel_id'])
            slack_data = {
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
            requests.post(i['object']['incoming_webhook']['url'], data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})

        else:
            print("Will not post to " + i['object']['team']['id'] + " - " + i['object']['incoming_webhook']['channel_id'])
    return {
        "statusCode": 200,
        "statusDescription": "200 OK",
        "isBase64Encoded": False,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": ""
    }
