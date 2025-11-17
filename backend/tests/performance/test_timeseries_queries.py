"""
Performance tests for time-series queries.

Tests query performance with realistic data volumes:
- 30-day query should complete in <200ms
- 90-day query should complete in <500ms
- Daily aggregation should complete in <300ms
- Concurrent queries should not degrade performance
"""
import pytest
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import status


@pytest.fixture
def setup_plot_with_environmental_data(test_db, client):
    """Setup plot with environmental data for performance testing."""
    from app.models.farm import Farm
    from app.models.plot import Plot

    farm = Farm(name="Test Farm", total_area_hectares=10.0)
    test_db.add(farm)
    test_db.commit()

    plot = Plot(name="Test Plot", farm_id=farm.id, area_hectares=1.0)
    test_db.add(plot)
    test_db.commit()

    return plot


@pytest.fixture
def create_environmental_readings():
    """Factory function to create environmental readings."""
    def _create_readings(client, plot_id, num_readings, start_date=None):
        """Create specified number of environmental readings."""
        if start_date is None:
            start_date = datetime(2024, 1, 1)

        readings = []
        for i in range(num_readings):
            reading_time = start_date + timedelta(hours=i)
            reading_data = {
                "time": reading_time.isoformat() + "Z",
                "temperature_celsius": 20.0 + (i % 24) * 0.5,
                "humidity_percent": 60.0 + (i % 24) * 1.0,
                "soil_moisture_percent": 40.0 + (i % 24) * 0.8,
                "soil_temperature_celsius": 18.0 + (i % 24) * 0.3,
                "light_intensity_lux": 10000 + (i % 24) * 2000
            }
            response = client.post(
                f"/api/v1/plots/{plot_id}/environmental",
                json=reading_data
            )
            if response.status_code == status.HTTP_201_CREATED:
                readings.append(response.json())

        return readings

    return _create_readings


