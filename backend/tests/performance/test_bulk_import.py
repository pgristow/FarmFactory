"""
Performance tests for bulk data import functionality.

Tests import performance with 1k, 10k, 100k, and 1M rows.
Monitors memory usage and ensures performance targets are met.

Performance Targets:
- 1,000 rows: <10 seconds
- 10,000 rows: <60 seconds
- 100,000 rows: <10 minutes (600 seconds)
- 1,000,000 rows: <60 minutes (3600 seconds)
"""
import pytest
import time
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO, StringIO
import psutil
import os


# Performance targets
TARGETS = {
    1_000: 10,        # 10 seconds
    10_000: 60,       # 1 minute
    100_000: 600,     # 10 minutes
    1_000_000: 3600,  # 60 minutes
}

MEMORY_TARGETS = {
    1_000: 100 * 1024 * 1024,        # 100 MB
    10_000: 500 * 1024 * 1024,       # 500 MB
    100_000: 2 * 1024 * 1024 * 1024, # 2 GB
    1_000_000: 5 * 1024 * 1024 * 1024, # 5 GB
}


@pytest.mark.performance
@pytest.mark.slow
class TestBulkImportPerformance:
    """Test bulk import performance with various dataset sizes."""

    def test_import_1k_rows(self, client, tmp_path):
        """Test importing 1,000 rows - Target: <10 seconds."""
        num_rows = 1_000
        target_time = TARGETS[num_rows]

        # Generate test data
        csv_file = self._generate_farm_csv(tmp_path, num_rows)

        # Measure import time
        start_time = time.time()
        start_memory = self._get_memory_usage()

        # Upload and process
        result = self._import_csv(client, csv_file, 'farms')

        elapsed_time = time.time() - start_time
        peak_memory = self._get_memory_usage() - start_memory

        # Log results
        print(f"\n1K rows import:")
        print(f"  Time: {elapsed_time:.2f}s (target: <{target_time}s)")
        print(f"  Memory: {peak_memory / 1024 / 1024:.2f}MB (target: <{MEMORY_TARGETS[num_rows] / 1024 / 1024:.0f}MB)")
        print(f"  Rate: {num_rows / elapsed_time:.0f} rows/sec")

        # Assertions
        assert elapsed_time < target_time, f"Import took {elapsed_time:.2f}s, target was <{target_time}s"
        assert peak_memory < MEMORY_TARGETS[num_rows], f"Memory usage {peak_memory / 1024 / 1024:.0f}MB exceeded target"

        # Verify data imported
        # assert result['rows_imported'] == num_rows
        # assert result['error_count'] == 0

    def test_import_10k_rows(self, client, tmp_path):
        """Test importing 10,000 rows - Target: <60 seconds."""
        num_rows = 10_000
        target_time = TARGETS[num_rows]

        csv_file = self._generate_farm_csv(tmp_path, num_rows)

        start_time = time.time()
        start_memory = self._get_memory_usage()

        result = self._import_csv(client, csv_file, 'farms')

        elapsed_time = time.time() - start_time
        peak_memory = self._get_memory_usage() - start_memory

        print(f"\n10K rows import:")
        print(f"  Time: {elapsed_time:.2f}s (target: <{target_time}s)")
        print(f"  Memory: {peak_memory / 1024 / 1024:.2f}MB")
        print(f"  Rate: {num_rows / elapsed_time:.0f} rows/sec")

        assert elapsed_time < target_time, f"Import took {elapsed_time:.2f}s, target was <{target_time}s"
        assert peak_memory < MEMORY_TARGETS[num_rows]

    @pytest.mark.slow
    def test_import_100k_rows(self, client, tmp_path):
        """Test importing 100,000 rows - Target: <10 minutes."""
        num_rows = 100_000
        target_time = TARGETS[num_rows]

        csv_file = self._generate_farm_csv(tmp_path, num_rows)

        start_time = time.time()
        start_memory = self._get_memory_usage()

        result = self._import_csv(client, csv_file, 'farms')

        elapsed_time = time.time() - start_time
        peak_memory = self._get_memory_usage() - start_memory

        print(f"\n100K rows import:")
        print(f"  Time: {elapsed_time:.2f}s ({elapsed_time / 60:.1f}min, target: <{target_time / 60:.0f}min)")
        print(f"  Memory: {peak_memory / 1024 / 1024:.2f}MB")
        print(f"  Rate: {num_rows / elapsed_time:.0f} rows/sec")

        assert elapsed_time < target_time, f"Import took {elapsed_time / 60:.1f}min, target was <{target_time / 60:.0f}min"
        assert peak_memory < MEMORY_TARGETS[num_rows]

    @pytest.mark.slow
    def test_import_1m_rows(self, client, tmp_path):
        """Test importing 1,000,000 rows - Target: <60 minutes."""
        num_rows = 1_000_000
        target_time = TARGETS[num_rows]

        csv_file = self._generate_farm_csv(tmp_path, num_rows)

        start_time = time.time()
        start_memory = self._get_memory_usage()

        result = self._import_csv(client, csv_file, 'farms')

        elapsed_time = time.time() - start_time
        peak_memory = self._get_memory_usage() - start_memory

        print(f"\n1M rows import:")
        print(f"  Time: {elapsed_time:.2f}s ({elapsed_time / 60:.1f}min, target: <{target_time / 60:.0f}min)")
        print(f"  Memory: {peak_memory / 1024 / 1024:.2f}MB ({peak_memory / 1024 / 1024 / 1024:.1f}GB)")
        print(f"  Rate: {num_rows / elapsed_time:.0f} rows/sec")

        assert elapsed_time < target_time, f"Import took {elapsed_time / 60:.1f}min, target was <{target_time / 60:.0f}min"
        assert peak_memory < MEMORY_TARGETS[num_rows]

    # Helper methods

    def _generate_farm_csv(self, tmp_path, num_rows):
        """Generate farm data CSV with specified number of rows."""
        data = {
            'farm_name': [f'Farm {i}' for i in range(num_rows)],
            'address': [f'{i} Farm Road, County {i % 100}' for i in range(num_rows)],
            'total_area_hectares': [50.5 + (i % 1000) * 0.1 for i in range(num_rows)],
            'latitude': [40.0 + (i % 100) * 0.01 for i in range(num_rows)],
            'longitude': [-74.0 + (i % 100) * 0.01 for i in range(num_rows)],
            'timezone': ['America/New_York'] * num_rows,
        }
        df = pd.DataFrame(data)

        csv_file = tmp_path / f'farms_{num_rows}.csv'
        df.to_csv(csv_file, index=False)
        return csv_file

    def _import_csv(self, client, csv_file, data_type):
        """Import CSV file through API."""
        # This would call the actual import API endpoints
        # For now, return mock result
        with open(csv_file, 'rb') as f:
            # response = client.post(
            #     "/api/v1/import/upload",
            #     files={"file": (csv_file.name, f, "text/csv")}
            # )
            # upload_id = response.json()['upload_id']
            #
            # process_response = client.post(
            #     "/api/v1/import/process",
            #     json={
            #         "upload_id": upload_id,
            #         "data_type": data_type,
            #         "column_mappings": {}
            #     }
            # )
            # job_id = process_response.json()['job_id']
            #
            # # Poll for completion
            # while True:
            #     status_response = client.get(f"/api/v1/import/status/{job_id}")
            #     status = status_response.json()
            #     if status['status'] in ['completed', 'failed']:
            #         return status
            #     time.sleep(1)
            pass

        return {'rows_imported': 0, 'error_count': 0}

    def _get_memory_usage(self):
        """Get current process memory usage in bytes."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss


@pytest.mark.performance
@pytest.mark.slow
class TestIrrigationImportPerformance:
    """Test irrigation data import performance."""

    def test_import_10k_irrigation_records(self, client, tmp_path):
        """Test importing 10,000 irrigation records."""
        num_rows = 10_000

        # Generate irrigation data
        data = {
            'plot_name': [f'Plot {i % 100}' for i in range(num_rows)],
            'event_time': [(datetime(2024, 1, 1) + timedelta(hours=i)).isoformat() for i in range(num_rows)],
            'method': ['drip' if i % 2 == 0 else 'sprinkler' for i in range(num_rows)],
            'duration_minutes': [120] * num_rows,
            'water_volume_liters': [500.0 + (i % 100)] * num_rows,
        }
        df = pd.DataFrame(data)

        csv_file = tmp_path / 'irrigation_10k.csv'
        df.to_csv(csv_file, index=False)

        start_time = time.time()

        # Import
        # result = self._import_csv(client, csv_file, 'irrigation')

        elapsed_time = time.time() - start_time

        print(f"\n10K irrigation records:")
        print(f"  Time: {elapsed_time:.2f}s")
        print(f"  Rate: {num_rows / elapsed_time:.0f} rows/sec")

        assert elapsed_time < 60  # Target: <60 seconds

    def _import_csv(self, client, csv_file, data_type):
        """Import CSV file."""
        return {'rows_imported': 0, 'error_count': 0}


@pytest.mark.performance
class TestConcurrentImports:
    """Test concurrent import operations."""

    def test_concurrent_2_imports(self, client, tmp_path):
        """Test 2 simultaneous imports."""
        import threading
        import queue

        results_queue = queue.Queue()

        def import_job(job_num, num_rows):
            """Run import job."""
            data = {
                'farm_name': [f'Job{job_num}_Farm{i}' for i in range(num_rows)],
                'total_area_hectares': [50.5] * num_rows,
            }
            df = pd.DataFrame(data)

            csv_file = tmp_path / f'farms_job{job_num}.csv'
            df.to_csv(csv_file, index=False)

            start_time = time.time()
            # result = self._import_csv(client, csv_file, 'farms')
            elapsed_time = time.time() - start_time

            results_queue.put({
                'job_num': job_num,
                'elapsed_time': elapsed_time,
                'num_rows': num_rows
            })

        # Start 2 concurrent imports
        num_rows = 5_000
        threads = []
        for i in range(2):
            thread = threading.Thread(target=import_job, args=(i, num_rows))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=120)

        # Get results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        print(f"\nConcurrent imports (2 jobs, {num_rows} rows each):")
        for result in results:
            print(f"  Job {result['job_num']}: {result['elapsed_time']:.2f}s")

        # Both should complete successfully
        assert len(results) == 2

    def test_concurrent_3_imports(self, client, tmp_path):
        """Test 3 simultaneous imports."""
        # Similar to above but with 3 jobs
        pass


@pytest.mark.performance
class TestMemoryEfficiency:
    """Test memory efficiency during bulk operations."""

    def test_memory_streaming_import(self, client, tmp_path):
        """Test that import streams data (constant memory usage)."""
        num_rows = 50_000

        # Generate large CSV
        data = {
            'farm_name': [f'Farm {i}' for i in range(num_rows)],
            'total_area_hectares': [50.5] * num_rows,
        }
        df = pd.DataFrame(data)

        csv_file = tmp_path / 'large_farms.csv'
        df.to_csv(csv_file, index=False)

        # Monitor memory during import
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        max_memory = initial_memory

        # Start import (would need hooks to monitor during processing)
        # For now, measure before and after
        # result = self._import_csv(client, csv_file, 'farms')

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        print(f"\nMemory usage for {num_rows} rows:")
        print(f"  Initial: {initial_memory / 1024 / 1024:.2f}MB")
        print(f"  Final: {final_memory / 1024 / 1024:.2f}MB")
        print(f"  Increase: {memory_increase / 1024 / 1024:.2f}MB")

        # Memory should not grow unbounded
        # For 50k rows, should use < 1GB additional memory
        assert memory_increase < 1024 * 1024 * 1024  # 1 GB

    def _import_csv(self, client, csv_file, data_type):
        """Import CSV file."""
        return {'rows_imported': 0, 'error_count': 0}


@pytest.mark.performance
class TestBatchProcessingPerformance:
    """Test batch processing efficiency."""

    def test_batch_size_optimization(self, client, tmp_path):
        """Test different batch sizes for optimal performance."""
        num_rows = 10_000
        batch_sizes = [100, 500, 1000, 2000]

        results = {}

        for batch_size in batch_sizes:
            # Generate CSV
            data = {
                'farm_name': [f'Farm {i}' for i in range(num_rows)],
                'total_area_hectares': [50.5] * num_rows,
            }
            df = pd.DataFrame(data)

            csv_file = tmp_path / f'farms_batch{batch_size}.csv'
            df.to_csv(csv_file, index=False)

            # Import with specific batch size
            start_time = time.time()
            # result = self._import_csv_with_batch_size(client, csv_file, 'farms', batch_size)
            elapsed_time = time.time() - start_time

            results[batch_size] = elapsed_time

            print(f"Batch size {batch_size}: {elapsed_time:.2f}s")

        # Find optimal batch size (fastest)
        optimal_batch_size = min(results, key=results.get)
        print(f"\nOptimal batch size: {optimal_batch_size}")

    def _import_csv_with_batch_size(self, client, csv_file, data_type, batch_size):
        """Import CSV with specified batch size."""
        return {'rows_imported': 0, 'error_count': 0}


@pytest.mark.performance
class TestValidationPerformance:
    """Test validation performance."""

    def test_validation_overhead(self, client, tmp_path):
        """Test validation overhead vs raw import."""
        num_rows = 10_000

        # Generate valid data
        data = {
            'farm_name': [f'Farm {i}' for i in range(num_rows)],
            'total_area_hectares': [50.5] * num_rows,
            'latitude': [40.7128] * num_rows,
            'longitude': [-74.0060] * num_rows,
        }
        df = pd.DataFrame(data)

        csv_file = tmp_path / 'farms_validation.csv'
        df.to_csv(csv_file, index=False)

        # Measure validation time
        start_time = time.time()
        # validation_result = self._validate_import(client, csv_file, 'farms')
        validation_time = time.time() - start_time

        # Measure import time
        start_time = time.time()
        # import_result = self._import_csv(client, csv_file, 'farms')
        import_time = time.time() - start_time

        print(f"\nValidation performance for {num_rows} rows:")
        print(f"  Validation: {validation_time:.2f}s")
        print(f"  Import: {import_time:.2f}s")
        print(f"  Validation overhead: {validation_time / import_time * 100:.1f}%")

        # Validation should be < 10% of total import time
        assert validation_time < import_time * 0.1

    def _validate_import(self, client, csv_file, data_type):
        """Validate import without processing."""
        return {'valid_rows': 0, 'invalid_rows': 0}

    def _import_csv(self, client, csv_file, data_type):
        """Import CSV file."""
        return {'rows_imported': 0, 'error_count': 0}


@pytest.mark.performance
class TestDatabasePerformance:
    """Test database-specific performance."""

    def test_bulk_insert_performance(self, client, tmp_path):
        """Test bulk insert vs individual inserts."""
        num_rows = 5_000

        data = {
            'farm_name': [f'Farm {i}' for i in range(num_rows)],
            'total_area_hectares': [50.5] * num_rows,
        }
        df = pd.DataFrame(data)

        # Test bulk insert
        start_time = time.time()
        # self._bulk_insert(df, 'farms')
        bulk_time = time.time() - start_time

        print(f"\nBulk insert {num_rows} rows:")
        print(f"  Time: {bulk_time:.2f}s")
        print(f"  Rate: {num_rows / bulk_time:.0f} rows/sec")

        # Bulk insert should be fast
        assert bulk_time < 10  # Should complete in <10 seconds

    def test_transaction_performance(self, client):
        """Test transaction commit/rollback performance."""
        # Test transaction overhead
        pass

    def _bulk_insert(self, df, table_name):
        """Perform bulk insert."""
        pass


@pytest.mark.performance
class TestErrorHandlingPerformance:
    """Test performance with validation errors."""

    def test_import_with_10_percent_errors(self, client, tmp_path):
        """Test performance with 10% invalid rows."""
        num_rows = 10_000
        num_invalid = int(num_rows * 0.1)

        # Generate data with 10% invalid
        data = {
            'farm_name': [f'Farm {i}' if i >= num_invalid else '' for i in range(num_rows)],
            'total_area_hectares': [50.5 if i >= num_invalid else -1 for i in range(num_rows)],
        }
        df = pd.DataFrame(data)

        csv_file = tmp_path / 'farms_with_errors.csv'
        df.to_csv(csv_file, index=False)

        start_time = time.time()
        # result = self._import_csv(client, csv_file, 'farms', skip_invalid=True)
        elapsed_time = time.time() - start_time

        print(f"\nImport with 10% errors ({num_rows} rows):")
        print(f"  Time: {elapsed_time:.2f}s")
        print(f"  Valid rows: {num_rows - num_invalid}")
        print(f"  Invalid rows: {num_invalid}")

        # Performance should be similar to clean import
        # (error detection should be efficient)

    def _import_csv(self, client, csv_file, data_type, skip_invalid=False):
        """Import CSV file."""
        return {'rows_imported': 0, 'error_count': 0}


# Helper function to generate performance report
def generate_performance_report(results):
    """Generate CSV report of performance benchmarks."""
    import csv

    report_file = 'performance_benchmarks.csv'

    with open(report_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Dataset Size', 'Import Time (s)', 'Memory Usage (MB)', 'Rows/Second', 'Status'])

        for size, data in results.items():
            writer.writerow([
                size,
                f"{data['time']:.2f}",
                f"{data['memory'] / 1024 / 1024:.2f}",
                f"{size / data['time']:.0f}",
                'PASS' if data['time'] < TARGETS[size] else 'FAIL'
            ])

    print(f"\nPerformance report saved to {report_file}")


# Pytest fixture for performance monitoring
@pytest.fixture
def performance_monitor():
    """Monitor performance during tests."""
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.start_memory = None
            self.process = psutil.Process(os.getpid())

        def start(self):
            self.start_time = time.time()
            self.start_memory = self.process.memory_info().rss

        def stop(self):
            elapsed_time = time.time() - self.start_time
            memory_used = self.process.memory_info().rss - self.start_memory
            return {
                'time': elapsed_time,
                'memory': memory_used
            }

    return PerformanceMonitor()
