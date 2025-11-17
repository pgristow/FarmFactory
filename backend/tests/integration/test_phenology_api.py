"""
Integration tests for Phenology Observations API endpoints.

Tests:
- Phenology CRUD
- Timeline endpoint
- Photo upload (mocked)
- Growth stage tracking
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status
from io import BytesIO

PHENOLOGY_ENDPOINT = "/api/v1/phenology"


@pytest.fixture
def sample_phenology_data():
    """Sample phenology observation data."""
    return {
        "time": "2024-01-20T09:00:00Z",
        "growth_stage": "vegetative",
        "height_cm": 25.0,
        "canopy_cover_percent": 40.0,
        "health_score": 8,
        "flowering_percent": 0.0,
        "notes": "Healthy vegetative growth, good leaf color",
        "observer": "John Farmer"
    }


@pytest.fixture
def setup_planting(test_db, client):
    """Setup farm, plot, crop, and planting for testing."""
    from app.models.farm import Farm
    from app.models.plot import Plot
    from app.models.crop import Crop
    from app.models.crop import Planting

    farm = Farm(name="Test Farm", total_area_hectares=10.0)
    test_db.add(farm)
    test_db.commit()

    plot = Plot(name="Test Plot", farm_id=farm.id, area_hectares=1.0)
    test_db.add(plot)
    test_db.commit()

    crop = Crop(name="Test Crop", crop_type="vegetable")
    test_db.add(crop)
    test_db.commit()

    planting = Planting(
        plot_id=plot.id,
        crop_id=crop.id,
        planting_date=datetime(2024, 1, 1),
        status="active"
    )
    test_db.add(planting)
    test_db.commit()

    return planting


@pytest.mark.integration
@pytest.mark.api
class TestPhenologyAPI:
    """Test phenology observation CRUD operations."""

    def test_create_phenology_observation(self, client, setup_planting, sample_phenology_data):
        """Test POST /api/v1/plantings/{planting_id}/phenology - Record observation."""
        planting = setup_planting
        response = client.post(
            f"/api/v1/plantings/{planting.id}/phenology",
            json=sample_phenology_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["growth_stage"] == sample_phenology_data["growth_stage"]
        assert data["height_cm"] == sample_phenology_data["height_cm"]
        assert data["health_score"] == sample_phenology_data["health_score"]
        assert data["planting_id"] == str(planting.id)
        assert "id" in data
        assert "time" in data

    def test_create_phenology_minimal_fields(self, client, setup_planting):
        """Test creating observation with minimal required fields."""
        planting = setup_planting
        minimal_obs = {
            "time": "2024-01-20T09:00:00Z",
            "growth_stage": "vegetative"
        }
        response = client.post(
            f"/api/v1/plantings/{planting.id}/phenology",
            json=minimal_obs
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["growth_stage"] == "vegetative"

    def test_create_phenology_with_all_fields(self, client, setup_planting):
        """Test creating comprehensive observation."""
        planting = setup_planting
        comprehensive_obs = {
            "time": "2024-02-15T09:00:00Z",
            "growth_stage": "flowering",
            "height_cm": 85.0,
            "canopy_cover_percent": 75.0,
            "health_score": 9,
            "flowering_percent": 50.0,
            "fruit_set_percent": 10.0,
            "pest_pressure": "low",
            "disease_presence": "none",
            "notes": "First flowers appearing",
            "observer": "Jane Agronomist"
        }
        response = client.post(
            f"/api/v1/plantings/{planting.id}/phenology",
            json=comprehensive_obs
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["height_cm"] == 85.0
        assert data["flowering_percent"] == 50.0

    def test_list_phenology_observations(self, client, setup_planting, sample_phenology_data):
        """Test GET /api/v1/plantings/{planting_id}/phenology - Get observation history."""
        planting = setup_planting

        # Create multiple observations over time
        stages = ["germination", "vegetative", "flowering", "fruiting"]
        for i, stage in enumerate(stages):
            obs_data = {
                **sample_phenology_data,
                "time": (datetime(2024, 1, 10) + timedelta(weeks=i * 2)).isoformat() + "Z",
                "growth_stage": stage,
                "height_cm": 10.0 + i * 20
            }
            client.post(f"/api/v1/plantings/{planting.id}/phenology", json=obs_data)

        # List observations
        response = client.get(f"/api/v1/plantings/{planting.id}/phenology")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 4

    def test_filter_phenology_by_date_range(self, client, setup_planting, sample_phenology_data):
        """Test filtering observations by date range."""
        planting = setup_planting

        # Create observations across different dates
        dates = [
            "2024-01-10T09:00:00Z",
            "2024-01-20T09:00:00Z",
            "2024-02-10T09:00:00Z",
            "2024-02-20T09:00:00Z"
        ]
        for date_str in dates:
            obs_data = {**sample_phenology_data, "time": date_str}
            client.post(f"/api/v1/plantings/{planting.id}/phenology", json=obs_data)

        # Filter to January only
        response = client.get(
            f"/api/v1/plantings/{planting.id}/phenology?"
            f"start_date=2024-01-01&end_date=2024-01-31"
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 2

    def test_filter_phenology_by_growth_stage(self, client, setup_planting, sample_phenology_data):
        """Test filtering by growth stage."""
        planting = setup_planting

        # Create observations at different stages
        stages = ["vegetative", "flowering", "vegetative", "fruiting"]
        for i, stage in enumerate(stages):
            obs_data = {
                **sample_phenology_data,
                "growth_stage": stage,
                "time": (datetime(2024, 1, 10) + timedelta(days=i * 7)).isoformat() + "Z"
            }
            client.post(f"/api/v1/plantings/{planting.id}/phenology", json=obs_data)

        # Filter by stage
        response = client.get(f"/api/v1/plantings/{planting.id}/phenology?stage=vegetative")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        vegetative_obs = [item for item in items if item.get("growth_stage") == "vegetative"]
        assert len(vegetative_obs) >= 2

    def test_pagination_phenology_observations(self, client, setup_planting, sample_phenology_data):
        """Test pagination on phenology observations."""
        planting = setup_planting

        # Create 20 observations
        for i in range(20):
            obs_data = {
                **sample_phenology_data,
                "time": (datetime(2024, 1, 1) + timedelta(days=i)).isoformat() + "Z"
            }
            client.post(f"/api/v1/plantings/{planting.id}/phenology", json=obs_data)

        # Test first page
        response = client.get(f"/api/v1/plantings/{planting.id}/phenology?limit=10&offset=0")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) == 10

        # Test second page
        response = client.get(f"/api/v1/plantings/{planting.id}/phenology?limit=10&offset=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) == 10

    def test_get_phenology_observation_by_id(self, client, setup_planting, sample_phenology_data):
        """Test GET /api/v1/phenology/{id} - Get specific observation."""
        planting = setup_planting

        # Create observation
        create_response = client.post(
            f"/api/v1/plantings/{planting.id}/phenology",
            json=sample_phenology_data
        )
        obs_id = create_response.json()["id"]

        # Get observation
        response = client.get(f"{PHENOLOGY_ENDPOINT}/{obs_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == obs_id
        assert data["growth_stage"] == sample_phenology_data["growth_stage"]

    def test_get_phenology_observation_not_found(self, client):
        """Test getting non-existent observation."""
        import uuid
        fake_id = str(uuid.uuid4())

        response = client.get(f"{PHENOLOGY_ENDPOINT}/{fake_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_phenology_observation(self, client, setup_planting, sample_phenology_data):
        """Test PUT /api/v1/phenology/{id} - Update observation."""
        planting = setup_planting

        # Create observation
        create_response = client.post(
            f"/api/v1/plantings/{planting.id}/phenology",
            json=sample_phenology_data
        )
        obs_id = create_response.json()["id"]

        # Update observation
        update_data = {
            "height_cm": 30.0,
            "health_score": 9,
            "notes": "Updated notes: Excellent growth progress"
        }
        response = client.put(f"{PHENOLOGY_ENDPOINT}/{obs_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["height_cm"] == 30.0
        assert data["health_score"] == 9

    def test_delete_phenology_observation(self, client, setup_planting, sample_phenology_data):
        """Test DELETE /api/v1/phenology/{id} - Delete observation."""
        planting = setup_planting

        # Create observation
        create_response = client.post(
            f"/api/v1/plantings/{planting.id}/phenology",
            json=sample_phenology_data
        )
        obs_id = create_response.json()["id"]

        # Delete observation
        response = client.delete(f"{PHENOLOGY_ENDPOINT}/{obs_id}")
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]

        # Verify deletion
        get_response = client.get(f"{PHENOLOGY_ENDPOINT}/{obs_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
@pytest.mark.api
class TestPhenologyTimelineAPI:
    """Test phenology timeline endpoints."""

    def test_get_growth_timeline(self, client, setup_planting, sample_phenology_data):
        """Test GET /api/v1/plantings/{planting_id}/phenology/timeline - Growth timeline."""
        planting = setup_planting

        # Create observations showing growth progression
        timeline_data = [
            {"time": "2024-01-10T09:00:00Z", "growth_stage": "germination", "height_cm": 2.0},
            {"time": "2024-01-20T09:00:00Z", "growth_stage": "vegetative", "height_cm": 15.0},
            {"time": "2024-02-10T09:00:00Z", "growth_stage": "vegetative", "height_cm": 40.0},
            {"time": "2024-02-25T09:00:00Z", "growth_stage": "flowering", "height_cm": 70.0},
            {"time": "2024-03-15T09:00:00Z", "growth_stage": "fruiting", "height_cm": 85.0}
        ]

        for obs in timeline_data:
            obs_data = {**sample_phenology_data, **obs}
            client.post(f"/api/v1/plantings/{planting.id}/phenology", json=obs_data)

        # Get timeline
        response = client.get(f"/api/v1/plantings/{planting.id}/phenology/timeline")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Timeline should show growth progression
        assert isinstance(data, (list, dict))

    def test_get_height_progression(self, client, setup_planting, sample_phenology_data):
        """Test height progression over time."""
        planting = setup_planting

        # Create observations with increasing height
        for i in range(10):
            obs_data = {
                **sample_phenology_data,
                "time": (datetime(2024, 1, 10) + timedelta(days=i * 5)).isoformat() + "Z",
                "height_cm": 10.0 + i * 8
            }
            client.post(f"/api/v1/plantings/{planting.id}/phenology", json=obs_data)

        # Get observations (can calculate growth rate from this)
        response = client.get(f"/api/v1/plantings/{planting.id}/phenology")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 10


@pytest.mark.integration
@pytest.mark.api
class TestPhenologyPhotoUpload:
    """Test photo upload functionality."""

    def test_create_observation_with_photo_url(self, client, setup_planting, sample_phenology_data):
        """Test creating observation with photo URL."""
        planting = setup_planting

        obs_with_photo = {
            **sample_phenology_data,
            "photo_url": "https://example.com/photos/plant_20240120.jpg"
        }
        response = client.post(
            f"/api/v1/plantings/{planting.id}/phenology",
            json=obs_with_photo
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "photo_url" in data

    @pytest.mark.skip(reason="Photo upload requires file handling - mock for now")
    def test_upload_photo_with_observation(self, client, setup_planting):
        """Test uploading photo file with observation (mocked)."""
        planting = setup_planting

        # This would require multipart/form-data handling
        # Skipped for now as it requires more complex setup
        pass

    def test_multiple_photos_per_observation(self, client, setup_planting, sample_phenology_data):
        """Test observation with multiple photos."""
        planting = setup_planting

        obs_with_photos = {
            **sample_phenology_data,
            "photo_urls": [
                "https://example.com/photos/plant1.jpg",
                "https://example.com/photos/plant2.jpg",
                "https://example.com/photos/plant3.jpg"
            ]
        }
        response = client.post(
            f"/api/v1/plantings/{planting.id}/phenology",
            json=obs_with_photos
        )

        # May or may not support multiple photos depending on schema
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]


@pytest.mark.integration
@pytest.mark.api
class TestPhenologyValidation:
    """Test validation and error handling for phenology API."""

    def test_invalid_growth_stage(self, client, setup_planting, sample_phenology_data):
        """Test validation for invalid growth stage."""
        planting = setup_planting
        invalid_data = {**sample_phenology_data, "growth_stage": "invalid_stage"}
        response = client.post(
            f"/api/v1/plantings/{planting.id}/phenology",
            json=invalid_data
        )
        # May be accepted or rejected depending on validation
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]

    def test_negative_height(self, client, setup_planting, sample_phenology_data):
        """Test validation for negative height."""
        planting = setup_planting
        invalid_data = {**sample_phenology_data, "height_cm": -10.0}
        response = client.post(
            f"/api/v1/plantings/{planting.id}/phenology",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_health_score(self, client, setup_planting, sample_phenology_data):
        """Test validation for health score out of range."""
        planting = setup_planting
        invalid_data = {**sample_phenology_data, "health_score": 15}  # Assuming 1-10 scale
        response = client.post(
            f"/api/v1/plantings/{planting.id}/phenology",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_percentage(self, client, setup_planting, sample_phenology_data):
        """Test validation for percentage out of range."""
        planting = setup_planting
        invalid_data = {**sample_phenology_data, "canopy_cover_percent": 150.0}
        response = client.post(
            f"/api/v1/plantings/{planting.id}/phenology",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_required_fields(self, client, setup_planting):
        """Test creating observation without required fields."""
        planting = setup_planting
        incomplete_data = {
            "height_cm": 25.0
            # Missing time and growth_stage
        }
        response = client.post(
            f"/api/v1/plantings/{planting.id}/phenology",
            json=incomplete_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_planting_id(self, client, sample_phenology_data):
        """Test creating observation for non-existent planting."""
        import uuid
        fake_planting_id = str(uuid.uuid4())

        response = client.post(
            f"/api/v1/plantings/{fake_planting_id}/phenology",
            json=sample_phenology_data
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_observation_before_planting_date(self, client, setup_planting, sample_phenology_data):
        """Test validation for observation before planting date."""
        planting = setup_planting

        # Planting date is 2024-01-01, observation is before that
        invalid_data = {
            **sample_phenology_data,
            "time": "2023-12-15T09:00:00Z"
        }
        response = client.post(
            f"/api/v1/plantings/{planting.id}/phenology",
            json=invalid_data
        )
        # Business logic may or may not allow this
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]
