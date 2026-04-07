import boto3
import requests
import json
from requests_aws4auth import AWS4Auth

region = "us-east-1"
service = "es"

credentials = boto3.Session().get_credentials()

awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token
)

host = "https://search-genai-knowledge-base-sg4ij5qc65n6qqa2i5gviiqqmi.us-east-1.es.amazonaws.com"

bedrock = boto3.client("bedrock-runtime", region_name=region)

def get_embedding(text):
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        body=json.dumps({"inputText": text})
    )
    result = json.loads(response['body'].read())
    return result['embedding']

query_text = "high demand product"

embedding = get_embedding(query_text)

query = {
    "size": 3,
    "query": {
        "knn": {
            "embedding": {
                "vector": embedding,
                "k": 3
            }
        }
    }
}

response = requests.get(
    f"{host}/products/_search",
    auth=awsauth,
    json=query
)

print("Status:", response.status_code)
print("Response:", response.text)
