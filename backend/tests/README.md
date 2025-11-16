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
