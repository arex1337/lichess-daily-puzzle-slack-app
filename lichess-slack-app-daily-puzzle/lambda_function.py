import json
import os
import requests
import base64
import urllib.parse
import boto3
from time import gmtime, strftime
from datetime import datetime

def lambda_handler(event, context):
    
    # Get the daily puzzle
    r = requests.get('https://lichess.org/training/daily', headers={'Accept': 'application/vnd.lichess.v5+json'})
    c = r.content
    o = json.loads(c)
    url = "https://lichess.org/training/" + str(o['puzzle']['id'])
    imgurl = "https://lichess.org/training/export/png/" + str(o['puzzle']['id']) + ".png"
    
    # Broadcast
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = dynamodb.Table('LichessSlackAppInstallations')
    response = table.scan()
    for i in response['Items']:
        if 'last_executed' not in i:
            i['last_executed'] = "2008-01-01 00:00:00"
        preferred_time = datetime.strptime(strftime("%Y-%m-%d "+i['preferred_time'], gmtime()), '%Y-%m-%d %H:%M')
        last_executed = datetime.strptime(i['last_executed'], '%Y-%m-%d %H:%M:%S')
        if datetime.strptime(strftime("%Y-%m-%d %H:%M", gmtime()), '%Y-%m-%d %H:%M') >= preferred_time and last_executed < preferred_time:
            print("Will post to " + i['object']['team']['id'] + " - " + i['object']['incoming_webhook']['channel_id'])
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