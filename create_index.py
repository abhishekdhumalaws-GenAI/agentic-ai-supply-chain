import boto3
import requests
from requests_aws4auth import AWS4Auth
import json

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

index_body = {
    "settings": {
        "index": {
            "knn": True
        }
    },
    "mappings": {
        "properties": {
            "content": {"type": "text"},
            "embedding": {
                "type": "knn_vector",
                "dimension": 1536
            }
        }
    }
}

response = requests.put(
    f"{host}/products",
    auth=awsauth,
    headers={"Content-Type": "application/json"},
    data=json.dumps(index_body)
)

print(response.status_code)
print(response.text)
