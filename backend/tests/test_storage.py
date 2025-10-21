import pytest
from app.services.storage import get_storage
from app.core.config import settings
from fastapi.testclient import TestClient
from app.main import app
from minio.error import S3Error

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_minio_connection(client):
    """
    Tests the connection to MinIO by creating a bucket, checking if it exists,
    and then deleting it.
    """
    storage_client = get_storage()
    bucket_name = settings.MINIO_BUCKET

    try:
        # 1. Ensure the bucket does not exist before the test
        if storage_client.bucket_exists(bucket_name):
            objects = storage_client.list_objects(bucket_name)
            for obj in objects:
                storage_client.remove_object(bucket_name, obj.object_name)
            storage_client.remove_bucket(bucket_name)

        # 2. Create the bucket
        storage_client.make_bucket(bucket_name)
        assert storage_client.bucket_exists(bucket_name)

        # 3. Clean up by removing the bucket
        storage_client.remove_bucket(bucket_name)
        assert not storage_client.bucket_exists(bucket_name)

    except S3Error as e:
        if "Connection refused" in str(e):
            pytest.fail(
                "MinIO connection failed. Please ensure the MinIO server is running "
                "and accessible at the configured endpoint.",
                pytrace=False
            )
        else:
            pytest.fail(f"MinIO connection test failed with an S3Error: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred during the MinIO connection test: {e}")