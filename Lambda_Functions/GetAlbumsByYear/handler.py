import boto3
import json

def lambda_handler(event, context):
    """
    Fetches albums released in a specific year from the DynamoDB table.
    """
    dynamodb = boto3.resource('dynamodb')
    table_name = 'albums'  # Replace with your table name
    table = dynamodb.Table(table_name)

    # Get the year from query parameters
    year = event.get('queryStringParameters', {}).get('release_year')

    if not year:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing releaseYear query parameter'})
        }

    try:
        # Query the table for albums released in the specified year
        response = table.scan(
            FilterExpression='release_year = :year',
            ExpressionAttributeValues={':year': year}
        )
        bey_albums = response['Items']

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(albums)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