@pytest.mark.performance
@pytest.mark.slow
class TestTimeSeriesQueryPerformance:
    """Test time-series query performance."""

    def test_30day_query_performance(self, client, setup_plot_with_environmental_data, create_environmental_readings):
        """30-day query should complete in <200ms."""
        plot = setup_plot_with_environmental_data

        # Insert 30 days of hourly data (720 rows)
        print(f"\nCreating 720 hourly readings for 30 days...")
        create_environmental_readings(client, plot.id, 720)

        # Query with plot_id and date range
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-01&end_date=2024-01-31"
        )
        query_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 720

        # Assert execution time <200ms
        print(f"30-day query completed in {query_time:.2f}ms")
        assert query_time < 200, f"Query took {query_time:.2f}ms, expected <200ms"

    def test_90day_query_performance(self, client, setup_plot_with_environmental_data, create_environmental_readings):
        """90-day query should complete in <500ms."""
        plot = setup_plot_with_environmental_data

        # Insert 90 days of hourly data (2160 rows)
        print(f"\nCreating 2160 hourly readings for 90 days...")
        create_environmental_readings(client, plot.id, 2160)

        # Query with date range
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-01&end_date=2024-03-31"
        )
        query_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 2160

        # Assert execution time <500ms
        print(f"90-day query completed in {query_time:.2f}ms")
        assert query_time < 500, f"Query took {query_time:.2f}ms, expected <500ms"

    def test_365day_query_performance(self, client, setup_plot_with_environmental_data, create_environmental_readings):
        """365-day query should complete in <2000ms."""
        plot = setup_plot_with_environmental_data

        # Insert 365 days of hourly data (8760 rows)
        print(f"\nCreating 8760 hourly readings for 365 days...")
        create_environmental_readings(client, plot.id, 8760)

        # Query with date range
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-01&end_date=2024-12-31"
        )
        query_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 8760 or "total" in data

        # Assert execution time <2000ms
        print(f"365-day query completed in {query_time:.2f}ms")
        assert query_time < 2000, f"Query took {query_time:.2f}ms, expected <2000ms"

    def test_aggregation_performance(self, client, setup_plot_with_environmental_data, create_environmental_readings):
        """Daily aggregation should complete in <300ms."""
        plot = setup_plot_with_environmental_data

        # Insert 90 days of hourly data
        print(f"\nCreating 2160 hourly readings for aggregation test...")
        create_environmental_readings(client, plot.id, 2160)

        # Aggregate by day
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-01&end_date=2024-03-31&aggregation=daily"
        )
        query_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        assert response.status_code == status.HTTP_200_OK

        # Assert execution time <300ms
        print(f"Daily aggregation completed in {query_time:.2f}ms")
        assert query_time < 300, f"Aggregation took {query_time:.2f}ms, expected <300ms"

    def test_hourly_aggregation_performance(self, client, setup_plot_with_environmental_data, create_environmental_readings):
        """Hourly aggregation on 5-minute data should complete in <500ms."""
        plot = setup_plot_with_environmental_data

        # Insert 30 days of 5-minute data (8640 rows)
        print(f"\nCreating 8640 5-minute readings for hourly aggregation...")
        readings = []
        start_date = datetime(2024, 1, 1)
        for i in range(8640):
            reading_time = start_date + timedelta(minutes=i * 5)
            reading_data = {
                "time": reading_time.isoformat() + "Z",
                "temperature_celsius": 20.0 + (i % 288) * 0.05,
                "humidity_percent": 60.0
            }
            response = client.post(
                f"/api/v1/plots/{plot.id}/environmental",
                json=reading_data
            )
            if response.status_code == status.HTTP_201_CREATED:
                readings.append(response.json())

        # Aggregate by hour
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-01&end_date=2024-01-31&aggregation=hourly"
        )
        query_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        assert response.status_code == status.HTTP_200_OK

        # Assert execution time <500ms
        print(f"Hourly aggregation completed in {query_time:.2f}ms")
        assert query_time < 500, f"Aggregation took {query_time:.2f}ms, expected <500ms"

    def test_concurrent_queries(self, client, setup_plot_with_environmental_data, create_environmental_readings):
        """10 concurrent queries should not degrade performance significantly."""
        plot = setup_plot_with_environmental_data

        # Insert 30 days of data
        print(f"\nCreating 720 readings for concurrent query test...")
        create_environmental_readings(client, plot.id, 720)

        def run_query():
            """Run a single query and return execution time."""
            start_time = time.time()
            response = client.get(
                f"/api/v1/plots/{plot.id}/environmental?"
                f"start_date=2024-01-01&end_date=2024-01-31"
            )
            query_time = (time.time() - start_time) * 1000
            return query_time, response.status_code

        # Run 10 concurrent queries
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(run_query) for _ in range(10)]
            results = [future.result() for future in as_completed(futures)]

        # All queries should succeed
        for query_time, status_code in results:
            assert status_code == status.HTTP_200_OK

        # Calculate average and max query time
        query_times = [r[0] for r in results]
        avg_time = sum(query_times) / len(query_times)
        max_time = max(query_times)

        print(f"Concurrent queries: avg={avg_time:.2f}ms, max={max_time:.2f}ms")

        # Assert all complete in reasonable time
        assert max_time < 300, f"Slowest query took {max_time:.2f}ms, expected <300ms"
        assert avg_time < 250, f"Average query time {avg_time:.2f}ms, expected <250ms"


