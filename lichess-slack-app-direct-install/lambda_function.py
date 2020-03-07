import json
import os

def lambda_handler(event, context):
    client_id = os.environ['client_id']
    scopes = "commands incoming-webhook"
    redirect_uri = "https://lichess-slack-app.org/lambda/lichess-slack-app-authorize"

    return {
        "statusCode": 302,
        "statusDescription": "302 Found",
        "isBase64Encoded": False,
        "headers": {
            "Location": "https://slack.com/oauth/v2/authorize?client_id=" + client_id + "&scope=" + scopes + "&redirect_uri=" + redirect_uri #+ state + team
        },
        "body": ""
    }