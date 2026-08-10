from typing import Optional
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from botocore.config import Config


class PresignRequest(BaseModel):
    bucket: str
    key: str
    operation: str = "put"
    expires: int = 3600
    region: Optional[str] = None
    endpoint_url: Optional[str] = None
    addressing_style: Optional[str] = None


app = FastAPI(title="S3 Presign API")


def s3_client(region: Optional[str] = None, endpoint_url: Optional[str] = None, addressing_style: Optional[str] = None):
    # Allow overriding the endpoint via argument or environment variable (for MinIO/localstack)
    env_endpoint = os.getenv("S3_ENDPOINT_URL")
    endpoint = endpoint_url or env_endpoint or None
    kwargs = {
        "aws_access_key_id": os.getenv(
            "AWS_ACCESS_KEY_ID", "AKIA_TEST_ACCESS_KEY_1234"
        ),
        "aws_secret_access_key": os.getenv(
            "AWS_SECRET_ACCESS_KEY",
            "TEST_SECRET_KEY_1234567890abcdef1234567890abcd",
        ),
        "region_name": region or os.getenv("AWS_REGION", "us-east-1"),
    }
    if endpoint:
        kwargs["endpoint_url"] = endpoint
    # Configure addressing style and signature version (v4)
    cfg_kwargs = {"signature_version": "s3v4"}
    if addressing_style:
        cfg_kwargs["s3"] = {"addressing_style": addressing_style}
    else:
        env_addr = os.getenv("S3_ADDRESSING_STYLE")
        if env_addr:
            cfg_kwargs["s3"] = {"addressing_style": env_addr}

    config = Config(**cfg_kwargs)
    return boto3.client("s3", config=config, **kwargs)


@app.post("/presign")
async def presign(req: PresignRequest):
    op_map = {"put": "put_object", "get": "get_object"}
    op = req.operation.lower()
    if op not in op_map:
        raise HTTPException(status_code=400, detail="operation must be 'put' or 'get'")

    client = s3_client(req.region, req.endpoint_url, req.addressing_style)
    try:
        url = client.generate_presigned_url(
            ClientMethod=op_map[op], Params={"Bucket": req.bucket, "Key": req.key}, ExpiresIn=req.expires
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"url": url}


@app.get("/health")
async def health():
    return {"status": "ok"}
