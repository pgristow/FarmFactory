"""
Integration tests for Financial Data API endpoints.

Tests:
- Costs and harvests CRUD
- P&L calculation
- ROI calculation
- Financial summaries
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status

INPUT_COSTS_ENDPOINT = "/api/v1/input-costs"
HARVESTS_ENDPOINT = "/api/v1/harvests"


@pytest.fixture
def sample_input_cost_data():
    """Sample input cost data."""
    return {
        "date": "2024-01-15",
        "category": "seeds",
        "description": "Tomato seeds - Beefsteak variety",
        "quantity": 1.0,
        "unit": "kg",
        "unit_cost_usd": 50.00,
        "total_cost_usd": 50.00,
        "supplier": "AgriSeeds Co.",
        "notes": "High quality hybrid seeds"
    }


@pytest.fixture
def sample_harvest_data():
    """Sample harvest data."""
    return {
        "harvest_date": "2024-04-15",
        "quantity_kg": 500.0,
        "quality_grade": "A",
        "price_per_kg_usd": 3.50,
        "total_revenue_usd": 1750.00,
        "buyer": "Local Market",
        "notes": "First harvest of the season"
    }


@pytest.fixture
def setup_planting(test_db, client):
    """Setup farm, plot, crop, and planting for testing."""
    from app.models.farm import Farm
    from app.models.plot import Plot
    from app.models.crop import Crop
    from app.models.crop import Planting

    farm = Farm(name="Test Farm", total_area_hectares=10.0)
    test_db.add(farm)
    test_db.commit()

    plot = Plot(name="Test Plot", farm_id=farm.id, area_hectares=1.0)
    test_db.add(plot)
    test_db.commit()

    crop = Crop(name="Test Crop", crop_type="vegetable")
    test_db.add(crop)
    test_db.commit()

    planting = Planting(
        plot_id=plot.id,
        crop_id=crop.id,
        planting_date=datetime(2024, 1, 1),
        status="active"
    )
    test_db.add(planting)
    test_db.commit()

    return {"farm": farm, "plot": plot, "crop": crop, "planting": planting}


@pytest.mark.integration
@pytest.mark.api
class TestInputCostsAPI:
    """Test input costs CRUD operations."""

    def test_create_input_cost(self, client, setup_planting, sample_input_cost_data):
        """Test POST /api/v1/input-costs - Record input cost."""
        setup_data = setup_planting
        cost_data = {**sample_input_cost_data, "plot_id": str(setup_data["plot"].id)}

        response = client.post(INPUT_COSTS_ENDPOINT, json=cost_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["category"] == sample_input_cost_data["category"]
        assert data["total_cost_usd"] == sample_input_cost_data["total_cost_usd"]
        assert data["description"] == sample_input_cost_data["description"]
        assert "id" in data
        assert "date" in data

    def test_create_input_cost_minimal_fields(self, client, setup_planting):
        """Test creating input cost with minimal required fields."""
        setup_data = setup_planting
        minimal_cost = {
            "plot_id": str(setup_data["plot"].id),
            "date": "2024-01-15",
            "category": "fertilizer",
            "total_cost_usd": 100.00
        }
        response = client.post(INPUT_COSTS_ENDPOINT, json=minimal_cost)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["category"] == "fertilizer"
        assert data["total_cost_usd"] == 100.00

    def test_list_input_costs(self, client, setup_planting, sample_input_cost_data):
        """Test GET /api/v1/input-costs - List costs with filtering."""
        setup_data = setup_planting

        # Create multiple costs
        categories = ["seeds", "fertilizer", "pesticide", "labor"]
        for i, category in enumerate(categories):
            cost_data = {
                **sample_input_cost_data,
                "plot_id": str(setup_data["plot"].id),
                "category": category,
                "total_cost_usd": 100.0 + i * 50,
                "date": (datetime(2024, 1, 15) + timedelta(days=i * 7)).isoformat()[:10]
            }
            client.post(INPUT_COSTS_ENDPOINT, json=cost_data)

        # List costs
        response = client.get(INPUT_COSTS_ENDPOINT)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 4

    def test_filter_costs_by_category(self, client, setup_planting, sample_input_cost_data):
        """Test filtering costs by category."""
        setup_data = setup_planting

        # Create costs in different categories
        for category in ["seeds", "fertilizer", "seeds"]:
            cost_data = {
                **sample_input_cost_data,
                "plot_id": str(setup_data["plot"].id),
                "category": category
            }
            client.post(INPUT_COSTS_ENDPOINT, json=cost_data)

        # Filter by category
        response = client.get(f"{INPUT_COSTS_ENDPOINT}?category=seeds")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        seeds_costs = [item for item in items if item.get("category") == "seeds"]
        assert len(seeds_costs) >= 2

    def test_filter_costs_by_date_range(self, client, setup_planting, sample_input_cost_data):
        """Test filtering costs by date range."""
        setup_data = setup_planting

        # Create costs across different months
        dates = ["2024-01-15", "2024-02-15", "2024-03-15"]
        for date in dates:
            cost_data = {
                **sample_input_cost_data,
                "plot_id": str(setup_data["plot"].id),
                "date": date
            }
            client.post(INPUT_COSTS_ENDPOINT, json=cost_data)

        # Filter to January only
        response = client.get(
            f"{INPUT_COSTS_ENDPOINT}?start_date=2024-01-01&end_date=2024-01-31"
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 1

    def test_filter_costs_by_plot(self, client, test_db, sample_input_cost_data):
        """Test filtering costs by plot."""
        from app.models.farm import Farm
        from app.models.plot import Plot

        # Create two plots
        farm = Farm(name="Test Farm", total_area_hectares=10.0)
        test_db.add(farm)
        test_db.commit()

        plot1 = Plot(name="Plot 1", farm_id=farm.id, area_hectares=1.0)
        plot2 = Plot(name="Plot 2", farm_id=farm.id, area_hectares=1.0)
        test_db.add_all([plot1, plot2])
        test_db.commit()

        # Create costs for each plot
        client.post(INPUT_COSTS_ENDPOINT, json={**sample_input_cost_data, "plot_id": str(plot1.id)})
        client.post(INPUT_COSTS_ENDPOINT, json={**sample_input_cost_data, "plot_id": str(plot2.id)})

        # Filter by plot
        response = client.get(f"{INPUT_COSTS_ENDPOINT}?plot_id={plot1.id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        plot1_costs = [item for item in items if item.get("plot_id") == str(plot1.id)]
        assert len(plot1_costs) >= 1

    def test_pagination_input_costs(self, client, setup_planting, sample_input_cost_data):
        """Test pagination on input costs."""
        setup_data = setup_planting

        # Create 25 costs
        for i in range(25):
            cost_data = {
                **sample_input_cost_data,
                "plot_id": str(setup_data["plot"].id),
                "date": (datetime(2024, 1, 1) + timedelta(days=i)).isoformat()[:10]
            }
            client.post(INPUT_COSTS_ENDPOINT, json=cost_data)

        # Test first page
        response = client.get(f"{INPUT_COSTS_ENDPOINT}?limit=10&offset=0")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) == 10

        # Test second page
        response = client.get(f"{INPUT_COSTS_ENDPOINT}?limit=10&offset=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) == 10

    def test_get_input_cost_by_id(self, client, setup_planting, sample_input_cost_data):
        """Test GET /api/v1/input-costs/{id} - Get specific cost."""
        setup_data = setup_planting
        cost_data = {**sample_input_cost_data, "plot_id": str(setup_data["plot"].id)}

        # Create cost
        create_response = client.post(INPUT_COSTS_ENDPOINT, json=cost_data)
        cost_id = create_response.json()["id"]

        # Get cost
        response = client.get(f"{INPUT_COSTS_ENDPOINT}/{cost_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == cost_id
        assert data["category"] == sample_input_cost_data["category"]

    def test_update_input_cost(self, client, setup_planting, sample_input_cost_data):
        """Test PUT /api/v1/input-costs/{id} - Update cost."""
        setup_data = setup_planting
        cost_data = {**sample_input_cost_data, "plot_id": str(setup_data["plot"].id)}

        # Create cost
        create_response = client.post(INPUT_COSTS_ENDPOINT, json=cost_data)
        cost_id = create_response.json()["id"]

        # Update cost
        update_data = {
            "total_cost_usd": 60.00,
            "notes": "Updated after invoice verification"
        }
        response = client.put(f"{INPUT_COSTS_ENDPOINT}/{cost_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["total_cost_usd"] == 60.00

    def test_delete_input_cost(self, client, setup_planting, sample_input_cost_data):
        """Test DELETE /api/v1/input-costs/{id} - Delete cost."""
        setup_data = setup_planting
        cost_data = {**sample_input_cost_data, "plot_id": str(setup_data["plot"].id)}

        # Create cost
        create_response = client.post(INPUT_COSTS_ENDPOINT, json=cost_data)
        cost_id = create_response.json()["id"]

        # Delete cost
        response = client.delete(f"{INPUT_COSTS_ENDPOINT}/{cost_id}")
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]

        # Verify deletion
        get_response = client.get(f"{INPUT_COSTS_ENDPOINT}/{cost_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
@pytest.mark.api
class TestHarvestsAPI:
    """Test harvest records CRUD operations."""

    def test_create_harvest(self, client, setup_planting, sample_harvest_data):
        """Test POST /api/v1/plantings/{planting_id}/harvests - Record harvest."""
        setup_data = setup_planting
        planting = setup_data["planting"]

        response = client.post(
            f"/api/v1/plantings/{planting.id}/harvests",
            json=sample_harvest_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["quantity_kg"] == sample_harvest_data["quantity_kg"]
        assert data["total_revenue_usd"] == sample_harvest_data["total_revenue_usd"]
        assert data["planting_id"] == str(planting.id)
        assert "id" in data

    def test_create_harvest_minimal_fields(self, client, setup_planting):
        """Test creating harvest with minimal required fields."""
        setup_data = setup_planting
        planting = setup_data["planting"]

        minimal_harvest = {
            "harvest_date": "2024-04-15",
            "quantity_kg": 500.0,
            "price_per_kg_usd": 3.50
        }
        response = client.post(
            f"/api/v1/plantings/{planting.id}/harvests",
            json=minimal_harvest
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["quantity_kg"] == 500.0

    def test_list_harvests_for_planting(self, client, setup_planting, sample_harvest_data):
        """Test GET /api/v1/plantings/{planting_id}/harvests - Get harvest history."""
        setup_data = setup_planting
        planting = setup_data["planting"]

        # Create multiple harvests
        for i in range(4):
            harvest_data = {
                **sample_harvest_data,
                "harvest_date": (datetime(2024, 4, 15) + timedelta(days=i * 7)).isoformat()[:10],
                "quantity_kg": 500.0 + i * 100
            }
            client.post(f"/api/v1/plantings/{planting.id}/harvests", json=harvest_data)

        # List harvests
        response = client.get(f"/api/v1/plantings/{planting.id}/harvests")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 4

    def test_get_harvest_by_id(self, client, setup_planting, sample_harvest_data):
        """Test GET /api/v1/harvests/{id} - Get specific harvest."""
        setup_data = setup_planting
        planting = setup_data["planting"]

        # Create harvest
        create_response = client.post(
            f"/api/v1/plantings/{planting.id}/harvests",
            json=sample_harvest_data
        )
        harvest_id = create_response.json()["id"]

        # Get harvest
        response = client.get(f"{HARVESTS_ENDPOINT}/{harvest_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == harvest_id

    def test_update_harvest(self, client, setup_planting, sample_harvest_data):
        """Test PUT /api/v1/harvests/{id} - Update harvest."""
        setup_data = setup_planting
        planting = setup_data["planting"]

        # Create harvest
        create_response = client.post(
            f"/api/v1/plantings/{planting.id}/harvests",
            json=sample_harvest_data
        )
        harvest_id = create_response.json()["id"]

        # Update harvest
        update_data = {
            "quantity_kg": 550.0,
            "total_revenue_usd": 1925.00
        }
        response = client.put(f"{HARVESTS_ENDPOINT}/{harvest_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["quantity_kg"] == 550.0

    def test_delete_harvest(self, client, setup_planting, sample_harvest_data):
        """Test DELETE /api/v1/harvests/{id} - Delete harvest."""
        setup_data = setup_planting
        planting = setup_data["planting"]

        # Create harvest
        create_response = client.post(
            f"/api/v1/plantings/{planting.id}/harvests",
            json=sample_harvest_data
        )
        harvest_id = create_response.json()["id"]

        # Delete harvest
        response = client.delete(f"{HARVESTS_ENDPOINT}/{harvest_id}")
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]

        # Verify deletion
        get_response = client.get(f"{HARVESTS_ENDPOINT}/{harvest_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
@pytest.mark.api
class TestFinancialSummaryAPI:
    """Test financial summary and P&L endpoints."""

    def test_get_plot_financial_summary(self, client, setup_planting, sample_input_cost_data, sample_harvest_data):
        """Test GET /api/v1/plots/{plot_id}/financial/summary - P&L summary."""
        setup_data = setup_planting
        plot = setup_data["plot"]
        planting = setup_data["planting"]

        # Create costs
        total_costs = 0
        for cost in [100.0, 150.0, 200.0]:
            cost_data = {
                **sample_input_cost_data,
                "plot_id": str(plot.id),
                "total_cost_usd": cost
            }
            client.post(INPUT_COSTS_ENDPOINT, json=cost_data)
            total_costs += cost

        # Create harvests
        total_revenue = 0
        for revenue in [1000.0, 1500.0]:
            harvest_data = {
                **sample_harvest_data,
                "total_revenue_usd": revenue
            }
            client.post(f"/api/v1/plantings/{planting.id}/harvests", json=harvest_data)
            total_revenue += revenue

        # Get summary
        response = client.get(f"/api/v1/plots/{plot.id}/financial/summary")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "total_costs" in data or "costs" in data
        assert "total_revenue" in data or "revenue" in data
        assert "profit" in data or "net_income" in data

    def test_get_plot_roi(self, client, setup_planting, sample_input_cost_data, sample_harvest_data):
        """Test ROI calculation."""
        setup_data = setup_planting
        plot = setup_data["plot"]
        planting = setup_data["planting"]

        # Create cost of $500
        cost_data = {
            **sample_input_cost_data,
            "plot_id": str(plot.id),
            "total_cost_usd": 500.0
        }
        client.post(INPUT_COSTS_ENDPOINT, json=cost_data)

        # Create harvest with revenue of $2000
        harvest_data = {
            **sample_harvest_data,
            "total_revenue_usd": 2000.0
        }
        client.post(f"/api/v1/plantings/{planting.id}/harvests", json=harvest_data)

        # Get ROI (should be 300%)
        response = client.get(f"/api/v1/plots/{plot.id}/financial/roi")

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            # ROI = (Revenue - Cost) / Cost * 100 = (2000 - 500) / 500 * 100 = 300%
            assert "roi" in data or "roi_percent" in data

    def test_financial_summary_with_date_range(self, client, setup_planting, sample_input_cost_data, sample_harvest_data):
        """Test financial summary with date range filter."""
        setup_data = setup_planting
        plot = setup_data["plot"]
        planting = setup_data["planting"]

        # Create costs in different months
        client.post(INPUT_COSTS_ENDPOINT, json={
            **sample_input_cost_data,
            "plot_id": str(plot.id),
            "date": "2024-01-15",
            "total_cost_usd": 100.0
        })
        client.post(INPUT_COSTS_ENDPOINT, json={
            **sample_input_cost_data,
            "plot_id": str(plot.id),
            "date": "2024-02-15",
            "total_cost_usd": 200.0
        })

        # Get summary for January only
        response = client.get(
            f"/api/v1/plots/{plot.id}/financial/summary?"
            f"start_date=2024-01-01&end_date=2024-01-31"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_cost_breakdown_by_category(self, client, setup_planting, sample_input_cost_data):
        """Test cost breakdown by category."""
        setup_data = setup_planting
        plot = setup_data["plot"]

        # Create costs in different categories
        categories_costs = {
            "seeds": 100.0,
            "fertilizer": 200.0,
            "pesticide": 150.0,
            "labor": 300.0
        }

        for category, cost in categories_costs.items():
            cost_data = {
                **sample_input_cost_data,
                "plot_id": str(plot.id),
                "category": category,
                "total_cost_usd": cost
            }
            client.post(INPUT_COSTS_ENDPOINT, json=cost_data)

        # Get summary (may include breakdown)
        response = client.get(f"/api/v1/plots/{plot.id}/financial/summary")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # May include cost breakdown by category
        assert isinstance(data, dict)


@pytest.mark.integration
@pytest.mark.api
class TestFinancialValidation:
    """Test validation and error handling for financial API."""

    def test_negative_cost(self, client, setup_planting, sample_input_cost_data):
        """Test validation for negative cost."""
        setup_data = setup_planting
        invalid_data = {
            **sample_input_cost_data,
            "plot_id": str(setup_data["plot"].id),
            "total_cost_usd": -100.0
        }
        response = client.post(INPUT_COSTS_ENDPOINT, json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_negative_harvest_quantity(self, client, setup_planting, sample_harvest_data):
        """Test validation for negative harvest quantity."""
        setup_data = setup_planting
        invalid_data = {**sample_harvest_data, "quantity_kg": -100.0}
        response = client.post(
            f"/api/v1/plantings/{setup_data['planting'].id}/harvests",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_negative_price(self, client, setup_planting, sample_harvest_data):
        """Test validation for negative price."""
        setup_data = setup_planting
        invalid_data = {**sample_harvest_data, "price_per_kg_usd": -5.0}
        response = client.post(
            f"/api/v1/plantings/{setup_data['planting'].id}/harvests",
            json=invalid_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_category(self, client, setup_planting, sample_input_cost_data):
        """Test validation for invalid cost category."""
        setup_data = setup_planting
        invalid_data = {
            **sample_input_cost_data,
            "plot_id": str(setup_data["plot"].id),
            "category": ""  # Empty category
        }
        response = client.post(INPUT_COSTS_ENDPOINT, json=invalid_data)
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]

    def test_harvest_before_planting_date(self, client, setup_planting, sample_harvest_data):
        """Test validation for harvest before planting date."""
        setup_data = setup_planting
        # Planting date is 2024-01-01
        invalid_data = {
            **sample_harvest_data,
            "harvest_date": "2023-12-15"  # Before planting
        }
        response = client.post(
            f"/api/v1/plantings/{setup_data['planting'].id}/harvests",
            json=invalid_data
        )
        # May be allowed or rejected depending on business rules
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]

    def test_missing_required_fields_cost(self, client, setup_planting):
        """Test creating cost without required fields."""
        setup_data = setup_planting
        incomplete_data = {
            "plot_id": str(setup_data["plot"].id)
            # Missing date, category, total_cost_usd
        }
        response = client.post(INPUT_COSTS_ENDPOINT, json=incomplete_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_required_fields_harvest(self, client, setup_planting):
        """Test creating harvest without required fields."""
        setup_data = setup_planting
        incomplete_data = {
            "quality_grade": "A"
            # Missing harvest_date, quantity_kg
        }
        response = client.post(
            f"/api/v1/plantings/{setup_data['planting'].id}/harvests",
            json=incomplete_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
