from minio import Minio
from app.core.config import settings

# Manually parse and clean the endpoint
endpoint_parts = settings.MINIO_ENDPOINT.split(':')
cleaned_host = endpoint_parts[0].strip()

# Aggressively clean the port part
raw_port = endpoint_parts[1].strip()
cleaned_port = "".join(filter(str.isdigit, raw_port))

cleaned_endpoint = f"{cleaned_host}:{cleaned_port}"

# Aggressively clean access_key and secret_key
cleaned_access_key = "".join(filter(lambda x: ord(x) < 128, settings.MINIO_ACCESS_KEY)).strip()
cleaned_secret_key = "".join(filter(lambda x: ord(x) < 128, settings.MINIO_SECRET_KEY)).strip()

client = Minio(
    endpoint=cleaned_endpoint,
    access_key=cleaned_access_key,
    secret_key=cleaned_secret_key,
    secure=False
)

# Ensure bucket exists
try:
    if not client.bucket_exists(settings.MINIO_BUCKET):
        client.make_bucket(settings.MINIO_BUCKET)
        print(f"Created MinIO bucket: {settings.MINIO_BUCKET}")
except Exception as e:
    print(f"Error checking/creating MinIO bucket: {e}")

def upload_file(file_content: bytes, filename: str, content_type: str = "application/octet-stream") -> str:
    """Upload a file to MinIO and return the object name."""
    import io
    import uuid
    
    # Generate a unique name to avoid collisions
    unique_filename = f"{uuid.uuid4()}-{filename}"
    
    client.put_object(
        settings.MINIO_BUCKET,
        unique_filename,
        io.BytesIO(file_content),
        length=len(file_content),
        content_type=content_type
    )
    return unique_filename

def download_file(object_name: str) -> str:
    """Download a file from MinIO to the local UPLOAD_DIR and return the path."""
    import os
    local_path = os.path.join(settings.UPLOAD_DIR, object_name)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    client.fget_object(
        settings.MINIO_BUCKET,
        object_name,
        local_path
    )
    return local_path

def delete_local_file(file_path: str):
    """Clean up local temporary file."""
    import os
    if os.path.exists(file_path):
        os.remove(file_path)

def get_storage():
    return client
