import boto3
import json

def handler(event, context):
    """
    Fetches all albums from the DynamoDB table and returns them as a JSON response.
    """
    dynamodb = boto3.resource('dynamodb')
    table_name = 'albums'  # Replace with your table name
    table = dynamodb.Table(table_name)

    try:
        response = table.scan()  # Fetch all items from the table
        bey_albums = response['Items']

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(bey_albums)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
