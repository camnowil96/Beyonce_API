import boto3
from botocore.exceptions import ClientError

# Create an S3 client
s3_client = boto3.client('s3')

bucket_name = 'beyonce-album-covers-2025' # Change this to a unique name

try:
    # Check if the bucket already exists and is owned by you
    s3_client.head_bucket(Bucket=bucket_name)
    print(f"The bucket '{bucket_name}' already exists and is owned by you.")
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == '403':
        # Bucket exists but is owned by someone else
        print(f"The bucket '{bucket_name}' already exists. Please choose a different name.")
    elif error_code == '404':
        # The bucket doesn't exist; create it
        try:
            response = s3_client.create_bucket(
                ACL='private',
                Bucket=bucket_name                
            )
            s3_client.put_object(Bucket="beyonce-album-covers-2025", Key='albumcover/')
            print(f"Bucket '{bucket_name}' created successfully.")
        except ClientError as create_error:
            print(f"Error creating bucket: {create_error}")
    else:
        # Handle unexpected errors
        print(f"Unexpected error: {e}")

# Create a table in DynamoDB

# Get the service resource.
dynamodb = boto3.resource('dynamodb')

# Create the DynamoDB table.
table = dynamodb.create_table(
    TableName='albums',
    KeySchema=[
        {
            'AttributeName': 'title',
            'KeyType': 'HASH'
        },
                {
            'AttributeName': 'release_year',
            'KeyType': 'RANGE'
        },
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'genre',
            'AttributeType': 'S'
        },
                {
            'AttributeName': 'tracklist',
            'AttributeType': 'S'
        },
    ],
)

# Wait until the table exists.
table.wait_until_exists()

# Print out some data about the table.
print(table.item_count)