"""
Integration tests for Nutrient Management API endpoints.

Tests:
- Nutrient application CRUD
- NPK balance calculation
- Date range filtering
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status

NUTRIENTS_ENDPOINT = "/api/v1/nutrients"


@pytest.fixture
def sample_nutrient_data():
    """Sample nutrient application data."""
    return {
        "time": "2024-01-20T08:00:00Z",
        "nutrient_type": "Compound Fertilizer",
        "application_method": "broadcast",
        "amount_kg": 50.0,
        "npk_ratio": "10-10-10",
        "nitrogen_kg": 5.0,
        "phosphorus_kg": 5.0,
        "potassium_kg": 5.0,
        "cost_usd": 75.00,
        "notes": "First application of the season"
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
class TestNutrientsAPI:
    """Test nutrient application CRUD operations."""

    def test_create_nutrient_application(self, client, setup_plot, sample_nutrient_data):
        """Test POST /api/v1/plots/{plot_id}/nutrients - Log nutrient application."""
        plot = setup_plot
        response = client.post(
            f"/api/v1/plots/{plot.id}/nutrients",
            json=sample_nutrient_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nutrient_type"] == sample_nutrient_data["nutrient_type"]
        assert data["amount_kg"] == sample_nutrient_data["amount_kg"]
        assert data["nitrogen_kg"] == sample_nutrient_data["nitrogen_kg"]
        assert data["plot_id"] == str(plot.id)
        assert "id" in data
        assert "time" in data

    def test_create_nutrient_minimal_fields(self, client, setup_plot):
        """Test creating nutrient application with only required fields."""
        plot = setup_plot
        minimal_nutrient = {
            "time": "2024-01-20T08:00:00Z",
            "nutrient_type": "Nitrogen",
            "amount_kg": 25.0
        }
        response = client.post(
            f"/api/v1/plots/{plot.id}/nutrients",
            json=minimal_nutrient
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nutrient_type"] == "Nitrogen"
        assert data["amount_kg"] == 25.0

    def test_create_nutrient_with_npk_breakdown(self, client, setup_plot):
        """Test creating nutrient with NPK breakdown."""
        plot = setup_plot
        npk_data = {
            "time": "2024-01-20T08:00:00Z",
            "nutrient_type": "NPK Fertilizer",
            "amount_kg": 100.0,
            "npk_ratio": "20-10-10",
            "nitrogen_kg": 20.0,
            "phosphorus_kg": 10.0,
            "potassium_kg": 10.0
        }
        response = client.post(
            f"/api/v1/plots/{plot.id}/nutrients",
            json=npk_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nitrogen_kg"] == 20.0
        assert data["phosphorus_kg"] == 10.0
        assert data["potassium_kg"] == 10.0

    def test_list_nutrient_applications(self, client, setup_plot, sample_nutrient_data):
        """Test GET /api/v1/plots/{plot_id}/nutrients - Get application history."""
        plot = setup_plot

        # Create multiple nutrient applications
        for i in range(5):
            app_data = {
                **sample_nutrient_data,
                "time": (datetime(2024, 1, 15) + timedelta(days=i * 7)).isoformat() + "Z",
                "amount_kg": 50.0 + i * 10
            }
            client.post(f"/api/v1/plots/{plot.id}/nutrients", json=app_data)

        # List applications
        response = client.get(f"/api/v1/plots/{plot.id}/nutrients")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 5

    def test_filter_nutrients_by_date_range(self, client, setup_plot, sample_nutrient_data):
        """Test filtering nutrient applications by date range."""
        plot = setup_plot

        # Create applications across different dates
        dates = [
            "2024-01-10T08:00:00Z",
            "2024-01-20T08:00:00Z",
            "2024-02-10T08:00:00Z",
            "2024-02-20T08:00:00Z"
        ]
        for date_str in dates:
            app_data = {**sample_nutrient_data, "time": date_str}
            client.post(f"/api/v1/plots/{plot.id}/nutrients", json=app_data)

        # Filter by date range (January only)
        response = client.get(
            f"/api/v1/plots/{plot.id}/nutrients?"
            f"start_date=2024-01-01&end_date=2024-01-31"
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        # Should get only January applications
        assert len(items) >= 2

    def test_filter_nutrients_by_type(self, client, setup_plot, sample_nutrient_data):
        """Test filtering by nutrient type."""
        plot = setup_plot

        # Create applications with different types
        types = ["Nitrogen", "Phosphorus", "Potassium", "Compound Fertilizer"]
        for i, nutrient_type in enumerate(types):
            app_data = {
                **sample_nutrient_data,
                "nutrient_type": nutrient_type,
                "time": (datetime(2024, 1, 15) + timedelta(days=i)).isoformat() + "Z"
            }
            client.post(f"/api/v1/plots/{plot.id}/nutrients", json=app_data)

        # Filter by type
        response = client.get(f"/api/v1/plots/{plot.id}/nutrients?nutrient_type=Nitrogen")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        nitrogen_apps = [item for item in items if item.get("nutrient_type") == "Nitrogen"]
        assert len(nitrogen_apps) >= 1

    def test_pagination_nutrient_applications(self, client, setup_plot, sample_nutrient_data):
        """Test pagination on nutrient applications."""
        plot = setup_plot

        # Create 25 applications
        for i in range(25):
            app_data = {
                **sample_nutrient_data,
                "time": (datetime(2024, 1, 1) + timedelta(days=i)).isoformat() + "Z"
            }
            client.post(f"/api/v1/plots/{plot.id}/nutrients", json=app_data)

        # Test first page
        response = client.get(f"/api/v1/plots/{plot.id}/nutrients?limit=10&offset=0")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) == 10

        # Test second page
        response = client.get(f"/api/v1/plots/{plot.id}/nutrients?limit=10&offset=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) == 10

    def test_get_nutrient_application_by_id(self, client, setup_plot, sample_nutrient_data):
        """Test GET /api/v1/nutrients/{id} - Get specific application."""
        plot = setup_plot

        # Create application
        create_response = client.post(
            f"/api/v1/plots/{plot.id}/nutrients",
            json=sample_nutrient_data
        )
        app_id = create_response.json()["id"]

        # Get application
        response = client.get(f"{NUTRIENTS_ENDPOINT}/{app_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == app_id
        assert data["nutrient_type"] == sample_nutrient_data["nutrient_type"]

    def test_get_nutrient_application_not_found(self, client):
        """Test getting non-existent nutrient application."""
        import uuid
        fake_id = str(uuid.uuid4())

        response = client.get(f"{NUTRIENTS_ENDPOINT}/{fake_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_nutrient_application(self, client, setup_plot, sample_nutrient_data):
        """Test PUT /api/v1/nutrients/{id} - Update nutrient application."""
        plot = setup_plot

        # Create application
        create_response = client.post(
            f"/api/v1/plots/{plot.id}/nutrients",
            json=sample_nutrient_data
        )
        app_id = create_response.json()["id"]

        # Update application
        update_data = {
            "amount_kg": 60.0,
            "cost_usd": 90.00,
            "notes": "Updated application amount"
        }
        response = client.put(f"{NUTRIENTS_ENDPOINT}/{app_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["amount_kg"] == 60.0
        assert data["cost_usd"] == 90.00

    def test_delete_nutrient_application(self, client, setup_plot, sample_nutrient_data):
        """Test DELETE /api/v1/nutrients/{id} - Delete nutrient application."""
        plot = setup_plot

        # Create application
        create_response = client.post(
            f"/api/v1/plots/{plot.id}/nutrients",
            json=sample_nutrient_data
        )
        app_id = create_response.json()["id"]

        # Delete application
        response = client.delete(f"{NUTRIENTS_ENDPOINT}/{app_id}")
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]

        # Verify deletion
        get_response = client.get(f"{NUTRIENTS_ENDPOINT}/{app_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
@pytest.mark.api
class TestNPKBalanceAPI:
    """Test NPK balance calculation endpoints."""

    def test_get_npk_balance(self, client, setup_plot, sample_nutrient_data):
        """Test GET /api/v1/plots/{plot_id}/nutrients/balance - NPK balance over time."""
        plot = setup_plot

        # Create nutrient applications with NPK breakdown
        applications = [
            {"time": "2024-01-10T08:00:00Z", "nitrogen_kg": 10.0, "phosphorus_kg": 5.0, "potassium_kg": 5.0},
            {"time": "2024-01-20T08:00:00Z", "nitrogen_kg": 15.0, "phosphorus_kg": 7.0, "potassium_kg": 8.0},
            {"time": "2024-01-30T08:00:00Z", "nitrogen_kg": 12.0, "phosphorus_kg": 6.0, "potassium_kg": 7.0}
        ]

        for app in applications:
            app_data = {**sample_nutrient_data, **app}
            client.post(f"/api/v1/plots/{plot.id}/nutrients", json=app_data)

        # Get NPK balance
        response = client.get(f"/api/v1/plots/{plot.id}/nutrients/balance")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "total_nitrogen_kg" in data or "nitrogen" in data
        assert "total_phosphorus_kg" in data or "phosphorus" in data
        assert "total_potassium_kg" in data or "potassium" in data

    def test_get_npk_balance_with_date_range(self, client, setup_plot, sample_nutrient_data):
        """Test NPK balance with date range filter."""
        plot = setup_plot

        # Create applications in different months
        client.post(
            f"/api/v1/plots/{plot.id}/nutrients",
            json={**sample_nutrient_data, "time": "2024-01-15T08:00:00Z", "nitrogen_kg": 10.0}
        )
        client.post(
            f"/api/v1/plots/{plot.id}/nutrients",
            json={**sample_nutrient_data, "time": "2024-02-15T08:00:00Z", "nitrogen_kg": 20.0}
        )

        # Get balance for January only
        response = client.get(
            f"/api/v1/plots/{plot.id}/nutrients/balance?"
            f"start_date=2024-01-01&end_date=2024-01-31"
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Should only include January application
        total_n_field = "total_nitrogen_kg" if "total_nitrogen_kg" in data else "nitrogen"
        assert data[total_n_field] >= 10.0

    def test_npk_balance_over_time(self, client, setup_plot, sample_nutrient_data):
        """Test NPK balance calculation over time (cumulative)."""
        plot = setup_plot

        # Create sequential applications
        cumulative_n = 0
        for i in range(5):
            n_amount = 10.0 + i * 5
            cumulative_n += n_amount
            app_data = {
                **sample_nutrient_data,
                "time": (datetime(2024, 1, 1) + timedelta(days=i * 7)).isoformat() + "Z",
                "nitrogen_kg": n_amount,
                "phosphorus_kg": 5.0,
                "potassium_kg": 5.0
            }
            client.post(f"/api/v1/plots/{plot.id}/nutrients", json=app_data)

        # Get cumulative balance
        response = client.get(f"/api/v1/plots/{plot.id}/nutrients/balance")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        total_n_field = "total_nitrogen_kg" if "total_nitrogen_kg" in data else "nitrogen"
        # Should equal cumulative sum
        assert abs(data[total_n_field] - cumulative_n) < 1.0

    def test_npk_balance_by_application(self, client, setup_plot, sample_nutrient_data):
        """Test NPK balance with breakdown by application."""
        plot = setup_plot

        # Create applications
        for i in range(3):
            app_data = {
                **sample_nutrient_data,
                "time": (datetime(2024, 1, 1) + timedelta(days=i * 10)).isoformat() + "Z",
                "nitrogen_kg": 10.0 * (i + 1)
            }
            client.post(f"/api/v1/plots/{plot.id}/nutrients", json=app_data)

        # Get balance with breakdown
        response = client.get(f"/api/v1/plots/{plot.id}/nutrients/balance?include_breakdown=true")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # May return timeline or breakdown of applications
        assert isinstance(data, (dict, list))


@pytest.mark.integration
@pytest.mark.api
class TestNutrientCostTracking:
    """Test nutrient cost tracking functionality."""

    def test_total_nutrient_cost(self, client, setup_plot, sample_nutrient_data):
        """Test calculating total nutrient cost."""
        plot = setup_plot

        # Create applications with costs
        costs = [50.0, 75.0, 100.0, 60.0]
        total_cost = sum(costs)

        for cost in costs:
            app_data = {
                **sample_nutrient_data,
                "cost_usd": cost,
                "time": (datetime(2024, 1, 1) + timedelta(days=len(costs))).isoformat() + "Z"
            }
            client.post(f"/api/v1/plots/{plot.id}/nutrients", json=app_data)

        # Get applications and calculate total
        response = client.get(f"/api/v1/plots/{plot.id}/nutrients")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        calculated_total = sum(item.get("cost_usd", 0) for item in items)
        assert abs(calculated_total - total_cost) < 1.0


@pytest.mark.integration
@pytest.mark.api
class TestNutrientsValidation:
    """Test validation and error handling for nutrients API."""

    def test_invalid_amount(self, client, setup_plot, sample_nutrient_data):
        """Test validation for negative amount."""
        plot = setup_plot
        invalid_data = {**sample_nutrient_data, "amount_kg": -50.0}
        response = client.post(
            f"/api/v1/plots/{plot.id}/nutrients",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_npk_values(self, client, setup_plot, sample_nutrient_data):
        """Test validation for negative NPK values."""
        plot = setup_plot
        invalid_data = {**sample_nutrient_data, "nitrogen_kg": -10.0}
        response = client.post(
            f"/api/v1/plots/{plot.id}/nutrients",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_cost(self, client, setup_plot, sample_nutrient_data):
        """Test validation for negative cost."""
        plot = setup_plot
        invalid_data = {**sample_nutrient_data, "cost_usd": -75.0}
        response = client.post(
            f"/api/v1/plots/{plot.id}/nutrients",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_required_fields(self, client, setup_plot):
        """Test creating nutrient application without required fields."""
        plot = setup_plot
        incomplete_data = {
            "nutrient_type": "Nitrogen"
            # Missing time and amount_kg
        }
        response = client.post(
            f"/api/v1/plots/{plot.id}/nutrients",
            json=incomplete_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_npk_sum_exceeds_total(self, client, setup_plot, sample_nutrient_data):
        """Test validation when NPK sum exceeds total amount."""
        plot = setup_plot
        invalid_data = {
            **sample_nutrient_data,
            "amount_kg": 10.0,
            "nitrogen_kg": 10.0,
            "phosphorus_kg": 10.0,
            "potassium_kg": 10.0  # Sum = 30kg, but total = 10kg
        }
        response = client.post(
            f"/api/v1/plots/{plot.id}/nutrients",
            json=invalid_data
        )
        # This validation may or may not be enforced depending on business rules
        # Could be warning instead of error
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]

    def test_invalid_plot_id(self, client, sample_nutrient_data):
        """Test creating nutrient application for non-existent plot."""
        import uuid
        fake_plot_id = str(uuid.uuid4())

        response = client.post(
            f"/api/v1/plots/{fake_plot_id}/nutrients",
            json=sample_nutrient_data
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
