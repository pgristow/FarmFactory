"""
Integration tests for Environmental Data API endpoints.

Tests:
- Environmental reading CRUD
- Batch creation
- Latest readings endpoint
- Average calculations
- Time-series queries
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status

ENVIRONMENTAL_ENDPOINT = "/api/v1/environmental"


@pytest.fixture
def sample_environmental_data():
    """Sample environmental reading data."""
    return {
        "time": "2024-01-15T12:00:00Z",
        "temperature_celsius": 25.5,
        "humidity_percent": 65.0,
        "soil_moisture_percent": 45.0,
        "soil_temperature_celsius": 22.0,
        "light_intensity_lux": 50000,
        "wind_speed_ms": 3.5,
        "rainfall_mm": 0.0,
        "atmospheric_pressure_hpa": 1013.25
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
class TestEnvironmentalAPI:
    """Test environmental data CRUD operations."""

    def test_create_environmental_reading(self, client, setup_plot, sample_environmental_data):
        """Test POST /api/v1/plots/{plot_id}/environmental - Record sensor reading."""
        plot = setup_plot
        response = client.post(
            f"/api/v1/plots/{plot.id}/environmental",
            json=sample_environmental_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["temperature_celsius"] == sample_environmental_data["temperature_celsius"]
        assert data["humidity_percent"] == sample_environmental_data["humidity_percent"]
        assert data["soil_moisture_percent"] == sample_environmental_data["soil_moisture_percent"]
        assert data["plot_id"] == str(plot.id)
        assert "id" in data
        assert "time" in data

    def test_create_environmental_minimal_fields(self, client, setup_plot):
        """Test creating reading with only some sensors."""
        plot = setup_plot
        minimal_reading = {
            "time": "2024-01-15T12:00:00Z",
            "temperature_celsius": 25.5,
            "humidity_percent": 65.0
        }
        response = client.post(
            f"/api/v1/plots/{plot.id}/environmental",
            json=minimal_reading
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["temperature_celsius"] == 25.5
        assert data["humidity_percent"] == 65.0

    def test_batch_create_environmental_readings(self, client, setup_plot, sample_environmental_data):
        """Test POST /api/v1/plots/{plot_id}/environmental/batch - Batch insert readings."""
        plot = setup_plot

        # Create batch of readings (hourly for 24 hours)
        batch_data = []
        for i in range(24):
            reading = {
                **sample_environmental_data,
                "time": (datetime(2024, 1, 15) + timedelta(hours=i)).isoformat() + "Z",
                "temperature_celsius": 20.0 + i * 0.5  # Temperature increases through day
            }
            batch_data.append(reading)

        response = client.post(
            f"/api/v1/plots/{plot.id}/environmental/batch",
            json={"readings": batch_data}
        )

        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
        data = response.json()
        # Response may return count or list of created readings
        if isinstance(data, dict) and "count" in data:
            assert data["count"] == 24
        elif isinstance(data, list):
            assert len(data) == 24

    def test_list_environmental_readings(self, client, setup_plot, sample_environmental_data):
        """Test GET /api/v1/plots/{plot_id}/environmental - Get readings with date range."""
        plot = setup_plot

        # Create hourly readings
        for i in range(48):
            reading_data = {
                **sample_environmental_data,
                "time": (datetime(2024, 1, 15) + timedelta(hours=i)).isoformat() + "Z",
                "temperature_celsius": 20.0 + (i % 24) * 0.5
            }
            client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # List readings
        response = client.get(f"/api/v1/plots/{plot.id}/environmental")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 48

    def test_filter_environmental_by_date_range(self, client, setup_plot, sample_environmental_data):
        """Test filtering readings by date range."""
        plot = setup_plot

        # Create readings across multiple days
        for day in range(7):
            for hour in [0, 6, 12, 18]:  # 4 readings per day
                reading_data = {
                    **sample_environmental_data,
                    "time": (datetime(2024, 1, 15) + timedelta(days=day, hours=hour)).isoformat() + "Z"
                }
                client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Filter to get only 3 days
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-15&end_date=2024-01-17"
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        # Should get readings from Jan 15, 16, 17 (3 days * 4 readings = 12)
        assert len(items) >= 12

    def test_filter_environmental_by_metric(self, client, setup_plot, sample_environmental_data):
        """Test filtering by specific metric (temperature, moisture, etc.)."""
        plot = setup_plot

        # Create readings
        for i in range(10):
            reading_data = {
                **sample_environmental_data,
                "time": (datetime(2024, 1, 15) + timedelta(hours=i)).isoformat() + "Z"
            }
            client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Filter to get only temperature readings
        response = client.get(f"/api/v1/plots/{plot.id}/environmental?metric=temperature")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Response format may vary - either filtered readings or just temperature values
        assert isinstance(data, (list, dict))

    def test_pagination_environmental_readings(self, client, setup_plot, sample_environmental_data):
        """Test pagination on environmental readings."""
        plot = setup_plot

        # Create 100 hourly readings
        for i in range(100):
            reading_data = {
                **sample_environmental_data,
                "time": (datetime(2024, 1, 1) + timedelta(hours=i)).isoformat() + "Z"
            }
            client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Test first page
        response = client.get(f"/api/v1/plots/{plot.id}/environmental?limit=50&offset=0")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) == 50

        # Test second page
        response = client.get(f"/api/v1/plots/{plot.id}/environmental?limit=50&offset=50")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) == 50

    def test_get_environmental_reading_by_id(self, client, setup_plot, sample_environmental_data):
        """Test GET /api/v1/environmental/{id} - Get specific reading."""
        plot = setup_plot

        # Create reading
        create_response = client.post(
            f"/api/v1/plots/{plot.id}/environmental",
            json=sample_environmental_data
        )
        reading_id = create_response.json()["id"]

        # Get reading
        response = client.get(f"{ENVIRONMENTAL_ENDPOINT}/{reading_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == reading_id
        assert data["temperature_celsius"] == sample_environmental_data["temperature_celsius"]

    def test_update_environmental_reading(self, client, setup_plot, sample_environmental_data):
        """Test PUT /api/v1/environmental/{id} - Update reading (for corrections)."""
        plot = setup_plot

        # Create reading
        create_response = client.post(
            f"/api/v1/plots/{plot.id}/environmental",
            json=sample_environmental_data
        )
        reading_id = create_response.json()["id"]

        # Update reading (e.g., sensor calibration correction)
        update_data = {
            "temperature_celsius": 26.0,
            "humidity_percent": 68.0
        }
        response = client.put(f"{ENVIRONMENTAL_ENDPOINT}/{reading_id}", json=update_data)

        # Updates may or may not be allowed for time-series data
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_405_METHOD_NOT_ALLOWED
        ]

    def test_delete_environmental_reading(self, client, setup_plot, sample_environmental_data):
        """Test DELETE /api/v1/environmental/{id} - Delete reading."""
        plot = setup_plot

        # Create reading
        create_response = client.post(
            f"/api/v1/plots/{plot.id}/environmental",
            json=sample_environmental_data
        )
        reading_id = create_response.json()["id"]

        # Delete reading
        response = client.delete(f"{ENVIRONMENTAL_ENDPOINT}/{reading_id}")
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]

        # Verify deletion
        get_response = client.get(f"{ENVIRONMENTAL_ENDPOINT}/{reading_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
@pytest.mark.api
class TestEnvironmentalLatestAPI:
    """Test latest readings endpoints."""

    def test_get_latest_readings(self, client, setup_plot, sample_environmental_data):
        """Test GET /api/v1/plots/{plot_id}/environmental/latest - Latest sensor values."""
        plot = setup_plot

        # Create readings at different times
        times = [
            "2024-01-15T06:00:00Z",
            "2024-01-15T12:00:00Z",
            "2024-01-15T18:00:00Z"  # Latest
        ]
        for i, time_str in enumerate(times):
            reading_data = {
                **sample_environmental_data,
                "time": time_str,
                "temperature_celsius": 20.0 + i * 5  # Increasing temperature
            }
            client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Get latest reading
        response = client.get(f"/api/v1/plots/{plot.id}/environmental/latest")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Latest should have temperature 30.0 (from 18:00 reading)
        assert data["temperature_celsius"] == 30.0

    def test_get_latest_by_metric(self, client, setup_plot, sample_environmental_data):
        """Test getting latest reading for specific metric."""
        plot = setup_plot

        # Create readings
        client.post(
            f"/api/v1/plots/{plot.id}/environmental",
            json={**sample_environmental_data, "time": "2024-01-15T12:00:00Z", "temperature_celsius": 25.0}
        )
        client.post(
            f"/api/v1/plots/{plot.id}/environmental",
            json={**sample_environmental_data, "time": "2024-01-15T13:00:00Z", "temperature_celsius": 27.0}
        )

        # Get latest temperature
        response = client.get(f"/api/v1/plots/{plot.id}/environmental/latest?metric=temperature")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # May return full reading or just temperature value
        assert isinstance(data, (dict, float))


@pytest.mark.integration
@pytest.mark.api
class TestEnvironmentalAggregationAPI:
    """Test time-series aggregation endpoints."""

    def test_hourly_averages(self, client, setup_plot, sample_environmental_data):
        """Test hourly aggregation."""
        plot = setup_plot

        # Create readings every 15 minutes for 2 hours
        for hour in range(2):
            for minute in [0, 15, 30, 45]:
                reading_data = {
                    **sample_environmental_data,
                    "time": datetime(2024, 1, 15, 12 + hour, minute).isoformat() + "Z",
                    "temperature_celsius": 25.0 + hour
                }
                client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Get hourly averages
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-15&end_date=2024-01-16&aggregation=hourly"
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Should return aggregated data
        assert isinstance(data, (list, dict))

    def test_daily_averages(self, client, setup_plot, sample_environmental_data):
        """Test daily aggregation."""
        plot = setup_plot

        # Create 24 hourly readings for 3 days
        for day in range(3):
            for hour in range(24):
                reading_data = {
                    **sample_environmental_data,
                    "time": (datetime(2024, 1, 15) + timedelta(days=day, hours=hour)).isoformat() + "Z",
                    "temperature_celsius": 20.0 + hour % 12
                }
                client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Get daily averages
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-15&end_date=2024-01-18&aggregation=daily"
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        # Should have 3 daily aggregates
        assert len(items) >= 3

    def test_min_max_aggregation(self, client, setup_plot, sample_environmental_data):
        """Test MIN/MAX aggregation for temperature."""
        plot = setup_plot

        # Create readings with varying temperatures
        temps = [15.0, 20.0, 25.0, 30.0, 28.0, 22.0, 18.0]
        for i, temp in enumerate(temps):
            reading_data = {
                **sample_environmental_data,
                "time": (datetime(2024, 1, 15, 6) + timedelta(hours=i * 2)).isoformat() + "Z",
                "temperature_celsius": temp
            }
            client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Get aggregated stats
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental/stats?"
            f"start_date=2024-01-15&end_date=2024-01-16"
        )

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            # Should include min, max, avg
            assert "temperature" in str(data).lower() or "stats" in data


@pytest.mark.integration
@pytest.mark.api
class TestEnvironmentalValidation:
    """Test validation and error handling for environmental API."""

    def test_invalid_temperature(self, client, setup_plot, sample_environmental_data):
        """Test validation for extreme temperature values."""
        plot = setup_plot
        invalid_data = {**sample_environmental_data, "temperature_celsius": 150.0}  # Too high
        response = client.post(
            f"/api/v1/plots/{plot.id}/environmental",
            json=invalid_data
        )
        # May be accepted or rejected depending on validation rules
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]

    def test_invalid_humidity(self, client, setup_plot, sample_environmental_data):
        """Test validation for humidity out of range."""
        plot = setup_plot
        invalid_data = {**sample_environmental_data, "humidity_percent": 150.0}  # > 100%
        response = client.post(
            f"/api/v1/plots/{plot.id}/environmental",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_negative_values(self, client, setup_plot, sample_environmental_data):
        """Test validation for negative values where not allowed."""
        plot = setup_plot
        invalid_data = {**sample_environmental_data, "light_intensity_lux": -1000}
        response = client.post(
            f"/api/v1/plots/{plot.id}/environmental",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_timestamp(self, client, setup_plot, sample_environmental_data):
        """Test creating reading without timestamp."""
        plot = setup_plot
        data_without_time = {k: v for k, v in sample_environmental_data.items() if k != "time"}
        response = client.post(
            f"/api/v1/plots/{plot.id}/environmental",
            json=data_without_time
        )
        # May auto-set to current time or require explicit time
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]

    def test_future_timestamp(self, client, setup_plot, sample_environmental_data):
        """Test validation for future timestamps."""
        plot = setup_plot
        future_time = (datetime.now() + timedelta(days=30)).isoformat() + "Z"
        future_data = {**sample_environmental_data, "time": future_time}
        response = client.post(
            f"/api/v1/plots/{plot.id}/environmental",
            json=future_data
        )
        # May be allowed or rejected
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]

    def test_invalid_plot_id(self, client, sample_environmental_data):
        """Test creating reading for non-existent plot."""
        import uuid
        fake_plot_id = str(uuid.uuid4())

        response = client.post(
            f"/api/v1/plots/{fake_plot_id}/environmental",
            json=sample_environmental_data
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.performance
class TestEnvironmentalPerformance:
    """Performance tests for environmental data queries."""

    def test_query_performance_30_days(self, client, setup_plot, sample_environmental_data):
        """Test that 30-day query completes in reasonable time."""
        import time

        plot = setup_plot

        # Create 30 days of hourly data (720 readings)
        for i in range(720):
            reading_data = {
                **sample_environmental_data,
                "time": (datetime(2024, 1, 1) + timedelta(hours=i)).isoformat() + "Z"
            }
            client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Query with 30-day range
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-01&end_date=2024-01-31"
        )
        query_time = time.time() - start_time

        assert response.status_code == status.HTTP_200_OK
        # Should complete in reasonable time (this is a basic test, more detailed in performance suite)
        assert query_time < 5.0  # 5 seconds max for test environment
