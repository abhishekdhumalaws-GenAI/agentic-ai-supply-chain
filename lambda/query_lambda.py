import json
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table("supply_chain_results")


def lambda_handler(event, context):

    user_query = event.get("query")

    # 🔥 Prompt for AI
    prompt = f"""
You are a query translator.

Convert user question into JSON query.

Schema:
{{
  "product_id": "...",
  "warehouse": "...",
  "action": "get_latest | get_all"
}}

User question:
{user_query}

Return ONLY JSON.
"""

    response = bedrock.invoke_model(
        modelId="amazon.nova-lite-v1:0",
        body=json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 300,
                "temperature": 0
            }
        })
    )

    result = json.loads(response['body'].read())

    ai_output = result['output']['message']['content'][0]['text']

    print("AI Output:", ai_output)

    try:
        query_json = json.loads(ai_output)
    except:
        return {
            "statusCode": 400,
            "body": "Failed to parse AI response"
        }

    # 🔍 Build DynamoDB query
    if query_json.get("action") == "get_latest":
        response = table.query(
            KeyConditionExpression="product_id = :p",
            ExpressionAttributeValues={
                ":p": query_json["product_id"]
            },
            ScanIndexForward=False,
            Limit=1
        )
    else:
        response = table.scan()

    return {
        "statusCode": 200,
        "body": json.dumps(response["Items"])
    }
