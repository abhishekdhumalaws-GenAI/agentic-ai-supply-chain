import json
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")


def invoke_model(model_name, user_input):

    if model_name == "nova":
        return invoke_nova(user_input)

    elif model_name == "claude":
        return invoke_claude(user_input)

    else:
        raise Exception("Unsupported model")


# 🔥 Nova Implementation
def invoke_nova(user_input):

    response = bedrock.invoke_model(
        modelId="amazon.nova-lite-v1:0",
        body=json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"text": f"You are a supply chain AI agent. {user_input}"}
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 800,
                "temperature": 0.5,
		"topP": 0.9
            }
        })
    )

    result = json.loads(response['body'].read())

    try:
	    output_text = result['output']['message']['content'][0]['text']
    except (KeyError, IndexError, TypeError):
	    output_text = "Error: Unable to parse model response"

    return output_text

# 🔥 Claude (future use)
def invoke_claude(user_input):

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [
                {"role": "user", "content": user_input}
            ],
            "max_tokens": 300
        })
    )

    result = json.loads(response['body'].read())
    return result
