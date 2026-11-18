import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


class S3Storage:
    def __init__(self):
        self.bucket = settings.S3_BUCKET_NAME
        self.client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
        )

    def upload_file(
        self,
        local_path: str,
        object_key: str,
        content_type: str = "image/tiff",
    ) -> str:
        path = Path(local_path)

        if not path.is_file():
            raise FileNotFoundError("Dataset file does not exist.")

        self.client.upload_file(
            str(path),
            self.bucket,
            object_key,
            ExtraArgs={
                "ContentType": content_type,
                "ServerSideEncryption": "AES256",
            },
        )

        return object_key

    def download_file(
        self,
        object_key: str,
        destination: str,
    ) -> str:
        try:
            self.client.download_file(
                self.bucket,
                object_key,
                destination,
            )
        except ClientError:
            raise

        return destination

    def create_download_url(
        self,
        object_key: str,
        expires_in: int = 300,
    ) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket,
                "Key": object_key,
            },
            ExpiresIn=expires_in,
        )