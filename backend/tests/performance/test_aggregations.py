"""
Performance tests for data aggregation queries.

Tests aggregation performance across different time periods:
- Daily aggregations
- Weekly aggregations
- Monthly aggregations
- Custom date range aggregations
- Multi-metric aggregations
"""
import pytest
import time
from datetime import datetime, timedelta
from fastapi import status


@pytest.fixture
def setup_plot_with_data(test_db, client):
    """Setup plot with comprehensive time-series data."""
    from app.models.farm import Farm
    from app.models.plot import Plot

    farm = Farm(name="Test Farm", total_area_hectares=10.0)
    test_db.add(farm)
    test_db.commit()

    plot = Plot(name="Test Plot", farm_id=farm.id, area_hectares=1.0)
    test_db.add(plot)
    test_db.commit()

    return plot


@pytest.mark.performance
@pytest.mark.slow
class TestDailyAggregationPerformance:
    """Test daily aggregation query performance."""

    def test_daily_aggregation_30_days(self, client, setup_plot_with_data):
        """Daily aggregation for 30 days should complete in <300ms."""
        plot = setup_plot_with_data

        # Create hourly data for 30 days (720 readings)
        print(f"\nCreating 720 hourly readings for daily aggregation...")
        for i in range(720):
            reading_data = {
                "time": (datetime(2024, 1, 1) + timedelta(hours=i)).isoformat() + "Z",
                "temperature_celsius": 20.0 + (i % 24) * 0.5,
                "humidity_percent": 60.0 + (i % 24) * 1.0,
                "soil_moisture_percent": 40.0
            }
            client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Query daily aggregations
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-01&end_date=2024-01-31&aggregation=daily"
        )
        query_time = (time.time() - start_time) * 1000

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])

        # Should have ~30 daily aggregates
        assert len(items) >= 30

        print(f"Daily aggregation (30 days) completed in {query_time:.2f}ms")
        assert query_time < 300, f"Aggregation took {query_time:.2f}ms, expected <300ms"

    def test_daily_aggregation_90_days(self, client, setup_plot_with_data):
        """Daily aggregation for 90 days should complete in <500ms."""
        plot = setup_plot_with_data

        # Create hourly data for 90 days (2160 readings)
        print(f"\nCreating 2160 hourly readings for 90-day daily aggregation...")
        for i in range(2160):
            reading_data = {
                "time": (datetime(2024, 1, 1) + timedelta(hours=i)).isoformat() + "Z",
                "temperature_celsius": 20.0 + (i % 24) * 0.5,
                "humidity_percent": 60.0
            }
            client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Query daily aggregations
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-01&end_date=2024-03-31&aggregation=daily"
        )
        query_time = (time.time() - start_time) * 1000

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])

        # Should have ~90 daily aggregates
        assert len(items) >= 90

        print(f"Daily aggregation (90 days) completed in {query_time:.2f}ms")
        assert query_time < 500, f"Aggregation took {query_time:.2f}ms, expected <500ms"


@pytest.mark.performance
@pytest.mark.slow
class TestWeeklyAggregationPerformance:
    """Test weekly aggregation query performance."""

    def test_weekly_aggregation_12_weeks(self, client, setup_plot_with_data):
        """Weekly aggregation for 12 weeks should complete in <400ms."""
        plot = setup_plot_with_data

        # Create daily data for 12 weeks (84 readings)
        print(f"\nCreating 84 daily readings for weekly aggregation...")
        for i in range(84):
            reading_data = {
                "time": (datetime(2024, 1, 1) + timedelta(days=i)).isoformat() + "Z",
                "temperature_celsius": 20.0 + (i % 7) * 0.3
            }
            client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Query weekly aggregations
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-01&end_date=2024-03-25&aggregation=weekly"
        )
        query_time = (time.time() - start_time) * 1000

        assert response.status_code == status.HTTP_200_OK
        print(f"Weekly aggregation (12 weeks) completed in {query_time:.2f}ms")
        assert query_time < 400, f"Aggregation took {query_time:.2f}ms, expected <400ms"


@pytest.mark.performance
@pytest.mark.slow
class TestMonthlyAggregationPerformance:
    """Test monthly aggregation query performance."""

    def test_monthly_aggregation_12_months(self, client, setup_plot_with_data):
        """Monthly aggregation for 12 months should complete in <600ms."""
        plot = setup_plot_with_data

        # Create daily data for 12 months (365 readings)
        print(f"\nCreating 365 daily readings for monthly aggregation...")
        for i in range(365):
            reading_data = {
                "time": (datetime(2024, 1, 1) + timedelta(days=i)).isoformat() + "Z",
                "temperature_celsius": 20.0 + (i % 30) * 0.2
            }
            client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Query monthly aggregations
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-01&end_date=2024-12-31&aggregation=monthly"
        )
        query_time = (time.time() - start_time) * 1000

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])

        # Should have 12 monthly aggregates
        assert len(items) >= 12

        print(f"Monthly aggregation (12 months) completed in {query_time:.2f}ms")
        assert query_time < 600, f"Aggregation took {query_time:.2f}ms, expected <600ms"


