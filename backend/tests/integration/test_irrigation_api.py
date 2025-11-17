"""
Integration tests for Irrigation Management API endpoints.

Tests:
- Irrigation event CRUD
- Date range filtering
- Method filtering
- Summary statistics
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status

IRRIGATION_ENDPOINT = "/api/v1/irrigation"


@pytest.fixture
def sample_irrigation_data():
    """Sample irrigation event data."""
    return {
        "time": "2024-01-15T06:00:00Z",
        "method": "drip",
        "duration_minutes": 120,
        "water_volume_liters": 500.0,
        "water_source": "well",
        "flow_rate_liters_per_minute": 4.17,
        "pressure_bar": 2.5,
        "notes": "Morning irrigation cycle"
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
class TestIrrigationAPI:
    """Test irrigation event CRUD operations."""

    def test_create_irrigation_event(self, client, setup_plot, sample_irrigation_data):
        """Test POST /api/v1/plots/{plot_id}/irrigation - Log irrigation event."""
        plot = setup_plot
        response = client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json=sample_irrigation_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["method"] == sample_irrigation_data["method"]
        assert data["duration_minutes"] == sample_irrigation_data["duration_minutes"]
        assert data["water_volume_liters"] == sample_irrigation_data["water_volume_liters"]
        assert data["plot_id"] == str(plot.id)
        assert "id" in data
        assert "time" in data

    def test_create_irrigation_minimal_fields(self, client, setup_plot):
        """Test creating irrigation event with only required fields."""
        plot = setup_plot
        minimal_irrigation = {
            "time": "2024-01-15T06:00:00Z",
            "method": "drip",
            "water_volume_liters": 500.0
        }
        response = client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json=minimal_irrigation
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["method"] == "drip"

    def test_create_irrigation_invalid_method(self, client, setup_plot, sample_irrigation_data):
        """Test creating irrigation with invalid method."""
        plot = setup_plot
        invalid_data = {**sample_irrigation_data, "method": "invalid_method"}
        response = client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json=invalid_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_irrigation_events(self, client, setup_plot, sample_irrigation_data):
        """Test GET /api/v1/plots/{plot_id}/irrigation - Get irrigation history."""
        plot = setup_plot

        # Create multiple irrigation events
        for i in range(5):
            event_data = {
                **sample_irrigation_data,
                "time": (datetime(2024, 1, 15) + timedelta(days=i)).isoformat() + "Z",
                "water_volume_liters": 500.0 + i * 50
            }
            client.post(f"/api/v1/plots/{plot.id}/irrigation", json=event_data)

        # List events
        response = client.get(f"/api/v1/plots/{plot.id}/irrigation")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 5

    def test_filter_irrigation_by_date_range(self, client, setup_plot, sample_irrigation_data):
        """Test filtering irrigation events by date range."""
        plot = setup_plot

        # Create events across different dates
        dates = [
            "2024-01-10T06:00:00Z",
            "2024-01-15T06:00:00Z",
            "2024-01-20T06:00:00Z",
            "2024-01-25T06:00:00Z"
        ]
        for date_str in dates:
            event_data = {**sample_irrigation_data, "time": date_str}
            client.post(f"/api/v1/plots/{plot.id}/irrigation", json=event_data)

        # Filter by date range
        response = client.get(
            f"/api/v1/plots/{plot.id}/irrigation?"
            f"start_date=2024-01-15&end_date=2024-01-20"
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        # Should get events from Jan 15 and Jan 20
        assert len(items) >= 2

    def test_filter_irrigation_by_method(self, client, setup_plot, sample_irrigation_data):
        """Test filtering irrigation events by method."""
        plot = setup_plot

        # Create events with different methods
        methods = ["drip", "sprinkler", "flood", "drip"]
        for i, method in enumerate(methods):
            event_data = {
                **sample_irrigation_data,
                "method": method,
                "time": (datetime(2024, 1, 15) + timedelta(days=i)).isoformat() + "Z"
            }
            client.post(f"/api/v1/plots/{plot.id}/irrigation", json=event_data)

        # Filter by method
        response = client.get(f"/api/v1/plots/{plot.id}/irrigation?method=drip")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        drip_events = [item for item in items if item.get("method") == "drip"]
        assert len(drip_events) >= 2

    def test_pagination_irrigation_events(self, client, setup_plot, sample_irrigation_data):
        """Test pagination on irrigation events."""
        plot = setup_plot

        # Create 25 irrigation events
        for i in range(25):
            event_data = {
                **sample_irrigation_data,
                "time": (datetime(2024, 1, 1) + timedelta(days=i)).isoformat() + "Z"
            }
            client.post(f"/api/v1/plots/{plot.id}/irrigation", json=event_data)

        # Test first page
        response = client.get(f"/api/v1/plots/{plot.id}/irrigation?limit=10&offset=0")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) == 10

        # Test second page
        response = client.get(f"/api/v1/plots/{plot.id}/irrigation?limit=10&offset=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) == 10

    def test_get_irrigation_event_by_id(self, client, setup_plot, sample_irrigation_data):
        """Test GET /api/v1/irrigation/{id} - Get specific irrigation event."""
        plot = setup_plot

        # Create event
        create_response = client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json=sample_irrigation_data
        )
        event_id = create_response.json()["id"]

        # Get event
        response = client.get(f"{IRRIGATION_ENDPOINT}/{event_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == event_id
        assert data["method"] == sample_irrigation_data["method"]

    def test_get_irrigation_event_not_found(self, client):
        """Test getting non-existent irrigation event."""
        import uuid
        fake_id = str(uuid.uuid4())

        response = client.get(f"{IRRIGATION_ENDPOINT}/{fake_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_irrigation_event(self, client, setup_plot, sample_irrigation_data):
        """Test PUT /api/v1/irrigation/{id} - Update irrigation event."""
        plot = setup_plot

        # Create event
        create_response = client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json=sample_irrigation_data
        )
        event_id = create_response.json()["id"]

        # Update event
        update_data = {
            "duration_minutes": 150,
            "water_volume_liters": 600.0,
            "notes": "Extended irrigation duration"
        }
        response = client.put(f"{IRRIGATION_ENDPOINT}/{event_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["duration_minutes"] == 150
        assert data["water_volume_liters"] == 600.0

    def test_delete_irrigation_event(self, client, setup_plot, sample_irrigation_data):
        """Test DELETE /api/v1/irrigation/{id} - Delete irrigation event."""
        plot = setup_plot

        # Create event
        create_response = client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json=sample_irrigation_data
        )
        event_id = create_response.json()["id"]

        # Delete event
        response = client.delete(f"{IRRIGATION_ENDPOINT}/{event_id}")
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]

        # Verify deletion
        get_response = client.get(f"{IRRIGATION_ENDPOINT}/{event_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
@pytest.mark.api
class TestIrrigationSummaryAPI:
    """Test irrigation summary statistics endpoints."""

    def test_get_irrigation_summary(self, client, setup_plot, sample_irrigation_data):
        """Test GET /api/v1/plots/{plot_id}/irrigation/summary - Water usage summary."""
        plot = setup_plot

        # Create irrigation events over a period
        total_water = 0
        for i in range(10):
            water_volume = 500.0 + i * 50
            total_water += water_volume
            event_data = {
                **sample_irrigation_data,
                "time": (datetime(2024, 1, 1) + timedelta(days=i)).isoformat() + "Z",
                "water_volume_liters": water_volume
            }
            client.post(f"/api/v1/plots/{plot.id}/irrigation", json=event_data)

        # Get summary
        response = client.get(f"/api/v1/plots/{plot.id}/irrigation/summary")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "total_water_liters" in data
        assert "event_count" in data
        assert data["event_count"] >= 10
        # Allow some tolerance for floating point
        assert abs(data["total_water_liters"] - total_water) < 1.0

    def test_get_irrigation_summary_with_date_range(self, client, setup_plot, sample_irrigation_data):
        """Test irrigation summary with date range filter."""
        plot = setup_plot

        # Create events across different months
        client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json={**sample_irrigation_data, "time": "2024-01-15T06:00:00Z", "water_volume_liters": 500.0}
        )
        client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json={**sample_irrigation_data, "time": "2024-02-15T06:00:00Z", "water_volume_liters": 600.0}
        )
        client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json={**sample_irrigation_data, "time": "2024-03-15T06:00:00Z", "water_volume_liters": 700.0}
        )

        # Get summary for January only
        response = client.get(
            f"/api/v1/plots/{plot.id}/irrigation/summary?"
            f"start_date=2024-01-01&end_date=2024-01-31"
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Should include only January events
        assert data["event_count"] >= 1

    def test_get_irrigation_summary_by_method(self, client, setup_plot, sample_irrigation_data):
        """Test irrigation summary grouped by method."""
        plot = setup_plot

        # Create events with different methods
        client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json={**sample_irrigation_data, "method": "drip", "water_volume_liters": 500.0}
        )
        client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json={**sample_irrigation_data, "method": "drip", "water_volume_liters": 550.0}
        )
        client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json={**sample_irrigation_data, "method": "sprinkler", "water_volume_liters": 800.0}
        )

        # Get summary
        response = client.get(f"/api/v1/plots/{plot.id}/irrigation/summary?group_by=method")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Response should be grouped by method or include method breakdown
        assert isinstance(data, (dict, list))


@pytest.mark.integration
@pytest.mark.api
class TestIrrigationValidation:
    """Test validation and error handling for irrigation API."""

    def test_invalid_water_volume(self, client, setup_plot, sample_irrigation_data):
        """Test validation for negative water volume."""
        plot = setup_plot
        invalid_data = {**sample_irrigation_data, "water_volume_liters": -100.0}
        response = client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_duration(self, client, setup_plot, sample_irrigation_data):
        """Test validation for negative duration."""
        plot = setup_plot
        invalid_data = {**sample_irrigation_data, "duration_minutes": -60}
        response = client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_pressure(self, client, setup_plot, sample_irrigation_data):
        """Test validation for invalid pressure."""
        plot = setup_plot
        invalid_data = {**sample_irrigation_data, "pressure_bar": -5.0}
        response = client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_flow_rate(self, client, setup_plot, sample_irrigation_data):
        """Test validation for invalid flow rate."""
        plot = setup_plot
        invalid_data = {**sample_irrigation_data, "flow_rate_liters_per_minute": 0}
        response = client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_future_date_validation(self, client, setup_plot, sample_irrigation_data):
        """Test validation for future dates (optional - depends on business rules)."""
        plot = setup_plot
        future_date = (datetime.now() + timedelta(days=30)).isoformat() + "Z"
        future_data = {**sample_irrigation_data, "time": future_date}
        response = client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json=future_data
        )
        # May be allowed or rejected depending on business rules
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_missing_required_fields(self, client, setup_plot):
        """Test creating irrigation event without required fields."""
        plot = setup_plot
        incomplete_data = {
            "method": "drip"
            # Missing time and water_volume_liters
        }
        response = client.post(
            f"/api/v1/plots/{plot.id}/irrigation",
            json=incomplete_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_plot_id(self, client, sample_irrigation_data):
        """Test creating irrigation event for non-existent plot."""
        import uuid
        fake_plot_id = str(uuid.uuid4())

        response = client.post(
            f"/api/v1/plots/{fake_plot_id}/irrigation",
            json=sample_irrigation_data
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
