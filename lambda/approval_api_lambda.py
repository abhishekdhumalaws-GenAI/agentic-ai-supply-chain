import json
import boto3
import urllib.parse

sf = boto3.client('stepfunctions')

def lambda_handler(event, context):

    print("EVENT:", json.dumps(event))

    try:
        # ✅ Extract token safely
        token = None

        if event.get("queryStringParameters"):
            token = event["queryStringParameters"].get("token")

        if not token:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing token"})
            }

        # ✅ Decode token (IMPORTANT)
        token = urllib.parse.unquote(token)

        # ✅ Resume Step Function
        sf.send_task_success(
            taskToken=token,
            output=json.dumps({"approved": True})
        )

        return {
            "statusCode": 200,
            "body": "✅ Approved successfully! You can close this page."
        }

    except Exception as e:
        print("ERROR:", str(e))

        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
