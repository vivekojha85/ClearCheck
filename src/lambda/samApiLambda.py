import urllib.request
import json
import boto3
import os

# SAM.gov API endpoint
SAM_API_URL = 'https://api.sam.gov/data-services/v1/extracts?api_key=4yZkGyeqYTqYjnvWZtCxaMzboz3h40CjlDFL868H&fileType=EXCLUSION'
# AWS S3 bucket name
S3_BUCKET_NAME = 'codeblodded'
# S3 object name
S3_OBJECT_NAME = 'Source/exclusionData.zip'

# AWS S3 client
s3_client = boto3.client('s3')


def download_exclusion_file(api_url):
    try:
        # Download the file from SAM.gov API
        with urllib.request.urlopen(api_url) as response:
            data = response.read()
            return data
    except Exception as e:
        print(f"Error downloading file from SAM.gov: {e}")
        return None


def upload_to_s3(file_data, bucket_name, object_name):
    """
    Uploads the downloaded file data to an S3 bucket.
    """
    try:
        s3_client.put_object(Body=file_data, Bucket=bucket_name, Key=object_name)
        print(f"File uploaded successfully to S3 bucket")
        # print(f"File uploaded successfully to S3 bucket {bucket_name} with object name {object_name}.")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")


def lambda_handler(event, context):
    """
    AWS Lambda handler function to download the exclusion file and upload it to S3.
    """
    # Log event
    print(f"Received event: {json.dumps(event)}")

    # Download the exclusion file from SAM.gov
    file_data = download_exclusion_file(SAM_API_URL)

    if file_data:
        # Upload the file to the S3 bucket
        upload_to_s3(file_data, S3_BUCKET_NAME, S3_OBJECT_NAME)
        return {
            'statusCode': 200,
            'body': json.dumps(
                f"File uploaded successfully to S3 bucket {S3_BUCKET_NAME} with object name {S3_OBJECT_NAME}.")
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps("Failed to download or upload the exclusion file.")
        }











