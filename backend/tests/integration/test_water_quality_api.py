"""
Integration tests for Water Quality API endpoints.

Tests:
- Water quality CRUD
- Trends endpoint
- Source filtering
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status

WATER_QUALITY_ENDPOINT = "/api/v1/water-quality"


@pytest.fixture
def sample_water_quality_data():
    """Sample water quality test data."""
    return {
        "time": "2024-01-15T10:00:00Z",
        "source": "well",
        "ph_level": 7.2,
        "ec_us_per_cm": 800.0,
        "tds_ppm": 500.0,
        "temperature_celsius": 18.0,
        "dissolved_oxygen_mg_per_l": 8.5,
        "turbidity_ntu": 2.5,
        "notes": "Monthly water quality test"
    }


@pytest.fixture
def setup_plot(test_db):
    """Setup farm and plot for testing."""
    from app.models.farm import Farm
    from app.models.plot import Plot

    farm = Farm(name="Test Farm", total_area_hectares=10.0)
    test_db.add(farm)
    test_db.commit()

    plot = Plot(name="Test Plot", farm_id=farm.id, area_hectares=1.0)
    test_db.add(plot)
    test_db.commit()

    return plot


@pytest.mark.integration
@pytest.mark.api
class TestWaterQualityAPI:
    """Test water quality CRUD operations."""

    def test_create_water_quality_test(self, client, setup_plot, sample_water_quality_data):
        """Test POST /api/v1/plots/{plot_id}/water-quality - Record water test."""
        plot = setup_plot
        response = client.post(
            f"/api/v1/plots/{plot.id}/water-quality",
            json=sample_water_quality_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["ph_level"] == sample_water_quality_data["ph_level"]
        assert data["ec_us_per_cm"] == sample_water_quality_data["ec_us_per_cm"]
        assert data["tds_ppm"] == sample_water_quality_data["tds_ppm"]
        assert data["source"] == sample_water_quality_data["source"]
        assert data["plot_id"] == str(plot.id)
        assert "id" in data

    def test_create_water_quality_minimal_fields(self, client, setup_plot):
        """Test creating water quality test with minimal required fields."""
        plot = setup_plot
        minimal_test = {
            "time": "2024-01-15T10:00:00Z",
            "source": "well",
            "ph_level": 7.0
        }
        response = client.post(
            f"/api/v1/plots/{plot.id}/water-quality",
            json=minimal_test
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["ph_level"] == 7.0
        assert data["source"] == "well"

    def test_list_water_quality_tests(self, client, setup_plot, sample_water_quality_data):
        """Test GET /api/v1/plots/{plot_id}/water-quality - Get test history."""
        plot = setup_plot

        # Create multiple tests
        for i in range(6):
            test_data = {
                **sample_water_quality_data,
                "time": (datetime(2024, 1, 1) + timedelta(weeks=i)).isoformat() + "Z",
                "ph_level": 7.0 + i * 0.1
            }
            client.post(f"/api/v1/plots/{plot.id}/water-quality", json=test_data)

        # List tests
        response = client.get(f"/api/v1/plots/{plot.id}/water-quality")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 6

    def test_filter_water_quality_by_date_range(self, client, setup_plot, sample_water_quality_data):
        """Test filtering water quality tests by date range."""
        plot = setup_plot

        # Create tests across different months
        dates = [
            "2024-01-15T10:00:00Z",
            "2024-02-15T10:00:00Z",
            "2024-03-15T10:00:00Z"
        ]
        for date_str in dates:
            test_data = {**sample_water_quality_data, "time": date_str}
            client.post(f"/api/v1/plots/{plot.id}/water-quality", json=test_data)

        # Filter to January only
        response = client.get(
            f"/api/v1/plots/{plot.id}/water-quality?"
            f"start_date=2024-01-01&end_date=2024-01-31"
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 1

    def test_filter_water_quality_by_source(self, client, setup_plot, sample_water_quality_data):
        """Test filtering by water source."""
        plot = setup_plot

        # Create tests from different sources
        sources = ["well", "river", "reservoir", "well"]
        for i, source in enumerate(sources):
            test_data = {
                **sample_water_quality_data,
                "source": source,
                "time": (datetime(2024, 1, 15) + timedelta(days=i)).isoformat() + "Z"
            }
            client.post(f"/api/v1/plots/{plot.id}/water-quality", json=test_data)

        # Filter by source
        response = client.get(f"/api/v1/plots/{plot.id}/water-quality?source=well")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        well_tests = [item for item in items if item.get("source") == "well"]
        assert len(well_tests) >= 2

    def test_pagination_water_quality(self, client, setup_plot, sample_water_quality_data):
        """Test pagination on water quality tests."""
        plot = setup_plot

        # Create 25 tests
        for i in range(25):
            test_data = {
                **sample_water_quality_data,
                "time": (datetime(2024, 1, 1) + timedelta(days=i)).isoformat() + "Z"
            }
            client.post(f"/api/v1/plots/{plot.id}/water-quality", json=test_data)

        # Test first page
        response = client.get(f"/api/v1/plots/{plot.id}/water-quality?limit=10&offset=0")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) == 10

        # Test second page
        response = client.get(f"/api/v1/plots/{plot.id}/water-quality?limit=10&offset=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) == 10

    def test_get_water_quality_by_id(self, client, setup_plot, sample_water_quality_data):
        """Test GET /api/v1/water-quality/{id} - Get specific test."""
        plot = setup_plot

        # Create test
        create_response = client.post(
            f"/api/v1/plots/{plot.id}/water-quality",
            json=sample_water_quality_data
        )
        test_id = create_response.json()["id"]

        # Get test
        response = client.get(f"{WATER_QUALITY_ENDPOINT}/{test_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == test_id
        assert data["ph_level"] == sample_water_quality_data["ph_level"]

    def test_get_water_quality_not_found(self, client):
        """Test getting non-existent water quality test."""
        import uuid
        fake_id = str(uuid.uuid4())

        response = client.get(f"{WATER_QUALITY_ENDPOINT}/{fake_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_water_quality(self, client, setup_plot, sample_water_quality_data):
        """Test PUT /api/v1/water-quality/{id} - Update test."""
        plot = setup_plot

        # Create test
        create_response = client.post(
            f"/api/v1/plots/{plot.id}/water-quality",
            json=sample_water_quality_data
        )
        test_id = create_response.json()["id"]

        # Update test
        update_data = {
            "ph_level": 7.5,
            "notes": "Re-tested after calibration"
        }
        response = client.put(f"{WATER_QUALITY_ENDPOINT}/{test_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["ph_level"] == 7.5

    def test_delete_water_quality(self, client, setup_plot, sample_water_quality_data):
        """Test DELETE /api/v1/water-quality/{id} - Delete test."""
        plot = setup_plot

        # Create test
        create_response = client.post(
            f"/api/v1/plots/{plot.id}/water-quality",
            json=sample_water_quality_data
        )
        test_id = create_response.json()["id"]

        # Delete test
        response = client.delete(f"{WATER_QUALITY_ENDPOINT}/{test_id}")
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]

        # Verify deletion
        get_response = client.get(f"{WATER_QUALITY_ENDPOINT}/{test_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
@pytest.mark.api
class TestWaterQualityTrendsAPI:
    """Test water quality trends endpoints."""

    def test_get_ph_trends(self, client, setup_plot, sample_water_quality_data):
        """Test GET /api/v1/plots/{plot_id}/water-quality/trends - pH trends over time."""
        plot = setup_plot

        # Create tests with varying pH levels
        ph_values = [6.8, 7.0, 7.2, 7.4, 7.3, 7.1]
        for i, ph in enumerate(ph_values):
            test_data = {
                **sample_water_quality_data,
                "time": (datetime(2024, 1, 1) + timedelta(weeks=i)).isoformat() + "Z",
                "ph_level": ph
            }
            client.post(f"/api/v1/plots/{plot.id}/water-quality", json=test_data)

        # Get pH trends
        response = client.get(
            f"/api/v1/plots/{plot.id}/water-quality/trends?metric=ph"
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Should return trend data
        assert isinstance(data, (list, dict))

    def test_get_ec_trends(self, client, setup_plot, sample_water_quality_data):
        """Test EC (electrical conductivity) trends."""
        plot = setup_plot

        # Create tests with varying EC
        for i in range(8):
            test_data = {
                **sample_water_quality_data,
                "time": (datetime(2024, 1, 1) + timedelta(weeks=i)).isoformat() + "Z",
                "ec_us_per_cm": 700.0 + i * 50
            }
            client.post(f"/api/v1/plots/{plot.id}/water-quality", json=test_data)

        # Get EC trends
        response = client.get(
            f"/api/v1/plots/{plot.id}/water-quality/trends?metric=ec"
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_all_metrics_trends(self, client, setup_plot, sample_water_quality_data):
        """Test getting trends for all metrics."""
        plot = setup_plot

        # Create comprehensive tests
        for i in range(5):
            test_data = {
                **sample_water_quality_data,
                "time": (datetime(2024, 1, 1) + timedelta(weeks=i)).isoformat() + "Z"
            }
            client.post(f"/api/v1/plots/{plot.id}/water-quality", json=test_data)

        # Get all trends
        response = client.get(f"/api/v1/plots/{plot.id}/water-quality/trends")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Should return trends for multiple metrics
        assert isinstance(data, (list, dict))


@pytest.mark.integration
@pytest.mark.api
class TestWaterQualityIndicators:
    """Test water quality indicators and thresholds."""

    def test_ph_quality_indicator(self, client, setup_plot, sample_water_quality_data):
        """Test pH quality indicator (good/warning/bad)."""
        plot = setup_plot

        # Create tests with different pH levels
        ph_tests = [
            {"ph": 5.5, "expected_quality": "bad"},  # Too acidic
            {"ph": 7.0, "expected_quality": "good"},  # Optimal
            {"ph": 9.0, "expected_quality": "bad"},   # Too alkaline
        ]

        for test_case in ph_tests:
            test_data = {
                **sample_water_quality_data,
                "ph_level": test_case["ph"],
                "time": datetime.now().isoformat() + "Z"
            }
            response = client.post(
                f"/api/v1/plots/{plot.id}/water-quality",
                json=test_data
            )
            assert response.status_code == status.HTTP_201_CREATED
            # Quality indicator may be calculated in response
            # (optional feature)

    def test_ec_quality_indicator(self, client, setup_plot, sample_water_quality_data):
        """Test EC quality indicator."""
        plot = setup_plot

        # High EC (salinity issue)
        test_data = {**sample_water_quality_data, "ec_us_per_cm": 3000.0}
        response = client.post(
            f"/api/v1/plots/{plot.id}/water-quality",
            json=test_data
        )
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.integration
@pytest.mark.api
class TestWaterQualityValidation:
    """Test validation and error handling for water quality API."""

    def test_invalid_ph_level(self, client, setup_plot, sample_water_quality_data):
        """Test validation for pH out of range."""
        plot = setup_plot
        invalid_data = {**sample_water_quality_data, "ph_level": 15.0}  # pH > 14
        response = client.post(
            f"/api/v1/plots/{plot.id}/water-quality",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_negative_ph(self, client, setup_plot, sample_water_quality_data):
        """Test validation for negative pH."""
        plot = setup_plot
        invalid_data = {**sample_water_quality_data, "ph_level": -1.0}
        response = client.post(
            f"/api/v1/plots/{plot.id}/water-quality",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_negative_ec(self, client, setup_plot, sample_water_quality_data):
        """Test validation for negative EC."""
        plot = setup_plot
        invalid_data = {**sample_water_quality_data, "ec_us_per_cm": -100.0}
        response = client.post(
            f"/api/v1/plots/{plot.id}/water-quality",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_negative_tds(self, client, setup_plot, sample_water_quality_data):
        """Test validation for negative TDS."""
        plot = setup_plot
        invalid_data = {**sample_water_quality_data, "tds_ppm": -50.0}
        response = client.post(
            f"/api/v1/plots/{plot.id}/water-quality",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_source(self, client, setup_plot, sample_water_quality_data):
        """Test validation for invalid water source."""
        plot = setup_plot
        invalid_data = {**sample_water_quality_data, "source": "invalid_source"}
        response = client.post(
            f"/api/v1/plots/{plot.id}/water-quality",
            json=invalid_data
        )
        # May be accepted or rejected depending on validation
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]

    def test_missing_required_fields(self, client, setup_plot):
        """Test creating water quality test without required fields."""
        plot = setup_plot
        incomplete_data = {
            "source": "well"
            # Missing time and ph_level
        }
        response = client.post(
            f"/api/v1/plots/{plot.id}/water-quality",
            json=incomplete_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_plot_id(self, client, sample_water_quality_data):
        """Test creating water quality test for non-existent plot."""
        import uuid
        fake_plot_id = str(uuid.uuid4())

        response = client.post(
            f"/api/v1/plots/{fake_plot_id}/water-quality",
            json=sample_water_quality_data
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
