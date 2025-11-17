# FarmFactory Backend Testing Documentation

## Overview

This document describes the testing strategy, best practices, and how to run tests for the FarmFactory backend.

## Table of Contents

- [Testing Strategy](#testing-strategy)
- [Test Types](#test-types)
- [Running Tests](#running-tests)
- [Coverage Requirements](#coverage-requirements)
- [Writing Tests](#writing-tests)
- [Best Practices](#best-practices)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

---

## Testing Strategy

FarmFactory uses a comprehensive testing approach with multiple test layers:

1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test API endpoints and component interactions
3. **Performance Tests** - Ensure system handles large datasets efficiently
4. **Security Tests** - Verify security measures are effective

### Testing Pyramid

```
        /\
       /  \        E2E Tests (Few)
      /----\
     /      \      Integration Tests (Some)
    /--------\
   /          \    Unit Tests (Many)
  /------------\
```

We follow the testing pyramid principle: many fast unit tests, some integration tests, and fewer end-to-end tests.

---

## Test Types

### Unit Tests (`tests/unit/`)

Test individual functions, classes, and modules in isolation.

**Location**: `tests/unit/`

**What to test**:
- Model validation and business logic
- Schema validation (Pydantic)
- Utility functions
- Service layer methods

**Example**:
```python
def test_farm_model_creation(test_db, sample_farm_data):
    """Test creating a farm with valid data."""
    farm = Farm(**sample_farm_data)
    test_db.add(farm)
    test_db.commit()

    assert farm.id is not None
    assert farm.name == sample_farm_data["name"]
```

**Run unit tests**:
```bash
pytest tests/unit -v
```

### Integration Tests (`tests/integration/`)

Test API endpoints and interactions between components.

**Location**: `tests/integration/`

**What to test**:
- API endpoints (CRUD operations)
- Request/response validation
- Authentication and authorization
- Database transactions
- Error handling

**Example**:
```python
def test_create_farm_api(client, sample_farm_data):
    """Test creating a farm via API."""
    response = client.post("/api/v1/farms", json=sample_farm_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_farm_data["name"]
```

**Run integration tests**:
```bash
pytest tests/integration -v
```

### Performance Tests (`tests/performance/`)

Test system performance with large datasets and concurrent operations.

**Location**: `tests/performance/`

**What to test**:
- Bulk data import (10k+ rows)
- Time-series query performance
- Database query optimization
- Concurrent request handling
- Memory usage

**Example**:
```python
@pytest.mark.performance
def test_import_10k_records(client):
    """Test importing 10,000 irrigation records."""
    # Generate 10k records
    records = generate_irrigation_records(10000)

    # Measure import time
    start_time = time.time()
    response = client.post("/api/v1/import/irrigation", files={"file": records})
    import_time = time.time() - start_time

    assert response.status_code == 200
    assert import_time < 15  # Should complete in < 15 seconds
```

**Run performance tests**:
```bash
pytest tests/performance -v -m performance
```

---

## Running Tests

### Prerequisites

1. Python 3.10+ installed
2. PostgreSQL with TimescaleDB running
3. Redis running
4. Dependencies installed: `pip install -r requirements.txt`

### Quick Start

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_models.py -v

# Run specific test
pytest tests/unit/test_models.py::test_create_farm -v

# Run tests matching pattern
pytest -k "test_farm" -v
```

### Run Tests by Marker

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Performance tests only
pytest -m performance

# Skip slow tests
pytest -m "not slow"

# Database tests only
pytest -m database
```

### Run with Coverage

```bash
# Run all tests with coverage
pytest --cov=app --cov-report=html

# Run specific tests with coverage
pytest tests/unit --cov=app --cov-report=term-missing

# Generate coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Run in Parallel

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (auto-detect CPU cores)
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

### Watch Mode

```bash
# Install pytest-watch
pip install pytest-watch

# Run tests automatically on file changes
ptw
```

---

## Coverage Requirements

### Coverage Thresholds

- **Overall Coverage**: Minimum 80%
- **Per-file Coverage**: Minimum 70%
- **Branch Coverage**: Minimum 75%

### Checking Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=app --cov-fail-under=80
```

### Coverage Reports

Coverage reports are generated in multiple formats:
- **Terminal**: Shows coverage summary and missing lines
- **HTML**: Interactive report at `htmlcov/index.html`
- **XML**: For CI/CD integration at `coverage.xml`

### Excluded from Coverage

The following are excluded from coverage requirements:
- Test files (`tests/`, `test_*.py`)
- Migration files (`alembic/`)
- Configuration files (`config.py`)
- `__init__.py` files

---

## Writing Tests

### Test Structure

Follow the Arrange-Act-Assert (AAA) pattern:

```python
def test_example():
    # Arrange - Set up test data
    farm_data = {"name": "Test Farm", "area": 50.0}

    # Act - Execute the code being tested
    result = create_farm(farm_data)

    # Assert - Verify the results
    assert result.name == "Test Farm"
    assert result.area == 50.0
```

### Using Fixtures

Fixtures provide reusable test data and setup:

```python
# Use built-in fixtures from conftest.py
def test_with_fixtures(test_db, sample_farm_data):
    farm = Farm(**sample_farm_data)
    test_db.add(farm)
    test_db.commit()

    assert farm.id is not None
```

### Creating Custom Fixtures

```python
@pytest.fixture
def farm_with_plots(test_db, sample_farm_data):
    """Create a farm with 3 plots."""
    farm = Farm(**sample_farm_data)
    test_db.add(farm)
    test_db.commit()

    for i in range(3):
        plot = Plot(name=f"Plot {i}", farm_id=farm.id)
        test_db.add(plot)
    test_db.commit()

    return farm
```

### Parametrized Tests

Test multiple scenarios with one test function:

```python
@pytest.mark.parametrize("area,expected_valid", [
    (50.0, True),
    (-10.0, False),
    (0.0, False),
    (1000000.0, True),
])
def test_farm_area_validation(area, expected_valid):
    if expected_valid:
        farm = Farm(name="Test", area_hectares=area)
        assert farm.area_hectares == area
    else:
        with pytest.raises(ValidationError):
            Farm(name="Test", area_hectares=area)
```

### Testing Exceptions

```python
def test_invalid_farm_raises_error():
    with pytest.raises(ValidationError) as exc_info:
        Farm(name=None)  # Name is required

    assert "name" in str(exc_info.value)
```

### Mocking

Use mocks to isolate code under test:

```python
from unittest.mock import Mock, patch

def test_with_mock():
    with patch('app.services.email_service.send_email') as mock_send:
        mock_send.return_value = True

        result = send_alert_email("test@example.com", "Alert!")

        assert result is True
        mock_send.assert_called_once_with("test@example.com", "Alert!")
```

---

## Best Practices

### General Guidelines

1. **One assertion per test** (when possible)
   - Makes test failures easier to diagnose
   - Tests are more focused and maintainable

2. **Use descriptive test names**
   ```python
   # Good
   def test_create_farm_with_valid_data_returns_201()

   # Bad
   def test_farm()
   ```

3. **Test edge cases**
   - Boundary values
   - Empty inputs
   - Maximum values
   - Invalid data types

4. **Avoid test interdependencies**
   - Each test should be independent
   - Don't rely on test execution order
   - Use fixtures for shared setup

5. **Keep tests fast**
   - Mock external services
   - Use in-memory database for unit tests
   - Minimize test data creation

### Unit Test Best Practices

- Test one thing at a time
- Mock external dependencies
- Use fixtures for test data
- Test both success and failure cases
- Test edge cases and boundaries

### Integration Test Best Practices

- Use test database (not production!)
- Clean up test data after each test
- Test realistic scenarios
- Verify database state changes
- Test API error responses

### Performance Test Best Practices

- Define clear performance targets
- Test with realistic data volumes
- Measure and log execution times
- Test under concurrent load
- Monitor memory usage

---

## CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests
- Daily schedule (integration tests)

### Test Workflow

1. **Backend Tests** (`.github/workflows/backend-tests.yml`)
   - Runs on Python 3.10, 3.11, 3.12
   - Unit tests + Integration tests
   - Code coverage reporting
   - Linting and type checking

2. **Performance Tests**
   - Runs after backend tests pass
   - Performance benchmarks
   - Results uploaded as artifacts

3. **Security Scans**
   - Bandit (security issues)
   - Safety (dependency vulnerabilities)

### Local CI Testing

Run the same checks locally:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
flake8 app
black --check app
isort --check-only app
mypy app

# Run all tests with coverage
pytest --cov=app --cov-report=term-missing

# Run security scans
bandit -r app
safety check
```

---

## Troubleshooting

### Common Issues

#### Tests fail with database connection error

**Problem**: `psycopg2.OperationalError: could not connect to server`

**Solution**:
```bash
# Check if PostgreSQL is running
docker-compose up -d postgres

# Verify DATABASE_URL environment variable
echo $DATABASE_URL

# Check connection
psql $DATABASE_URL -c "SELECT 1"
```

#### Tests pass locally but fail in CI

**Problem**: Different behavior in CI environment

**Solution**:
- Check environment variables in CI configuration
- Ensure test database is properly initialized
- Review CI logs for specific errors
- Run tests in Docker locally to match CI environment

#### Import errors in tests

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
# Install package in editable mode
pip install -e .

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Slow tests

**Problem**: Tests take too long to run

**Solution**:
- Use in-memory SQLite for unit tests
- Mock external services
- Run tests in parallel: `pytest -n auto`
- Use markers to skip slow tests: `pytest -m "not slow"`

#### Coverage not collected properly

**Problem**: Coverage report shows 0% or missing files

**Solution**:
```bash
# Ensure pytest-cov is installed
pip install pytest-cov

# Run with explicit source
pytest --cov=app --cov-report=term-missing

# Check .coveragerc configuration
cat .coveragerc
```

---

## Additional Resources

### Documentation
- [pytest documentation](https://docs.pytest.org/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)

### Tools
- **pytest**: Test framework
- **pytest-cov**: Coverage plugin
- **pytest-asyncio**: Async test support
- **httpx**: Async HTTP client for API testing
- **faker**: Test data generation

### Getting Help

- Check existing tests for examples
- Review conftest.py for available fixtures
- Ask in team Slack channel
- Create issue in GitHub repository

---

## Summary

- Write tests for all new code
- Aim for >80% code coverage
- Run tests before committing: `pytest`
- Fix failing tests immediately
- Keep tests fast and focused
- Use fixtures for reusable test data
- Mock external dependencies
- Test edge cases and error conditions

**Remember**: Good tests are an investment in code quality and maintainability!

---

## Import System Testing (Sprint 2)

### Overview

Sprint 2 introduced a comprehensive data import system with extensive test coverage. The import system includes 400+ tests covering unit, integration, performance, and E2E scenarios.

### Import Test Files

```
tests/
├── unit/
│   ├── test_csv_parser.py         # CSV parsing (30+ tests)
│   ├── test_excel_parser.py       # Excel parsing (25+ tests)
│   ├── test_column_mapper.py      # Column mapping (35+ tests)
│   ├── test_data_validator.py     # Data validation (60+ tests)
│   ├── test_file_formats.py       # File formats (40+ tests)
│   └── test_import_errors.py      # Error handling (50+ tests)
├── integration/
│   ├── test_import_api.py         # Import API endpoints (40+ tests)
│   └── test_import_workflow.py    # Import workflows (30+ tests)
├── performance/
│   └── test_bulk_import.py        # Performance benchmarks (15+ tests)
└── e2e/
    └── test_complete_import.py    # End-to-end workflows (10+ tests)
```

### Running Import Tests

```bash
# All import tests
pytest tests/unit/test_csv_parser.py \
       tests/unit/test_excel_parser.py \
       tests/unit/test_column_mapper.py \
       tests/unit/test_data_validator.py \
       tests/integration/test_import_api.py \
       tests/integration/test_import_workflow.py \
       tests/e2e/test_complete_import.py -v

# Unit tests only
pytest tests/unit/test_csv_parser.py \
       tests/unit/test_excel_parser.py \
       tests/unit/test_column_mapper.py \
       tests/unit/test_data_validator.py -v

# Integration tests
pytest tests/integration/test_import_api.py \
       tests/integration/test_import_workflow.py -v

# Performance tests (SLOW)
pytest tests/performance/test_bulk_import.py -v -m performance

# E2E tests
pytest tests/e2e/test_complete_import.py -v -m e2e

# Quick import tests (skip slow ones)
pytest tests/unit/test_csv_parser.py -m "not slow"
```

### Performance Targets

| Dataset Size | Target Time | Memory Limit | Target Rate |
|--------------|-------------|--------------|-------------|
| 1,000 rows   | <10 seconds | <100 MB      | >100 r/s    |
| 10,000 rows  | <60 seconds | <500 MB      | >166 r/s    |
| 100,000 rows | <10 minutes | <2 GB        | >166 r/s    |
| 1,000,000 rows | <60 minutes | <5 GB      | >277 r/s    |

### Running Performance Benchmarks

```bash
# Run all performance tests (may take hours)
pytest tests/performance/test_bulk_import.py -v

# Run specific benchmark
pytest tests/performance/test_bulk_import.py::TestBulkImportPerformance::test_import_1k_rows -v
pytest tests/performance/test_bulk_import.py::TestBulkImportPerformance::test_import_10k_rows -v

# Skip very slow tests (100k+, 1M rows)
pytest tests/performance/test_bulk_import.py -m "performance and not slow"
```

### Coverage Targets for Import Modules

| Module | Target | Status |
|--------|--------|--------|
| Overall Import System | 85% | Target |
| CSV Parser | 90% | Target |
| Excel Parser | 90% | Target |
| Column Mapper | 85% | Target |
| Data Validator | 90% | Target |
| Import Service | 85% | Target |
| Import API | 80% | Target |

### Generating Import Coverage Report

```bash
# Coverage for import modules only
pytest --cov=app.services.csv_parser \
       --cov=app.services.excel_parser \
       --cov=app.services.column_mapping_service \
       --cov=app.services.validation_service \
       --cov=app.services.import_service \
       --cov=app.api.v1.endpoints.import \
       --cov-report=html \
       --cov-report=term-missing \
       tests/unit/test_csv_parser.py \
       tests/unit/test_excel_parser.py \
       tests/unit/test_column_mapper.py \
       tests/unit/test_data_validator.py \
       tests/integration/test_import_api.py \
       tests/integration/test_import_workflow.py

# Open coverage report
open htmlcov/index.html
```

### Import Test Plan

For detailed import testing strategy, see:
- **Import Test Plan**: `tests/IMPORT_TEST_PLAN.md`
- **Sprint Plan**: `SPRINT_2_PLAN.md` (QA Specialist tasks)

### Known Issues (Import Tests)

1. **Import API endpoints not yet implemented**
   - Tests are written but commented out
   - Will be enabled when backend tasks (BE-102 to BE-109) complete
   - Status: Sprint 2 in progress

2. **Performance tests require actual setup**
   - Need PostgreSQL with real data
   - Need Celery worker running
   - Mock implementations used for now

3. **Frontend component tests pending**
   - React/TypeScript tests (QA-106) not yet created
   - Requires Jest/Vitest setup
   - Planned for Sprint 2 completion

### Test Data for Import Tests

```bash
# Sample test data is generated dynamically using tmp_path fixture
# Example:
def test_import(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("farm_name,area\nFarm 1,50.5")
    # ... test with csv_file
```

### Import Test Markers

```bash
# Unit tests
pytest -m unit tests/unit/test_csv_parser.py

# Integration tests
pytest -m integration tests/integration/test_import_api.py

# Performance tests
pytest -m performance tests/performance/test_bulk_import.py

# E2E tests
pytest -m e2e tests/e2e/test_complete_import.py

# Slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

---

**Import Testing Last Updated**: 2025-11-17
**Sprint**: Sprint 2 - Data Import System
**Test Count**: 335+ import-specific tests
**Coverage Target**: 85% for import modules

---

## Sprint 3: Core Data Management Testing

### Overview

Sprint 3 introduces comprehensive testing for core farm data management, including crops, irrigation, nutrients, environmental data, water quality, phenology observations, and financial tracking. The testing framework includes 200+ tests with a focus on CRUD operations, time-series queries, and performance optimization.

### Sprint 3 Test Files

```
tests/
├── integration/
│   ├── test_crops_api.py              # Crop & Planting CRUD (25+ tests)
│   ├── test_irrigation_api.py         # Irrigation CRUD & summaries (30+ tests)
│   ├── test_nutrients_api.py          # Nutrient applications & NPK balance (25+ tests)
│   ├── test_environmental_api.py      # Environmental readings & aggregations (35+ tests)
│   ├── test_water_quality_api.py      # Water quality tests & trends (20+ tests)
│   ├── test_phenology_api.py          # Phenology observations & timeline (25+ tests)
│   └── test_financial_api.py          # Input costs, harvests & P&L (30+ tests)
├── performance/
│   ├── test_timeseries_queries.py     # Time-series query performance (25+ tests)
│   └── test_aggregations.py           # Aggregation performance (15+ tests)
└── conftest.py                        # Sprint 3 fixtures added
```

### Running Sprint 3 Tests

```bash
# All Sprint 3 integration tests
pytest tests/integration/test_crops_api.py \
       tests/integration/test_irrigation_api.py \
       tests/integration/test_nutrients_api.py \
       tests/integration/test_environmental_api.py \
       tests/integration/test_water_quality_api.py \
       tests/integration/test_phenology_api.py \
       tests/integration/test_financial_api.py -v

# Crop management tests only
pytest tests/integration/test_crops_api.py -v

# Irrigation tests only
pytest tests/integration/test_irrigation_api.py -v

# Performance tests (SLOW)
pytest tests/performance/test_timeseries_queries.py \
       tests/performance/test_aggregations.py -v -m performance

# Quick tests (skip slow performance tests)
pytest tests/integration/ -m "not slow"
```

### Test Categories

#### 1. Crop Management Tests (`test_crops_api.py`)

**Coverage**: Crop and Planting CRUD operations

**Key Test Classes**:
- `TestCropsAPI` - Crop creation, listing, updating, deletion (10+ tests)
- `TestPlantingsAPI` - Planting management and status tracking (8+ tests)
- `TestCropsValidation` - Input validation and error handling (7+ tests)

**Example**:
```bash
# Run crop tests
pytest tests/integration/test_crops_api.py::TestCropsAPI -v

# Run planting tests
pytest tests/integration/test_crops_api.py::TestPlantingsAPI -v
```

#### 2. Irrigation Tests (`test_irrigation_api.py`)

**Coverage**: Irrigation events, water usage summaries, date filtering

**Key Test Classes**:
- `TestIrrigationAPI` - Irrigation event CRUD (12+ tests)
- `TestIrrigationSummaryAPI` - Water usage calculations (8+ tests)
- `TestIrrigationValidation` - Data validation (10+ tests)

**Example**:
```bash
# Run irrigation CRUD tests
pytest tests/integration/test_irrigation_api.py::TestIrrigationAPI -v

# Run summary/aggregation tests
pytest tests/integration/test_irrigation_api.py::TestIrrigationSummaryAPI -v
```

#### 3. Nutrient Management Tests (`test_nutrients_api.py`)

**Coverage**: Nutrient applications, NPK balance calculations

**Key Test Classes**:
- `TestNutrientsAPI` - Nutrient application CRUD (12+ tests)
- `TestNPKBalanceAPI` - NPK balance calculations (7+ tests)
- `TestNutrientCostTracking` - Cost tracking (3+ tests)
- `TestNutrientsValidation` - Validation (7+ tests)

**Example**:
```bash
# Run NPK balance tests
pytest tests/integration/test_nutrients_api.py::TestNPKBalanceAPI -v
```

#### 4. Environmental Data Tests (`test_environmental_api.py`)

**Coverage**: Sensor readings, aggregations, latest values

**Key Test Classes**:
- `TestEnvironmentalAPI` - Environmental data CRUD (15+ tests)
- `TestEnvironmentalLatestAPI` - Latest readings (5+ tests)
- `TestEnvironmentalAggregationAPI` - Time-series aggregations (7+ tests)
- `TestEnvironmentalValidation` - Data validation (8+ tests)

**Example**:
```bash
# Run aggregation tests
pytest tests/integration/test_environmental_api.py::TestEnvironmentalAggregationAPI -v
```

#### 5. Water Quality Tests (`test_water_quality_api.py`)

**Coverage**: Water quality tests, trends, quality indicators

**Key Test Classes**:
- `TestWaterQualityAPI` - Water quality CRUD (12+ tests)
- `TestWaterQualityTrendsAPI` - Trend analysis (6+ tests)
- `TestWaterQualityValidation` - Data validation (8+ tests)

**Example**:
```bash
# Run water quality trends tests
pytest tests/integration/test_water_quality_api.py::TestWaterQualityTrendsAPI -v
```

#### 6. Phenology Tests (`test_phenology_api.py`)

**Coverage**: Growth observations, timelines, photo uploads

**Key Test Classes**:
- `TestPhenologyAPI` - Phenology observation CRUD (13+ tests)
- `TestPhenologyTimelineAPI` - Growth timeline (5+ tests)
- `TestPhenologyPhotoUpload` - Photo handling (3+ tests)
- `TestPhenologyValidation` - Data validation (8+ tests)

**Example**:
```bash
# Run phenology timeline tests
pytest tests/integration/test_phenology_api.py::TestPhenologyTimelineAPI -v
```

#### 7. Financial Data Tests (`test_financial_api.py`)

**Coverage**: Input costs, harvests, P&L, ROI calculations

**Key Test Classes**:
- `TestInputCostsAPI` - Input cost tracking (12+ tests)
- `TestHarvestsAPI` - Harvest records (8+ tests)
- `TestFinancialSummaryAPI` - P&L and ROI (6+ tests)
- `TestFinancialValidation` - Data validation (8+ tests)

**Example**:
```bash
# Run financial summary tests
pytest tests/integration/test_financial_api.py::TestFinancialSummaryAPI -v
```

### Performance Testing

#### Time-Series Query Performance (`test_timeseries_queries.py`)

**Performance Targets**:
- 30-day query: < 200ms
- 90-day query: < 500ms
- 365-day query: < 2000ms
- Daily aggregation: < 300ms
- Concurrent queries: < 300ms max

**Key Test Classes**:
- `TestTimeSeriesQueryPerformance` - Date range queries (5+ tests)
- `TestIrrigationQueryPerformance` - Irrigation queries (2+ tests)
- `TestNutrientQueryPerformance` - Nutrient queries (1+ tests)
- `TestMultiPlotQueryPerformance` - Multi-plot queries (1+ tests)
- `TestIndexEffectiveness` - Index optimization (2+ tests)

**Example**:
```bash
# Run 30-day performance test
pytest tests/performance/test_timeseries_queries.py::TestTimeSeriesQueryPerformance::test_30day_query_performance -v

# Run all time-series performance tests (SLOW)
pytest tests/performance/test_timeseries_queries.py -v -m performance
```

#### Aggregation Performance (`test_aggregations.py`)

**Performance Targets**:
- Daily aggregation (30 days): < 300ms
- Daily aggregation (90 days): < 500ms
- Weekly aggregation (12 weeks): < 400ms
- Monthly aggregation (12 months): < 600ms
- Irrigation summary: < 300ms

**Key Test Classes**:
- `TestDailyAggregationPerformance` - Daily aggregations (2+ tests)
- `TestWeeklyAggregationPerformance` - Weekly aggregations (1+ tests)
- `TestMonthlyAggregationPerformance` - Monthly aggregations (1+ tests)
- `TestIrrigationAggregationPerformance` - Irrigation summaries (2+ tests)
- `TestNutrientAggregationPerformance` - NPK balance (1+ tests)
- `TestMultiMetricAggregationPerformance` - Multi-metric (1+ tests)

**Example**:
```bash
# Run daily aggregation tests
pytest tests/performance/test_aggregations.py::TestDailyAggregationPerformance -v

# Run all aggregation performance tests (SLOW)
pytest tests/performance/test_aggregations.py -v -m performance
```

### Sprint 3 Fixtures (conftest.py)

New fixtures added for Sprint 3:

```python
# Crop management fixtures
@pytest.fixture
def sample_crop(test_db):
    """Create a sample crop for testing."""
    # Returns a Crop instance

@pytest.fixture
def sample_planting(test_db, sample_plot, sample_crop):
    """Create a sample planting for testing."""
    # Returns a Planting instance

# Plot fixture
@pytest.fixture
def sample_plot(test_db):
    """Create a sample plot with farm for testing."""
    # Returns a Plot instance

# Performance testing fixture
@pytest.fixture
def sample_plot_with_data(test_db, sample_plot):
    """Create plot with 90 days of irrigation data."""
    # Returns a Plot with 90 irrigation events
```

### Test Markers for Sprint 3

```bash
# Integration tests
pytest -m integration tests/integration/test_crops_api.py

# API tests
pytest -m api tests/integration/

# Performance tests
pytest -m performance tests/performance/

# Slow tests (performance benchmarks)
pytest -m slow

# Skip slow tests
pytest -m "not slow" tests/integration/
```

### Coverage Targets for Sprint 3 Modules

| Module | Target | Priority |
|--------|--------|----------|
| Crops API | 85% | High |
| Irrigation API | 85% | High |
| Nutrients API | 85% | High |
| Environmental API | 85% | High |
| Water Quality API | 80% | Medium |
| Phenology API | 80% | Medium |
| Financial API | 85% | High |
| Time-Series Services | 80% | High |

### Generating Sprint 3 Coverage Report

```bash
# Coverage for all Sprint 3 modules
pytest --cov=app.api.v1.endpoints.crops \
       --cov=app.api.v1.endpoints.irrigation \
       --cov=app.api.v1.endpoints.nutrients \
       --cov=app.api.v1.endpoints.environmental \
       --cov=app.api.v1.endpoints.water_quality \
       --cov=app.api.v1.endpoints.phenology \
       --cov=app.api.v1.endpoints.financial \
       --cov=app.services.aggregation_service \
       --cov-report=html \
       --cov-report=term-missing \
       tests/integration/

# Open coverage report
open htmlcov/index.html
```

### Known Issues (Sprint 3)

1. **API endpoints not yet fully implemented**
   - Tests are written based on API specifications
   - Some endpoints may return 404 or different status codes
   - Tests will be updated as APIs are implemented
   - Status: Sprint 3 in progress

2. **Performance targets based on PostgreSQL + TimescaleDB**
   - Performance tests assume proper database setup
   - Indexes must be in place (see `004_add_timeseries_indexes.py`)
   - SQLite used in tests will have different performance
   - Real performance should be measured in staging environment

3. **Async test client setup**
   - Some tests use synchronous TestClient
   - May need to switch to AsyncClient for async endpoints
   - Currently using `httpx.AsyncClient` for async tests

4. **Photo upload functionality**
   - Phenology photo upload tests are marked as skipped
   - Requires multipart/form-data handling
   - Will be implemented when file upload is added

### Running All Sprint 3 Tests

```bash
# Quick test suite (integration tests only, skip slow)
pytest tests/integration/ -m "integration and not slow" -v

# Full test suite (including performance tests)
pytest tests/integration/ tests/performance/ -v

# With coverage
pytest tests/integration/ \
       --cov=app.api.v1.endpoints \
       --cov=app.services \
       --cov-report=html \
       --cov-report=term-missing

# Parallel execution (faster)
pytest tests/integration/ -n auto -v
```

### Performance Benchmark Summary

Run comprehensive performance benchmarks:

```bash
# Generate performance report
pytest tests/performance/test_timeseries_queries.py::TestQueryPerformanceBenchmarks::test_benchmark_all_query_types -v
pytest tests/performance/test_aggregations.py::TestAggregationBenchmarks::test_benchmark_aggregation_types -v

# Results are printed to console with timing for:
# - Raw data queries
# - Date range filters
# - Daily/weekly/monthly aggregations
# - Multi-metric aggregations
```

### Test Data Best Practices

1. **Use fixtures for test data** - Leverage conftest.py fixtures
2. **Clean test data** - Tests use database transactions (auto-rollback)
3. **Realistic data volumes** - Performance tests use realistic data sizes
4. **Date consistency** - Use fixed dates (2024-01-01) for reproducibility
5. **Incremental IDs** - Don't rely on specific ID values in assertions

### Debugging Failed Tests

```bash
# Run single test with verbose output
pytest tests/integration/test_crops_api.py::TestCropsAPI::test_create_crop -vv

# Run with print statements visible
pytest tests/integration/test_crops_api.py -s

# Run with debugger on failure
pytest tests/integration/test_crops_api.py --pdb

# Show local variables on failure
pytest tests/integration/test_crops_api.py -l
```

### Next Steps

1. **Implement remaining API endpoints** (Backend team)
2. **Add async support** where needed
3. **Optimize database queries** based on performance test results
4. **Add E2E tests** for complete workflows
5. **Frontend integration tests** (React/TypeScript)

---

**Sprint 3 Testing Last Updated**: 2025-11-17
**Sprint**: Sprint 3 - Core Data Management
**Test Count**: 200+ integration and performance tests
**Coverage Target**: 85% for core modules
**Performance**: Sub-second queries for 90-day time ranges
