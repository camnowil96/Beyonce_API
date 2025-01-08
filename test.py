import boto3

apigateway_client = boto3.client("apigateway")
response = apigateway_client.create_rest_api(name="test-api")
print(response)
