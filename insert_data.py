import json
import boto3
import requests
from requests_aws4auth import AWS4Auth

# ---------------- AWS SETUP ----------------
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

# ---------------- BEDROCK CLIENT ----------------
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def get_embedding(text):
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        body=json.dumps({"inputText": text})
    )

    result = json.loads(response['body'].read())
    return result['embedding']


# ---------------- SAMPLE DATA ----------------
documents = [
    "Product p1 has stable demand and medium inventory",
    "Product p2 has high demand and risk of stockout",
    "Product p3 has low demand and excess inventory",
    "Reorder when stock falls below safety level",
    "High demand products require frequent restocking"
]


# ---------------- INSERT DATA ----------------
for doc in documents:

    embedding = get_embedding(doc)

    data = {
        "content": doc,
        "embedding": embedding
    }

    response = requests.post(
        f"{host}/products/_doc",
        auth=awsauth,
        json=data
    )

    print(response.text)