@pytest.mark.performance
@pytest.mark.slow
class TestIrrigationQueryPerformance:
    """Test irrigation time-series query performance."""

    def test_30day_irrigation_query_performance(self, client, test_db):
        """Test irrigation query performance for 30 days."""
        from app.models.farm import Farm
        from app.models.plot import Plot

        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        plot = Plot(name="Test Plot", farm_id=farm.id, area_hectares=1.0)
        test_db.add(plot)
        test_db.commit()

        # Create 90 irrigation events (3 per day for 30 days)
        print(f"\nCreating 90 irrigation events...")
        for i in range(90):
            event_data = {
                "time": (datetime(2024, 1, 1) + timedelta(hours=i * 8)).isoformat() + "Z",
                "method": "drip",
                "duration_minutes": 120,
                "water_volume_liters": 500.0
            }
            client.post(f"/api/v1/plots/{plot.id}/irrigation", json=event_data)

        # Query 30 days
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/irrigation?"
            f"start_date=2024-01-01&end_date=2024-01-31"
        )
        query_time = (time.time() - start_time) * 1000

        assert response.status_code == status.HTTP_200_OK
        print(f"30-day irrigation query completed in {query_time:.2f}ms")
        assert query_time < 200, f"Query took {query_time:.2f}ms, expected <200ms"

    def test_irrigation_summary_performance(self, client, test_db):
        """Test irrigation summary calculation performance."""
        from app.models.farm import Farm
        from app.models.plot import Plot

        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        plot = Plot(name="Test Plot", farm_id=farm.id, area_hectares=1.0)
        test_db.add(plot)
        test_db.commit()

        # Create 100 irrigation events
        print(f"\nCreating 100 irrigation events for summary...")
        for i in range(100):
            event_data = {
                "time": (datetime(2024, 1, 1) + timedelta(hours=i * 6)).isoformat() + "Z",
                "method": "drip" if i % 2 == 0 else "sprinkler",
                "duration_minutes": 120,
                "water_volume_liters": 500.0 + i * 10
            }
            client.post(f"/api/v1/plots/{plot.id}/irrigation", json=event_data)

        # Query summary
        start_time = time.time()
        response = client.get(f"/api/v1/plots/{plot.id}/irrigation/summary")
        query_time = (time.time() - start_time) * 1000

        assert response.status_code == status.HTTP_200_OK
        print(f"Irrigation summary completed in {query_time:.2f}ms")
        assert query_time < 300, f"Summary took {query_time:.2f}ms, expected <300ms"


@pytest.mark.performance
@pytest.mark.slow
class TestNutrientQueryPerformance:
    """Test nutrient application query performance."""

    def test_nutrient_balance_calculation_performance(self, client, test_db):
        """Test NPK balance calculation performance."""
        from app.models.farm import Farm
        from app.models.plot import Plot

        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        plot = Plot(name="Test Plot", farm_id=farm.id, area_hectares=1.0)
        test_db.add(plot)
        test_db.commit()

        # Create 50 nutrient applications
        print(f"\nCreating 50 nutrient applications...")
        for i in range(50):
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
class TestMultiPlotQueryPerformance:
    """Test query performance with multiple plots."""

    def test_query_performance_with_multiple_plots(self, client, test_db):
        """Test query performance when database has data for multiple plots."""
        from app.models.farm import Farm
        from app.models.plot import Plot

        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        # Create 10 plots
        plots = []
        for i in range(10):
            plot = Plot(name=f"Plot {i}", farm_id=farm.id, area_hectares=1.0)
            test_db.add(plot)
            plots.append(plot)
        test_db.commit()

        # Create data for all plots (100 readings per plot = 1000 total)
        print(f"\nCreating 1000 readings across 10 plots...")
        for plot in plots:
            for i in range(100):
                reading_data = {
                    "time": (datetime(2024, 1, 1) + timedelta(hours=i)).isoformat() + "Z",
                    "temperature_celsius": 20.0 + i * 0.1
                }
                client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Query single plot - should still be fast
        target_plot = plots[5]
        start_time = time.time()
        response = client.get(f"/api/v1/plots/{target_plot.id}/environmental")
        query_time = (time.time() - start_time) * 1000

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 100

        print(f"Single plot query (from 10 plots) completed in {query_time:.2f}ms")
        assert query_time < 250, f"Query took {query_time:.2f}ms, expected <250ms"


