import json
import boto3
from urllib.parse import quote

sns = boto3.client('sns')

TOPIC_ARN = "arn:aws:sns:us-east-1:623593083974:supply-chain-alerts"
API_URL = "https://jhlbzdzfid.execute-api.us-east-1.amazonaws.com/approve"   # 🔥 update later

def lambda_handler(event, context):

    print("Approval Needed:", json.dumps(event))

    token = event["token"]
    data = event["input"]

    # 🔥 Create approval link
    encoded_token = quote(token)

    approve_link = f"{API_URL}?token={encoded_token}"

    message = f"""
    🚨 Approval Required

    Click below to approve:

    {approve_link}

    Data:
    {json.dumps(data, indent=2)}
    """

    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject="Approval Required",
        Message=message
    )

    return {"status": "waiting_for_approval"}
