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

def get_storage():
    return client