@pytest.mark.performance
@pytest.mark.slow
class TestIndexEffectiveness:
    """Test that indexes are being used effectively."""

    def test_filtered_query_performance(self, client, test_db):
        """Test that filtered queries use indexes effectively."""
        from app.models.farm import Farm
        from app.models.plot import Plot

        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        plot = Plot(name="Test Plot", farm_id=farm.id, area_hectares=1.0)
        test_db.add(plot)
        test_db.commit()

        # Create 1000 readings
        print(f"\nCreating 1000 readings for index test...")
        for i in range(1000):
            reading_data = {
                "time": (datetime(2024, 1, 1) + timedelta(hours=i)).isoformat() + "Z",
                "temperature_celsius": 20.0 + i * 0.01
            }
            client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Query with multiple filters (should use indexes)
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-15&end_date=2024-01-20"
        )
        query_time = (time.time() - start_time) * 1000

        assert response.status_code == status.HTTP_200_OK
        print(f"Filtered query completed in {query_time:.2f}ms")
        assert query_time < 200, f"Filtered query took {query_time:.2f}ms, expected <200ms"

    def test_pagination_performance(self, client, test_db):
        """Test that pagination doesn't significantly degrade performance."""
        from app.models.farm import Farm
        from app.models.plot import Plot

        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        plot = Plot(name="Test Plot", farm_id=farm.id, area_hectares=1.0)
        test_db.add(plot)
        test_db.commit()

        # Create 1000 readings
        print(f"\nCreating 1000 readings for pagination test...")
        for i in range(1000):
            reading_data = {
                "time": (datetime(2024, 1, 1) + timedelta(hours=i)).isoformat() + "Z",
                "temperature_celsius": 20.0
            }
            client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        # Query different pages and compare performance
        page_times = []
        for offset in [0, 100, 500, 900]:
            start_time = time.time()
            response = client.get(
                f"/api/v1/plots/{plot.id}/environmental?limit=100&offset={offset}"
            )
            query_time = (time.time() - start_time) * 1000
            page_times.append(query_time)
            assert response.status_code == status.HTTP_200_OK

        avg_time = sum(page_times) / len(page_times)
        max_time = max(page_times)

        print(f"Pagination performance: avg={avg_time:.2f}ms, max={max_time:.2f}ms")
        assert max_time < 250, f"Slowest page took {max_time:.2f}ms, expected <250ms"


@pytest.mark.performance
class TestQueryPerformanceBenchmarks:
    """Benchmark various query patterns for reporting."""

    def test_benchmark_all_query_types(self, client, test_db):
        """Benchmark all major query types and report results."""
        from app.models.farm import Farm
        from app.models.plot import Plot

        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        plot = Plot(name="Test Plot", farm_id=farm.id, area_hectares=1.0)
        test_db.add(plot)
        test_db.commit()

        # Create test data
        print(f"\n=== Performance Benchmark Report ===")
        print(f"Creating test dataset: 720 readings (30 days hourly)...")

        for i in range(720):
            reading_data = {
                "time": (datetime(2024, 1, 1) + timedelta(hours=i)).isoformat() + "Z",
                "temperature_celsius": 20.0 + (i % 24) * 0.5,
                "humidity_percent": 60.0,
                "soil_moisture_percent": 40.0
            }
            client.post(f"/api/v1/plots/{plot.id}/environmental", json=reading_data)

        benchmarks = {}

        # Benchmark 1: Simple list query
        start_time = time.time()
        response = client.get(f"/api/v1/plots/{plot.id}/environmental?limit=100")
        benchmarks["Simple list (100 items)"] = (time.time() - start_time) * 1000

        # Benchmark 2: Date range query
        start_time = time.time()
        response = client.get(
            f"/api/v1/plots/{plot.id}/environmental?"
            f"start_date=2024-01-01&end_date=2024-01-15"
        )
        benchmarks["Date range query (15 days)"] = (time.time() - start_time) * 1000

        # Benchmark 3: Latest reading
        start_time = time.time()
        response = client.get(f"/api/v1/plots/{plot.id}/environmental/latest")
        benchmarks["Latest reading"] = (time.time() - start_time) * 1000

        # Print benchmark results
        print(f"\n--- Benchmark Results ---")
        for query_type, time_ms in benchmarks.items():
            print(f"{query_type}: {time_ms:.2f}ms")

        print(f"\n=== End of Benchmark Report ===\n")

        # All benchmarks should be reasonable
        for query_type, time_ms in benchmarks.items():
            assert time_ms < 500, f"{query_type} took {time_ms:.2f}ms, expected <500ms"
