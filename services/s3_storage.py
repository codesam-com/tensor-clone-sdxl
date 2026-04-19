import boto3
import os
import base64
import uuid

S3_BUCKET = os.getenv("S3_BUCKET")
S3_REGION = os.getenv("S3_REGION")

s3 = boto3.client("s3", region_name=S3_REGION)


def upload_base64_image(base64_str: str):
    image_data = base64.b64decode(base64_str)
    key = f"images/{uuid.uuid4()}.png"

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=image_data,
        ContentType="image/png"
    )

    url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{key}"
    return url
