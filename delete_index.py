import boto3
import requests
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

response = requests.delete(f"{host}/products", auth=awsauth)

print(response.status_code)
print(response.text)
