import json
import boto3

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('albums')  # Replace with your actual table name

def lambda_handler(event, context):
    """
    Generates a summary for a specified album. The album title is passed in
    the request body or as a query parameter.
    """
    # Get the album title from the request
    body = event.get('body')
    
    if body:
        try:
            body = json.loads(body)  # Parse body only if it's not empty
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON in body'})
            }
    album_title = body.get('title') if body else event.get('queryStringParameters', {}).get('title')
    if not album_title:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing album title in the request'})
        }
    # Convert the input album title to sentence case (capitalize first letter)
    album_title_formatted = album_title.strip().capitalize()

    try:
        # Query DynamoDB to check if the album title exists
        response = table.get_item(
            Key={'title': album_title_formatted}
        )

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Album not found in the database'})
            }

        # Fetch the item from DynamoDB that was retrieved in the first response
        bey_album = response['Item']

        bey_album_data = {
            'release_year': bey_album['release_year'],
            'genre': bey_album['genre'],
            'tracklist': bey_album['tracklist'],
            'album_url': bey_album['album_url']
        }

        summary = f"The album '{album_title}' is a masterpiece of modern music."

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'title': album_title, 'data': bey_album_data, 'summary': summary})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }