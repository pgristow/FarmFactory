"""
PyTest configuration and fixtures for FarmFactory backend tests.
"""
import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.config import settings

# Use in-memory SQLite database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db(test_engine) -> Generator:
    """Create a fresh database session for each test."""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(test_db) -> Generator:
    """Create test client with database override."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_farm_data():
    """Sample farm data for testing."""
    return {
        "name": "Test Farm",
        "address": "123 Farm Road, Agricultural Valley",
        "total_area_hectares": 50.5,
        "timezone": "America/New_York",
        "latitude": 40.7128,
        "longitude": -74.0060
    }


@pytest.fixture
def sample_plot_data():
    """Sample plot data for testing."""
    return {
        "name": "North Field",
        "plot_number": "NF-001",
        "area_hectares": 5.5,
        "elevation_meters": 250.0,
        "slope_degrees": 3.5
    }


@pytest.fixture
def sample_crop_data():
    """Sample crop data for testing."""
    return {
        "name": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "variety": "Beefsteak",
        "optimal_temp_min_celsius": 18.0,
        "optimal_temp_max_celsius": 28.0,
        "optimal_ph_min": 6.0,
        "optimal_ph_max": 6.8,
        "days_to_maturity": 80
    }


@pytest.fixture
def sample_irrigation_data():
    """Sample irrigation event data for testing."""
    return {
        "time": "2024-01-15T06:00:00Z",
        "method": "drip",
        "duration_minutes": 120,
        "water_volume_liters": 500.0,
        "water_source": "well",
        "notes": "Morning irrigation"
    }


@pytest.fixture
def sample_nutrient_data():
    """Sample nutrient application data for testing."""
    return {
        "time": "2024-01-20T08:00:00Z",
        "nutrient_type": "Compound Fertilizer",
        "application_method": "broadcast",
        "amount_kg": 50.0,
        "npk_ratio": "10-10-10",
        "nitrogen_kg": 5.0,
        "phosphorus_kg": 5.0,
        "potassium_kg": 5.0,
        "cost_usd": 75.00
    }


@pytest.fixture
def sample_soil_profile_data():
    """Sample soil profile data for testing."""
    return {
        "soil_type": "Loamy Clay",
        "ph_level": 6.8,
        "organic_matter_percent": 3.5,
        "texture": "medium",
        "drainage_class": "well-drained",
        "cec_meq_per_100g": 15.0,
        "test_date": "2024-01-01"
    }


# Performance testing fixtures
@pytest.fixture
def large_dataset():
    """Generate large dataset for performance testing."""
    import pandas as pd
    from datetime import datetime, timedelta

    # Generate 10,000 irrigation records
    base_date = datetime(2024, 1, 1)
    data = []
    for i in range(10000):
        data.append({
            "time": base_date + timedelta(hours=i),
            "plot_name": f"Plot-{i % 10}",
            "method": "drip",
            "duration_minutes": 120,
            "water_volume_liters": 500.0
        })

    return pd.DataFrame(data)


@pytest.fixture
def mock_csv_file(tmp_path):
    """Create a mock CSV file for import testing."""
    import csv

    csv_file = tmp_path / "test_irrigation.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['date_time', 'plot_name', 'method', 'duration_minutes', 'water_volume_liters'])
        writer.writerow(['2024-01-15 06:00', 'North Field', 'drip', '120', '500'])
        writer.writerow(['2024-01-16 06:00', 'South Field', 'sprinkler', '90', '800'])

    return csv_file


@pytest.fixture
def authenticated_client(client):
    """Client with authentication token."""
    # TODO: Implement authentication when auth system is in place
    return client


# Sprint 3 fixtures for Core Data Management
@pytest.fixture
def sample_crop(test_db):
    """Create a sample crop for testing."""
    from app.models.crop import Crop

    crop = Crop(
        name="Test Tomato",
        scientific_name="Solanum lycopersicum",
        variety="Roma VF",
        crop_type="vegetable",
        optimal_temp_min_celsius=18.0,
        optimal_temp_max_celsius=27.0,
        days_to_maturity=75
    )
    test_db.add(crop)
    test_db.commit()
    test_db.refresh(crop)
    return crop


@pytest.fixture
def sample_plot(test_db):
    """Create a sample plot for testing."""
    from app.models.farm import Farm
    from app.models.plot import Plot

    farm = Farm(name="Test Farm", total_area_hectares=10.0)
    test_db.add(farm)
    test_db.commit()

    plot = Plot(name="Test Plot", farm_id=farm.id, area_hectares=1.0)
    test_db.add(plot)
    test_db.commit()
    test_db.refresh(plot)
    return plot


@pytest.fixture
def sample_planting(test_db, sample_plot, sample_crop):
    """Create a sample planting for testing."""
    from app.models.crop import Planting
    from datetime import date

    planting = Planting(
        plot_id=sample_plot.id,
        crop_id=sample_crop.id,
        planting_date=date(2024, 1, 15),
        expected_harvest_date=date(2024, 5, 15),
        quantity=2500,
        status="active"
    )
    test_db.add(planting)
    test_db.commit()
    test_db.refresh(planting)
    return planting


@pytest.fixture
def sample_plot_with_data(test_db, sample_plot):
    """Create plot with 90 days of irrigation data for performance testing."""
    from app.models.irrigation import IrrigationEvent
    from datetime import datetime, timedelta

    # Create 90 irrigation events
    for i in range(90):
        event = IrrigationEvent(
            plot_id=sample_plot.id,
            time=datetime.now() - timedelta(days=i),
            method="drip",
            duration_minutes=120,
            water_volume_liters=500.0
        )
        test_db.add(event)
    test_db.commit()
    return sample_plot


# Markers for test organization
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
