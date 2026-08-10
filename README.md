# S3 Presigned URL API

This project provides a small FastAPI service that generates S3 presigned URLs locally (no network call to AWS required). The container still needs AWS credentials to compute signatures; pass them via env vars.

Build the Docker image:

```bash
docker build -t s3-presign-api .
```

Run the container (example with dummy creds):

```bash
docker run -p 8000:8000 \
  -e AWS_ACCESS_KEY_ID=AKIA_TEST_ACCESS_KEY_1234 \
  -e AWS_SECRET_ACCESS_KEY=TEST_SECRET_KEY_1234567890abcdef1234567890abcd \
  s3-presign-api
```

Example request (generate a PUT presigned URL):

```bash
curl -s -X POST http://localhost:8000/presign \
  -H "Content-Type: application/json" \
  -d '{"bucket":"my-bucket","key":"uploads/file.txt","operation":"put","expires":3600}' | jq
```

Using a custom S3 endpoint (MinIO / LocalStack)

Run the container with `S3_ENDPOINT_URL` pointing at your S3-compatible service:

```bash
docker run -p 8000:8000 \
  -e AWS_ACCESS_KEY_ID=minio \
  -e AWS_SECRET_ACCESS_KEY=minio123 \
  -e S3_ENDPOINT_URL=http://host.docker.internal:9000 \
  s3-presign-api
```

Then request a presigned URL as usual; the service will sign URLs against the custom endpoint.

Files:
- [app/main.py](app/main.py) - FastAPI app exposing `POST /presign` and `GET /health`
- [Dockerfile](Dockerfile) - Docker image definition
- [requirements.txt](requirements.txt) - Python deps
