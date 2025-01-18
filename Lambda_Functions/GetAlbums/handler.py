import json
import boto3

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('albums')  # Replace with your actual table name

def lambda_handler(event, context):
    try:
        # Fetch all items from the DynamoDB table
        response = table.scan()
        bey_albums = response['Items']
        bey_albums.sort(key=lambda x: x['release_year'])

        # Reorder the keys within each album in place
        for idx, album in enumerate(bey_albums):
            bey_albums[idx] = {
                'title': album['title'],
                'release_year': album['release_year'],
                'genre': album['genre'],
                'tracklist': album['tracklist'],
                'album_url': album['album_url']
            }

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(bey_albums)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({'error': str(e)})
        }