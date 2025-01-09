import boto3

# Initialize AWS clients
apig_client = boto3.client("apigateway")
lambda_client = boto3.client("lambda")
account_id = boto3.client("sts").get_caller_identity()["Account"]

# API Gateway configuration
api_name = "BeyonceDiscographyAPI"
api_stage = "prod"

# Define Lambda function names
get_albums_function_name = "GetAlbums"
get_albums_by_year_function_name = "GetAlbumsByYear"
get_album_summary_function_name = "GetAlbumSummary"

# Construct Lambda ARNs
get_albums_function_arn = (
    f"arn:aws:lambda:{apig_client.meta.region_name}:{account_id}:function:{get_albums_function_name}"
)
get_albums_by_year_function_arn = (
    f"arn:aws:lambda:{apig_client.meta.region_name}:{account_id}:function:{get_albums_by_year_function_name}"
)
get_album_summary_function_arn = (
    f"arn:aws:lambda:{apig_client.meta.region_name}:{account_id}:function:{get_album_summary_function_name}"
)

# Step 1: Create the API Gateway REST API
response = apig_client.create_rest_api(name=api_name)
api_id = response["id"]
print(f"API Gateway created with ID: {api_id}")

# Step 2: Get the root resource ID ("/")
resources = apig_client.get_resources(restApiId=api_id)
base_id = next(item["id"] for item in resources["items"] if item["path"] == "/")
print(f"Root resource ID: {base_id}")

# Step 3: Configure GET /albums (List all albums)
apig_client.put_method(
    restApiId=api_id,
    resourceId=base_id,
    httpMethod="GET",
    authorizationType="NONE",
)
apig_client.put_integration(
    restApiId=api_id,
    resourceId=base_id,
    httpMethod="GET",
    type="AWS_PROXY",
    integrationHttpMethod="POST",
    uri=f"arn:aws:apigateway:{apig_client.meta.region_name}:lambda:path/2015-03-31/functions/{get_albums_function_arn}/invocations",
)
print("GET /albums configured.")

# Step 4: Add a new resource for /albums/year
response = apig_client.create_resource(restApiId=api_id, parentId=base_id, pathPart="year")
year_id = response["id"]
print(f"Resource for /albums/year created with ID: {year_id}")

# Step 5: Configure GET /albums/year (Get albums by year)
apig_client.put_method(
    restApiId=api_id,
    resourceId=year_id,
    httpMethod="GET",
    authorizationType="NONE",
    requestParameters={"method.request.querystring.year": True},  # Require 'year' param
)
apig_client.put_integration(
    restApiId=api_id,
    resourceId=year_id,
    httpMethod="GET",
    type="AWS_PROXY",
    integrationHttpMethod="POST",
    uri=f"arn:aws:apigateway:{apig_client.meta.region_name}:lambda:path/2015-03-31/functions/{get_albums_by_year_function_arn}/invocations",
    requestParameters={"integration.request.querystring.year": "method.request.querystring.year"},
)
print("GET /albums/year configured.")

# Step 6: Add a new resource for /albums/summary
response = apig_client.create_resource(restApiId=api_id, parentId=base_id, pathPart="summary")
summary_id = response["id"]
print(f"Resource for /albums/summary created with ID: {summary_id}")

# Step 7: Configure GET /albums/summary (Get album summary)
apig_client.put_method(
    restApiId=api_id,
    resourceId=summary_id,
    httpMethod="GET",
    authorizationType="NONE",
    requestParameters={"method.request.querystring.title": True},  # Require 'title' param
)
apig_client.put_integration(
    restApiId=api_id,
    resourceId=summary_id,
    httpMethod="GET",
    type="AWS_PROXY",
    integrationHttpMethod="POST",
    uri=f"arn:aws:apigateway:{apig_client.meta.region_name}:lambda:path/2015-03-31/functions/{get_album_summary_function_arn}/invocations",
    requestParameters={"integration.request.querystring.title": "method.request.querystring.title"},
)
print("GET /albums/summary configured.")

# Step 8: Deploy the API
apig_client.create_deployment(restApiId=api_id, stageName=api_stage)
print(f"API deployed to stage: {api_stage}")
