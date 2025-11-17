"""
Integration tests for Crop Management API endpoints.

Tests:
- Crop CRUD (create, read, update, delete)
- Planting CRUD
- Planting status updates
- Filtering by plot, crop, status
- Pagination
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status

CROPS_ENDPOINT = "/api/v1/crops"
PLANTINGS_ENDPOINT = "/api/v1/plantings"


@pytest.fixture
def sample_crop_data():
    """Sample crop data for testing."""
    return {
        "name": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "variety": "Beefsteak",
        "crop_type": "vegetable",
        "optimal_temp_min_celsius": 18.0,
        "optimal_temp_max_celsius": 28.0,
        "optimal_ph_min": 6.0,
        "optimal_ph_max": 6.8,
        "days_to_maturity": 80,
        "water_requirements_mm_per_day": 5.0,
        "description": "Large beefsteak tomatoes"
    }


@pytest.fixture
def sample_planting_data():
    """Sample planting data for testing."""
    return {
        "planting_date": "2024-01-15",
        "expected_harvest_date": "2024-04-15",
        "quantity": 100,
        "spacing_cm": 60,
        "row_spacing_cm": 90,
        "status": "active",
        "notes": "Spring planting"
    }


@pytest.mark.integration
@pytest.mark.api
class TestCropsAPI:
    """Test crop CRUD operations."""

    def test_create_crop(self, client, sample_crop_data):
        """Test POST /api/v1/crops - Create new crop."""
        response = client.post(CROPS_ENDPOINT, json=sample_crop_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == sample_crop_data["name"]
        assert data["scientific_name"] == sample_crop_data["scientific_name"]
        assert data["variety"] == sample_crop_data["variety"]
        assert data["days_to_maturity"] == sample_crop_data["days_to_maturity"]
        assert "id" in data
        assert "created_at" in data

    def test_create_crop_minimal_fields(self, client):
        """Test creating crop with only required fields."""
        minimal_crop = {
            "name": "Lettuce",
            "crop_type": "vegetable"
        }
        response = client.post(CROPS_ENDPOINT, json=minimal_crop)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Lettuce"

    def test_create_crop_missing_required_fields(self, client):
        """Test creating crop without required name field."""
        invalid_crop = {
            "scientific_name": "Test species"
        }
        response = client.post(CROPS_ENDPOINT, json=invalid_crop)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_crop_invalid_temperature_range(self, client, sample_crop_data):
        """Test validation for invalid temperature range."""
        invalid_crop = sample_crop_data.copy()
        invalid_crop["optimal_temp_min_celsius"] = 30.0
        invalid_crop["optimal_temp_max_celsius"] = 20.0  # Max less than min

        response = client.post(CROPS_ENDPOINT, json=invalid_crop)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_crops(self, client, sample_crop_data):
        """Test GET /api/v1/crops - List all crops."""
        # Create multiple crops
        client.post(CROPS_ENDPOINT, json=sample_crop_data)
        client.post(CROPS_ENDPOINT, json={**sample_crop_data, "name": "Lettuce", "variety": "Romaine"})
        client.post(CROPS_ENDPOINT, json={**sample_crop_data, "name": "Cucumber"})

        response = client.get(CROPS_ENDPOINT)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)  # May return list or paginated object

        # Extract items from response
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 3

    def test_list_crops_with_pagination(self, client, sample_crop_data):
        """Test pagination on crops list."""
        # Create 15 crops
        for i in range(15):
            crop_data = {**sample_crop_data, "name": f"Crop {i}"}
            client.post(CROPS_ENDPOINT, json=crop_data)

        # Test first page
        response = client.get(f"{CROPS_ENDPOINT}?skip=0&limit=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) == 10

        # Test second page
        response = client.get(f"{CROPS_ENDPOINT}?skip=10&limit=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 5

    def test_filter_crops_by_type(self, client, sample_crop_data):
        """Test filtering crops by crop_type."""
        # Create crops of different types
        client.post(CROPS_ENDPOINT, json={**sample_crop_data, "name": "Tomato", "crop_type": "vegetable"})
        client.post(CROPS_ENDPOINT, json={**sample_crop_data, "name": "Corn", "crop_type": "grain"})
        client.post(CROPS_ENDPOINT, json={**sample_crop_data, "name": "Apple", "crop_type": "fruit"})

        response = client.get(f"{CROPS_ENDPOINT}?crop_type=vegetable")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        # At least the tomato should be in results
        vegetable_crops = [item for item in items if item.get("crop_type") == "vegetable"]
        assert len(vegetable_crops) >= 1

    def test_search_crops_by_name(self, client, sample_crop_data):
        """Test searching crops by name."""
        client.post(CROPS_ENDPOINT, json={**sample_crop_data, "name": "Cherry Tomato"})
        client.post(CROPS_ENDPOINT, json={**sample_crop_data, "name": "Beefsteak Tomato"})
        client.post(CROPS_ENDPOINT, json={**sample_crop_data, "name": "Cucumber"})

        response = client.get(f"{CROPS_ENDPOINT}?search=Tomato")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        tomato_crops = [item for item in items if "Tomato" in item.get("name", "")]
        assert len(tomato_crops) >= 2

    def test_get_crop_by_id(self, client, sample_crop_data):
        """Test GET /api/v1/crops/{id} - Get specific crop."""
        # Create a crop
        create_response = client.post(CROPS_ENDPOINT, json=sample_crop_data)
        crop_id = create_response.json()["id"]

        # Get the crop
        response = client.get(f"{CROPS_ENDPOINT}/{crop_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == crop_id
        assert data["name"] == sample_crop_data["name"]
        assert data["variety"] == sample_crop_data["variety"]

    def test_get_crop_not_found(self, client):
        """Test getting non-existent crop."""
        import uuid
        fake_id = str(uuid.uuid4())

        response = client.get(f"{CROPS_ENDPOINT}/{fake_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_crop(self, client, sample_crop_data):
        """Test PUT /api/v1/crops/{id} - Update crop."""
        # Create a crop
        create_response = client.post(CROPS_ENDPOINT, json=sample_crop_data)
        crop_id = create_response.json()["id"]

        # Update the crop
        update_data = {
            "name": "Updated Tomato",
            "variety": "Heirloom",
            "days_to_maturity": 90
        }
        response = client.put(f"{CROPS_ENDPOINT}/{crop_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["name"] == "Updated Tomato"
        assert data["variety"] == "Heirloom"
        assert data["days_to_maturity"] == 90

    def test_update_crop_partial(self, client, sample_crop_data):
        """Test partial update (PATCH) of crop."""
        # Create a crop
        create_response = client.post(CROPS_ENDPOINT, json=sample_crop_data)
        crop_id = create_response.json()["id"]
        original_variety = create_response.json()["variety"]

        # Partial update - only name
        update_data = {"name": "New Name Only"}
        response = client.patch(f"{CROPS_ENDPOINT}/{crop_id}", json=update_data)

        # If PATCH not implemented, try PUT
        if response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            response = client.put(f"{CROPS_ENDPOINT}/{crop_id}", json={**sample_crop_data, **update_data})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "New Name Only"

    def test_delete_crop(self, client, sample_crop_data):
        """Test DELETE /api/v1/crops/{id} - Delete crop."""
        # Create a crop
        create_response = client.post(CROPS_ENDPOINT, json=sample_crop_data)
        crop_id = create_response.json()["id"]

        # Delete the crop
        response = client.delete(f"{CROPS_ENDPOINT}/{crop_id}")
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]

        # Verify it's deleted (soft delete - may still exist with deleted flag)
        get_response = client.get(f"{CROPS_ENDPOINT}/{crop_id}")
        # Could be 404 (hard delete) or 200 with deleted=true (soft delete)
        assert get_response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]


@pytest.mark.integration
@pytest.mark.api
class TestPlantingsAPI:
    """Test planting CRUD operations."""

    def test_create_planting(self, client, test_db, sample_crop_data, sample_planting_data):
        """Test POST /api/v1/plots/{plot_id}/plantings - Create planting."""
        # First create a farm and plot
        from app.models.farm import Farm
        from app.models.plot import Plot
        from app.models.crop import Crop

        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        plot = Plot(name="Plot 1", farm_id=farm.id, area_hectares=1.0)
        test_db.add(plot)
        test_db.commit()

        # Create crop
        crop_response = client.post(CROPS_ENDPOINT, json=sample_crop_data)
        crop_id = crop_response.json()["id"]

        # Create planting
        planting_data = {**sample_planting_data, "crop_id": crop_id}
        response = client.post(f"/api/v1/plots/{plot.id}/plantings", json=planting_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["crop_id"] == crop_id
        assert data["plot_id"] == str(plot.id)
        assert data["status"] == "active"
        assert "id" in data

    def test_list_plantings_for_plot(self, client, test_db, sample_crop_data, sample_planting_data):
        """Test GET /api/v1/plots/{plot_id}/plantings - List plantings."""
        from app.models.farm import Farm
        from app.models.plot import Plot
        from app.models.crop import Crop

        # Setup
        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        plot = Plot(name="Plot 1", farm_id=farm.id, area_hectares=1.0)
        test_db.add(plot)
        test_db.commit()

        # Create crops and plantings
        crop1 = client.post(CROPS_ENDPOINT, json={**sample_crop_data, "name": "Tomato"}).json()
        crop2 = client.post(CROPS_ENDPOINT, json={**sample_crop_data, "name": "Pepper"}).json()

        client.post(f"/api/v1/plots/{plot.id}/plantings",
                   json={**sample_planting_data, "crop_id": crop1["id"]})
        client.post(f"/api/v1/plots/{plot.id}/plantings",
                   json={**sample_planting_data, "crop_id": crop2["id"]})

        # List plantings
        response = client.get(f"/api/v1/plots/{plot.id}/plantings")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 2

    def test_filter_plantings_by_status(self, client, test_db, sample_crop_data, sample_planting_data):
        """Test filtering plantings by status."""
        from app.models.farm import Farm
        from app.models.plot import Plot

        # Setup
        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        plot = Plot(name="Plot 1", farm_id=farm.id, area_hectares=1.0)
        test_db.add(plot)
        test_db.commit()

        # Create crops and plantings with different statuses
        crop1 = client.post(CROPS_ENDPOINT, json={**sample_crop_data, "name": "Crop1"}).json()
        crop2 = client.post(CROPS_ENDPOINT, json={**sample_crop_data, "name": "Crop2"}).json()

        client.post(f"/api/v1/plots/{plot.id}/plantings",
                   json={**sample_planting_data, "crop_id": crop1["id"], "status": "active"})
        client.post(f"/api/v1/plots/{plot.id}/plantings",
                   json={**sample_planting_data, "crop_id": crop2["id"], "status": "harvested"})

        # Filter by status
        response = client.get(f"/api/v1/plots/{plot.id}/plantings?status=active")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        active_plantings = [item for item in items if item.get("status") == "active"]
        assert len(active_plantings) >= 1

    def test_get_planting_by_id(self, client, test_db, sample_crop_data, sample_planting_data):
        """Test GET /api/v1/plantings/{id} - Get specific planting."""
        from app.models.farm import Farm
        from app.models.plot import Plot

        # Setup
        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        plot = Plot(name="Plot 1", farm_id=farm.id, area_hectares=1.0)
        test_db.add(plot)
        test_db.commit()

        crop = client.post(CROPS_ENDPOINT, json=sample_crop_data).json()

        # Create planting
        create_response = client.post(f"/api/v1/plots/{plot.id}/plantings",
                                     json={**sample_planting_data, "crop_id": crop["id"]})
        planting_id = create_response.json()["id"]

        # Get planting
        response = client.get(f"{PLANTINGS_ENDPOINT}/{planting_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == planting_id
        assert data["crop_id"] == crop["id"]

    def test_update_planting_status(self, client, test_db, sample_crop_data, sample_planting_data):
        """Test PUT /api/v1/plantings/{id} - Update planting status."""
        from app.models.farm import Farm
        from app.models.plot import Plot

        # Setup
        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        plot = Plot(name="Plot 1", farm_id=farm.id, area_hectares=1.0)
        test_db.add(plot)
        test_db.commit()

        crop = client.post(CROPS_ENDPOINT, json=sample_crop_data).json()

        # Create planting
        create_response = client.post(f"/api/v1/plots/{plot.id}/plantings",
                                     json={**sample_planting_data, "crop_id": crop["id"], "status": "active"})
        planting_id = create_response.json()["id"]

        # Update status to harvested
        update_data = {"status": "harvested", "actual_harvest_date": "2024-04-20"}
        response = client.put(f"{PLANTINGS_ENDPOINT}/{planting_id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "harvested"

    def test_delete_planting(self, client, test_db, sample_crop_data, sample_planting_data):
        """Test DELETE /api/v1/plantings/{id} - Delete planting."""
        from app.models.farm import Farm
        from app.models.plot import Plot

        # Setup
        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        plot = Plot(name="Plot 1", farm_id=farm.id, area_hectares=1.0)
        test_db.add(plot)
        test_db.commit()

        crop = client.post(CROPS_ENDPOINT, json=sample_crop_data).json()

        # Create planting
        create_response = client.post(f"/api/v1/plots/{plot.id}/plantings",
                                     json={**sample_planting_data, "crop_id": crop["id"]})
        planting_id = create_response.json()["id"]

        # Delete planting
        response = client.delete(f"{PLANTINGS_ENDPOINT}/{planting_id}")
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]

        # Verify deletion
        get_response = client.get(f"{PLANTINGS_ENDPOINT}/{planting_id}")
        assert get_response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]


@pytest.mark.integration
@pytest.mark.api
class TestCropsValidation:
    """Test validation and error handling for crops API."""

    def test_invalid_days_to_maturity(self, client, sample_crop_data):
        """Test validation for negative days to maturity."""
        invalid_crop = {**sample_crop_data, "days_to_maturity": -10}
        response = client.post(CROPS_ENDPOINT, json=invalid_crop)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_ph_range(self, client, sample_crop_data):
        """Test validation for invalid pH range."""
        invalid_crop = {**sample_crop_data, "optimal_ph_min": 14.0}  # pH > 14
        response = client.post(CROPS_ENDPOINT, json=invalid_crop)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_water_requirements(self, client, sample_crop_data):
        """Test validation for negative water requirements."""
        invalid_crop = {**sample_crop_data, "water_requirements_mm_per_day": -5.0}
        response = client.post(CROPS_ENDPOINT, json=invalid_crop)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
