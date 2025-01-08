import json

def handler(event, context):
    """
    Generates a summary for a specified album. The album title is passed in
    the request body or as a query parameter.
    """
    # Get the album title from the request
    body = json.loads(event.get('body', '{}'))
    album_title = body.get('title') or event.get('queryStringParameters', {}).get('title')

    if not album_title:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing album title in the request'})
        }

    try:
        # Placeholder for AI-generated summary (replace with actual implementation)
        summary = f"The album '{album_title}' is a masterpiece of modern music."

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'title': album_title, 'summary': summary})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