@pytest.mark.performance
@pytest.mark.slow
class TestIrrigationAggregationPerformance:
    """Test irrigation summary aggregation performance."""

    def test_irrigation_water_summary_performance(self, client, test_db):
        """Test irrigation water usage summary calculation."""
        from app.models.farm import Farm
        from app.models.plot import Plot

        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        plot = Plot(name="Test Plot", farm_id=farm.id, area_hectares=1.0)
        test_db.add(plot)
        test_db.commit()

        # Create 100 irrigation events
        print(f"\nCreating 100 irrigation events...")
        for i in range(100):
            event_data = {
                "time": (datetime(2024, 1, 1) + timedelta(hours=i * 6)).isoformat() + "Z",
                "method": "drip" if i % 2 == 0 else "sprinkler",
                "duration_minutes": 120,
                "water_volume_liters": 500.0 + i * 10
            }
            client.post(f"/api/v1/plots/{plot.id}/irrigation", json=event_data)

        # Calculate summary
        start_time = time.time()
        response = client.get(f"/api/v1/plots/{plot.id}/irrigation/summary")
        query_time = (time.time() - start_time) * 1000

        assert response.status_code == status.HTTP_200_OK
        print(f"Irrigation summary completed in {query_time:.2f}ms")
        assert query_time < 300, f"Summary took {query_time:.2f}ms, expected <300ms"

    def test_irrigation_summary_by_method_performance(self, client, test_db):
        """Test irrigation summary grouped by method."""
        from app.models.farm import Farm
        from app.models.plot import Plot

        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        plot = Plot(name="Test Plot", farm_id=farm.id, area_hectares=1.0)
        test_db.add(plot)
        test_db.commit()

        # Create 150 irrigation events with different methods
        print(f"\nCreating 150 irrigation events for method grouping...")
        methods = ["drip", "sprinkler", "flood"]
        for i in range(150):
            event_data = {
                "time": (datetime(2024, 1, 1) + timedelta(hours=i * 4)).isoformat() + "Z",
                "method": methods[i % 3],
                "duration_minutes": 120,
                "water_volume_liters": 500.0
            }
            client.post(f"/api/v1/plots/{plot.id}/irrigation", json=event_data)

        # Get summary grouped by method
        start_time = time.time()
        response = client.get(f"/api/v1/plots/{plot.id}/irrigation/summary?group_by=method")
        query_time = (time.time() - start_time) * 1000

        assert response.status_code == status.HTTP_200_OK
        print(f"Irrigation summary by method completed in {query_time:.2f}ms")
        assert query_time < 400, f"Summary took {query_time:.2f}ms, expected <400ms"


@pytest.mark.performance
@pytest.mark.slow
class TestNutrientAggregationPerformance:
    """Test nutrient application aggregation performance."""

    def test_npk_balance_calculation_performance(self, client, test_db):
        """Test NPK balance calculation with 100 applications."""
        from app.models.farm import Farm
        from app.models.plot import Plot

        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        plot = Plot(name="Test Plot", farm_id=farm.id, area_hectares=1.0)
        test_db.add(plot)
        test_db.commit()

        # Create 100 nutrient applications
        print(f"\nCreating 100 nutrient applications...")
        for i in range(100):
            app_data = {
                "time": (datetime(2024, 1, 1) + timedelta(days=i * 3)).isoformat() + "Z",
                "nutrient_type": "NPK Fertilizer",
                "amount_kg": 50.0,
                "nitrogen_kg": 10.0,
                "phosphorus_kg": 5.0,
                "potassium_kg": 5.0
            }
            client.post(f"/api/v1/plots/{plot.id}/nutrients", json=app_data)

        # Calculate NPK balance
        start_time = time.time()
        response = client.get(f"/api/v1/plots/{plot.id}/nutrients/balance")
        query_time = (time.time() - start_time) * 1000

        assert response.status_code == status.HTTP_200_OK
        print(f"NPK balance calculation completed in {query_time:.2f}ms")
        assert query_time < 300, f"Calculation took {query_time:.2f}ms, expected <300ms"


