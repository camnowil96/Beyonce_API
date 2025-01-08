import boto3

def create_api_gateway():
    # Initialize the clients
    apigateway_client = boto3.client('apigatewayv2')
    lambda_client = boto3.client('lambda')
    region = "us-east-1"  # Your AWS region
    aws_account_id = "051826710466"  # Your AWS account ID

    # Create the API Gateway
    api_name = "BeyonceAlbumsAPI"
    api = apigateway_client.create_api(
        Name=api_name,
        ProtocolType='HTTP'
    )
    api_id = api['ApiId']
    print(f"Created API Gateway with ID: {api_id}")

    # Define Lambda function ARNs (replace with your actual Lambda function ARNs)
    get_albums_arn = "arn:aws:lambda:us-east-1:051826710466:function:GetAlbums"
    get_albums_by_year_arn = "arn:aws:lambda:us-east-1:051826710466:function:GetAlbumsByYear"
    get_album_summary_arn = "arn:aws:lambda:us-east-1:051826710466:function:GetAlbumSummary"

    # Set up integrations
    def create_integration(function_arn):
        return apigateway_client.create_integration(
            ApiId=api_id,
            IntegrationType='AWS_PROXY',
            IntegrationUri=function_arn,
            PayloadFormatVersion='2.0'
        )['IntegrationId']

    get_albums_integration_id = create_integration(get_albums_arn)
    get_albums_by_year_integration_id = create_integration(get_albums_by_year_arn)
    get_album_summary_integration_id = create_integration(get_album_summary_arn)

    # Add routes
    def create_route(route_key, integration_id):
        apigateway_client.create_route(
            ApiId=api_id,
            RouteKey=route_key,
            Target=f'integrations/{integration_id}'
        )

    create_route('GET /albums', get_albums_integration_id)
    create_route('GET /albums/year', get_albums_by_year_integration_id)
    create_route('POST /albums/summary', get_album_summary_integration_id)

    # Create stage directly if it doesn't exist
    stage_name = 'dev'
    try:
        apigateway_client.create_stage(
            ApiId=api_id,
            StageName=stage_name,
            AutoDeploy=True
        )
        print(f"Created new stage: {stage_name}")
    except apigateway_client.exceptions.BadRequestException:
        print(f"Stage '{stage_name}' already exists.")

    # Deploy the API
    apigateway_client.create_deployment(ApiId=api_id, StageName=stage_name)
    print(f"API deployed to stage: {stage_name}")

    # Add permissions for API Gateway to invoke Lambda
    def add_permission(function_name, api_id, stage_name, region, lambda_client):
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=f"{api_id}-{function_name}",
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=f"arn:aws:execute-api:{region}:{aws_account_id}:{api_id}/{stage_name}/*/*"  # Corrected SourceArn format
        )

    # Call add_permission for each Lambda function
    add_permission("GetAlbums", api_id, stage_name, region, lambda_client)
    add_permission("GetAlbumsByYear", api_id, stage_name, region, lambda_client)
    add_permission("GetAlbumSummary", api_id, stage_name, region, lambda_client)

    print(f"API Gateway is set up and linked to Lambda functions!")

# Call the create_api_gateway function to run the setup
create_api_gateway()



