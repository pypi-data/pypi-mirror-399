r"""
Integration tests for gcpinventory with real GCP credentials.

These tests use a real service account to:
1. Authenticate with GCP
2. Fetch real GCP resources (BigQuery, Cloud Scheduler)
3. Create ETLObject instances from real data
4. Validate ObjectIDAssigner works with production data

REQUIRES:
- Service account at E:\A\GCP_ETL_Pipeline\hackathon\SyncFlow_GCP_Intelligence\config\service-account.json
- GCP project: prismatic-smoke-463810-c1
- Required APIs enabled: BigQuery, Cloud Scheduler, Cloud Functions
"""

import os
import pytest
from google.oauth2 import service_account
from google.cloud import bigquery, scheduler_v1

from gcpinventory.models import ETLObject, ObjectType, ObjectStatus
from gcpinventory.assigner import ObjectIDAssigner


# Path to service account (can be overridden with env var)
DEFAULT_SA_PATH = "/mnt/e/A/GCP_ETL_Pipeline/hackathon/SyncFlow_GCP_Intelligence/config/service-account.json"
SA_PATH = os.getenv("GCP_SERVICE_ACCOUNT_PATH", DEFAULT_SA_PATH)
PROJECT_ID = "prismatic-smoke-463810-c1"


@pytest.fixture(scope="module")
def gcp_credentials():
    """Load GCP credentials from service account file."""
    if not os.path.exists(SA_PATH):
        pytest.skip(f"Service account file not found at {SA_PATH}")

    credentials = service_account.Credentials.from_service_account_file(
        SA_PATH,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return credentials


@pytest.fixture(scope="module")
def bigquery_client(gcp_credentials):
    """Create BigQuery client."""
    return bigquery.Client(project=PROJECT_ID, credentials=gcp_credentials)


@pytest.fixture(scope="module")
def scheduler_client(gcp_credentials):
    """Create Cloud Scheduler client."""
    return scheduler_v1.CloudSchedulerClient(credentials=gcp_credentials)


class TestGCPAuthentication:
    """Test that GCP authentication works with the service account."""

    def test_service_account_file_exists(self):
        """Verify service account file exists."""
        assert os.path.exists(SA_PATH), f"Service account not found at {SA_PATH}"

    def test_credentials_load(self, gcp_credentials):
        """Test that credentials load successfully."""
        assert gcp_credentials is not None
        assert gcp_credentials.project_id == PROJECT_ID

    def test_bigquery_connection(self, bigquery_client):
        """Test BigQuery client can connect."""
        # Simple query to verify connection
        query = "SELECT 1 as test"
        result = bigquery_client.query(query).result()
        rows = list(result)
        assert len(rows) == 1
        assert rows[0]["test"] == 1


class TestBigQueryDatasetCollection:
    """Test collecting BigQuery datasets as ETLObjects."""

    def test_collect_bigquery_datasets(self, bigquery_client):
        """Test fetching BigQuery datasets and creating ETLObjects."""
        objects = []

        # Collect datasets
        for dataset_list_item in bigquery_client.list_datasets():
            # Fetch full dataset to get location and other details
            dataset = bigquery_client.get_dataset(dataset_list_item.dataset_id)

            obj = ETLObject(
                object_id=None,  # Will be assigned later
                object_type=ObjectType.DATASET,
                name=dataset.dataset_id,
                gcp_resource_name=f"{PROJECT_ID}.{dataset.dataset_id}",
                description=f"BigQuery dataset in {dataset.location}",
                status=ObjectStatus.ACTIVE,
                metadata={
                    "location": dataset.location,
                    "created": dataset.created.isoformat() if dataset.created else None,
                    "resource_type": "bigquery_dataset",
                },
            )
            objects.append(obj)

        # Verify we collected at least one dataset
        assert len(objects) > 0, "No BigQuery datasets found in project"

        # Verify ETLObject structure
        for obj in objects:
            assert obj.object_type == ObjectType.DATASET
            assert obj.name is not None
            assert obj.gcp_resource_name.startswith(PROJECT_ID)
            assert obj.status == ObjectStatus.ACTIVE
            assert "location" in obj.metadata

    def test_assign_ids_to_real_datasets(self, bigquery_client):
        """Test ObjectIDAssigner with real BigQuery datasets."""
        objects = []

        # Collect datasets
        for dataset in bigquery_client.list_datasets():
            obj = ETLObject(
                object_id=None,
                object_type=ObjectType.DATASET,
                name=dataset.dataset_id,
                gcp_resource_name=f"{PROJECT_ID}.{dataset.dataset_id}",
            )
            objects.append(obj)

        # Assign IDs
        assigner = ObjectIDAssigner()
        assigner.assign_ids(objects)

        # Verify all objects have IDs
        for obj in objects:
            assert obj.object_id is not None
            assert obj.object_id.startswith("OBJ")
            assert len(obj.object_id) == 7  # OBJ0001 format

        # Verify IDs are unique
        object_ids = [obj.object_id for obj in objects]
        assert len(object_ids) == len(set(object_ids)), "Duplicate IDs found"

        # Verify reverse assignments
        for obj in objects:
            assert obj.object_id in assigner.reverse_assignments
            assert assigner.reverse_assignments[obj.object_id]["name"] == obj.name


class TestCloudSchedulerCollection:
    """Test collecting Cloud Scheduler jobs as ETLObjects."""

    def test_collect_scheduler_jobs(self, scheduler_client):
        """Test fetching Cloud Scheduler jobs and creating ETLObjects."""
        objects = []
        parent = f"projects/{PROJECT_ID}/locations/us-central1"

        try:
            # Collect scheduler jobs
            for job in scheduler_client.list_jobs(request={"parent": parent}):
                obj = ETLObject(
                    object_id=None,
                    object_type=ObjectType.TRIGGER,
                    name=job.name.split("/")[-1],
                    gcp_resource_name=job.name,
                    description=job.description or "Cloud Scheduler job",
                    status=ObjectStatus.ACTIVE,
                    metadata={
                        "schedule": job.schedule,
                        "state": job.state.name if job.state else None,
                        "timezone": job.time_zone,
                        "resource_type": "cloud_scheduler",
                    },
                )
                objects.append(obj)
        except Exception as e:
            pytest.skip(f"Cloud Scheduler API may not be enabled or no jobs exist: {e}")

        # If we found jobs, verify structure
        if len(objects) > 0:
            for obj in objects:
                assert obj.object_type == ObjectType.TRIGGER
                assert obj.name is not None
                assert "schedule" in obj.metadata


class TestMixedObjectCollection:
    """Test collecting multiple object types and assigning stable IDs."""

    def test_mixed_collection_with_stable_ids(self, bigquery_client, scheduler_client):
        """Test collecting datasets and triggers together with ID assignment."""
        objects = []

        # Collect BigQuery datasets
        for dataset in bigquery_client.list_datasets():
            obj = ETLObject(
                object_id=None,
                object_type=ObjectType.DATASET,
                name=dataset.dataset_id,
                gcp_resource_name=f"{PROJECT_ID}.{dataset.dataset_id}",
            )
            objects.append(obj)

        # Collect Cloud Scheduler jobs (if available)
        parent = f"projects/{PROJECT_ID}/locations/us-central1"
        try:
            for job in scheduler_client.list_jobs(request={"parent": parent}):
                obj = ETLObject(
                    object_id=None,
                    object_type=ObjectType.TRIGGER,
                    name=job.name.split("/")[-1],
                    gcp_resource_name=job.name,
                )
                objects.append(obj)
        except Exception:
            pass  # Skip if no scheduler jobs

        assert len(objects) > 0, "No objects collected"

        # First run - assign IDs
        assigner1 = ObjectIDAssigner()
        assigner1.assign_ids(objects)
        first_run_ids = {obj.name: obj.object_id for obj in objects}

        # Second run - recreate same objects and assign IDs again
        objects2 = []
        for dataset in bigquery_client.list_datasets():
            obj = ETLObject(
                object_id=None,
                object_type=ObjectType.DATASET,
                name=dataset.dataset_id,
                gcp_resource_name=f"{PROJECT_ID}.{dataset.dataset_id}",
            )
            objects2.append(obj)

        assigner2 = ObjectIDAssigner()
        assigner2.assign_ids(objects2)
        second_run_ids = {obj.name: obj.object_id for obj in objects2}

        # Verify stable IDs - same objects get same IDs across runs
        for name in second_run_ids:
            if name in first_run_ids:
                assert first_run_ids[name] == second_run_ids[name], \
                    f"Object {name} got different IDs: {first_run_ids[name]} vs {second_run_ids[name]}"

    def test_to_dict_serialization_with_real_data(self, bigquery_client):
        """Test ETLObject.to_dict() with real GCP data."""
        objects = []

        for dataset_list_item in bigquery_client.list_datasets():
            # Fetch full dataset to get location
            dataset = bigquery_client.get_dataset(dataset_list_item.dataset_id)

            obj = ETLObject(
                object_id=None,
                object_type=ObjectType.DATASET,
                name=dataset.dataset_id,
                gcp_resource_name=f"{PROJECT_ID}.{dataset.dataset_id}",
                metadata={"location": dataset.location},
            )
            objects.append(obj)

        assert len(objects) > 0

        # Assign IDs
        assigner = ObjectIDAssigner()
        assigner.assign_ids(objects)

        # Test serialization
        for obj in objects:
            d = obj.to_dict()

            # Verify structure
            assert isinstance(d, dict)
            assert d["object_id"].startswith("OBJ")
            assert d["object_type"] == "DATASET"
            assert d["name"] == obj.name
            assert d["gcp_resource_name"] == obj.gcp_resource_name
            assert isinstance(d["metadata"], dict)
            assert "location" in d["metadata"]
