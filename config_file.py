import boto3
import os
import logging
import json
from botocore.exceptions import ClientError

# Function definitions
def upload_file(file_name, bucket, folder, object_name=None):
    """Upload a file to an S3 bucket."""
    if object_name is None:
        object_name = f"{folder}/{os.path.basename(file_name)}"
    try:
        s3_client = boto3.client("s3")
        s3_client.upload_file(file_name, bucket, object_name)
        logging.info(f"Uploaded {file_name} to {bucket}/{object_name}")
    except ClientError as e:
        logging.error(f"Error uploading {file_name} to S3: {e}")
        raise

def upload_album_covers(local_folder, bucket, folder):
    """Upload all album cover images from a local folder to the S3 bucket."""
    try:
        for file_name in os.listdir(local_folder):
            file_path = os.path.join(local_folder, file_name)
            if os.path.isfile(file_path):
                upload_file(file_path, bucket, folder)
    except ClientError as e:
        logging.error(f"Error uploading album covers: {e}")
        raise

def add_album(table, title, release_year, genre, tracklist, album_url):
    """Add an album to the DynamoDB table."""
    try:
        table.put_item(
            Item={
                "title": title,
                "release_year": release_year,
                "genre": genre,
                "tracklist": tracklist,
                "album_url": album_url
            }
        )
        logging.info(f"Added album '{title}' to table {table.name}")
    except ClientError as e:
        logging.error(
            f"Couldn't add album '{title}' to table {table.name}. Error: {e}"
        )
        raise

def process_album_data(json_file, table, bucket, s3_folder):
    """
    Processes album data from a JSON file, uploads covers to S3, 
    and inserts metadata into DynamoDB.
    """
    with open(json_file, "r") as file:
        album_data = json.load(file)

    for album in album_data:
        title = album["title"]
        release_year = album["releaseYear"]
        genre = album["genre"]
        tracklist = album["tracklist"]
        local_cover_path = album["cover_path"]

        # Upload album cover to S3
        object_name = f"{s3_folder}/{os.path.basename(local_cover_path)}"
        upload_file(local_cover_path, bucket, s3_folder)

        # Construct S3 URL
        album_url = f"https://{bucket}.s3.amazonaws.com/{object_name}"

        # Insert album metadata into DynamoDB
        add_album(table, title, release_year, genre, tracklist, album_url)

def setup_s3_bucket(bucket_name, folder):
    """Ensure the S3 bucket and folder exist."""
    s3_client = boto3.client("s3")
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        logging.info(f"The bucket '{bucket_name}' already exists.")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            try:
                s3_client.create_bucket(Bucket=bucket_name, ACL="private")
                logging.info(f"Bucket '{bucket_name}' created successfully.")
            except ClientError as create_error:
                logging.error(f"Error creating bucket: {create_error}")
                raise
        else:
            logging.error(f"Unexpected error: {e}")
            raise

    # Ensure the folder exists in the bucket
    try:
        s3_client.put_object(Bucket=bucket_name, Key=f"{folder}/")
        logging.info(f"Folder '{folder}/' ensured in bucket '{bucket_name}'.")
    except ClientError as e:
        logging.error(f"Error ensuring folder: {e}")
        raise

def setup_dynamodb_table():
    """Ensure the DynamoDB table exists."""
    dynamodb = boto3.resource("dynamodb")
    try:
        table = dynamodb.create_table(
            TableName="albums",
            KeySchema=[{"AttributeName": "title", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "title", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        logging.info("DynamoDB table 'albums' created successfully.")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "ResourceInUseException":
            logging.info("DynamoDB table 'albums' already exists.")
        else:
            logging.error(f"Unexpected error occurred: {e}")
            raise

    return dynamodb.Table("albums")

# Main script execution
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Configuration
    bucket_name = "beyonce-album-covers-2025"
    s3_folder = "albumcover"
    json_file = "albums.json"
    local_folder = "/home/camnowil96/Downloads/Album_Cover_Art"

    # Ensure S3 bucket and folder exist
    setup_s3_bucket(bucket_name, s3_folder)

    # Ensure DynamoDB table exists
    table = setup_dynamodb_table()

    # Process album data
    process_album_data(json_file, table, bucket_name, s3_folder)
