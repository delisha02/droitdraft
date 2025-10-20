import pytest
from app.services.storage import get_storage
from app.core.config import settings

def test_minio_connection():
    """
    Tests the connection to MinIO by creating a bucket, checking if it exists,
    and then deleting it.
    """
    storage_client = get_storage()
    bucket_name = settings.MINIO_BUCKET

    try:
        # 1. Ensure the bucket does not exist before the test
        if storage_client.bucket_exists(bucket_name):
            # To be safe, remove all objects before removing the bucket
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

    except Exception as e:
        pytest.fail(f"MinIO connection test failed: {e}")