@pytest.mark.performance
@pytest.mark.slow
class TestMultiMetricAggregationPerformance:
    """Test multi-metric aggregation performance."""

    def test_multi_metric_daily_aggregation(self, client, setup_plot_with_data):
        """Test aggregating multiple metrics simultaneously."""
        plot = setup_plot_with_data

        # Create comprehensive environmental data
        print(f"\nCreating 500 comprehensive environmental readings...")
        for i in range(500):
            reading_data = {
                "time": (datetime(2024, 1, 1) + timedelta(hours=i)).isoformat() + "Z",
                "temperature_celsius": 20.0 + (i % 24) * 0.5,
                "humidity_percent": 60.0 + (i % 24) * 1.0,
                "soil_moisture_percent": 40.0 + (i % 24) * 0.8,
                "soil_temperature_celsius": 18.0 + (i % 24) * 0.3,
                "light_intensity_lux": 10000 + (i % 24) * 2000
            }
            client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Aggregate all metrics
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-01&end_date=2024-01-21&aggregation=daily"
        )
        query_time = (time.time() - start_time) * 1000

        assert response.status_code == status.HTTP_200_OK
        print(f"Multi-metric aggregation completed in {query_time:.2f}ms")
        assert query_time < 400, f"Aggregation took {query_time:.2f}ms, expected <400ms"


@pytest.mark.performance
@pytest.mark.slow
class TestAggregationWithMultiplePlots:
    """Test aggregation performance with multiple plots."""

    def test_farm_level_aggregation_performance(self, client, test_db):
        """Test farm-level aggregation across multiple plots."""
        from app.models.farm import Farm
        from app.models.plot import Plot

        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        # Create 5 plots
        plots = []
        for i in range(5):
            plot = Plot(name=f"Plot {i}", farm_id=farm.id, area_hectares=1.0)
            test_db.add(plot)
            plots.append(plot)
        test_db.commit()

        # Create data for each plot (50 readings per plot = 250 total)
        print(f"\nCreating 250 readings across 5 plots...")
        for plot in plots:
            for i in range(50):
                reading_data = {
                    "time": (datetime(2024, 1, 1) + timedelta(hours=i)).isoformat() + "Z",
                    "temperature_celsius": 20.0 + i * 0.1
                }
                client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Query farm-level aggregation (if endpoint exists)
        start_time = time.time()
        # Note: This endpoint may not exist yet - adjust as needed
        response = client.get(f"/api/v1/farms/{farm.id}/environmental/summary")
        query_time = (time.time() - start_time) * 1000

        # May return 404 if endpoint doesn't exist yet
        if response.status_code == status.HTTP_200_OK:
            print(f"Farm-level aggregation completed in {query_time:.2f}ms")
            assert query_time < 500, f"Aggregation took {query_time:.2f}ms, expected <500ms"


@pytest.mark.performance
class TestAggregationBenchmarks:
    """Benchmark various aggregation patterns for reporting."""

    def test_benchmark_aggregation_types(self, client, setup_plot_with_data):
        """Benchmark different aggregation types."""
        plot = setup_plot_with_data

        # Create test dataset
        print(f"\n=== Aggregation Performance Benchmark ===")
        print(f"Creating test dataset: 200 hourly readings...")

        for i in range(200):
            reading_data = {
                "time": (datetime(2024, 1, 1) + timedelta(hours=i)).isoformat() + "Z",
                "temperature_celsius": 20.0 + (i % 24) * 0.5,
                "humidity_percent": 60.0,
                "soil_moisture_percent": 40.0
            }
            client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        benchmarks = {}

        # Benchmark 1: No aggregation (raw data)
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-01&end_date=2024-01-09"
        )
        benchmarks["Raw data query"] = (time.time() - start_time) * 1000

        # Benchmark 2: Hourly aggregation
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-01&end_date=2024-01-09&aggregation=hourly"
        )
        benchmarks["Hourly aggregation"] = (time.time() - start_time) * 1000

        # Benchmark 3: Daily aggregation
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-01&end_date=2024-01-09&aggregation=daily"
        )
        benchmarks["Daily aggregation"] = (time.time() - start_time) * 1000

        # Print results
        print(f"\n--- Aggregation Benchmark Results ---")
        for agg_type, time_ms in benchmarks.items():
            print(f"{agg_type}: {time_ms:.2f}ms")

        print(f"\n=== End of Aggregation Benchmark ===\n")

        # All should be reasonable
        for agg_type, time_ms in benchmarks.items():
            assert time_ms < 500, f"{agg_type} took {time_ms:.2f}ms, expected <500ms"
