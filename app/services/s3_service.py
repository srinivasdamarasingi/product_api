import boto3
from botocore.exceptions import BotoCoreError, ClientError
from app.config import settings

s3_client = boto3.client(
    "s3",
    region_name=settings.AWS_REGION
)


def upload_file_to_s3(file_obj, object_key: str, content_type: str) -> str:
    """
    Upload a file object to the Product API S3 bucket.

    Returns the S3 object key.
    """

    try:
        s3_client.upload_fileobj(
            file_obj,
            settings.S3_BUCKET_NAME,
            object_key,
            ExtraArgs={
                "ContentType": content_type
            }
        )

        return object_key

    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(
            "Failed to upload file to S3"
        ) from exc


def delete_file_from_s3(object_key: str) -> None:
    """
    Delete an object from the Product API S3 bucket.
    """

    try:
        s3_client.delete_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=object_key
        )

    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(
            "Failed to delete file from S3"
        ) from exc


def generate_presigned_url(
    object_key: str,
    expires_in: int = 300
) -> str:
    """
    Generate a temporary URL for downloading
    a private S3 object.
    """

    try:
        return s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.S3_BUCKET_NAME,
                "Key": object_key
            },
            ExpiresIn=expires_in
        )

    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(
            "Failed to generate presigned URL"
        ) from exc
