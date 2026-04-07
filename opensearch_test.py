import requests
from requests_aws4auth import AWS4Auth
import boto3
import json

region = "us-east-1"
service = "es"

host = "https://search-genai-knowledge-base-sg4ij5qc65n6qqa2i5gviiqqmi.us-east-1.es.amazonaws.com"

credentials = boto3.Session().get_credentials()

awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token
)

# ---------------- STEP 1: CREATE INDEX ----------------
index_name = "products"

create_index_response = requests.put(
    f"{host}/{index_name}",
    auth=awsauth,
    json={
        "settings": {
            "index": {"number_of_shards": 1}
        },
        "mappings": {
            "properties": {
                "content": {"type": "text"}
            }
        }
    }
)

print("CREATE INDEX:", create_index_response.text)


# ---------------- STEP 2: INSERT DATA ----------------
doc = {
    "content": "Product p2 has high demand and low stock risk"
}

insert_response = requests.post(
    f"{host}/{index_name}/_doc?refresh=true",
    auth=awsauth,
    json=doc
)

print("INSERT DATA:", insert_response.text)


# ---------------- STEP 3: SEARCH DATA ----------------
query = {
    "query": {
        "match": {
            "content": "p2 demand"
        }
    }
}

search_response = requests.get(
    f"{host}/{index_name}/_search",
    auth=awsauth,
    json=query
)

print("SEARCH RESULT:", search_response.text)
