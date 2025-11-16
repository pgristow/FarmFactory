#!/usr/bin/env python3
"""
Simple script to test the FarmFactory API
Requires the API to be running on http://localhost:8000
"""
import requests
import json
from uuid import UUID

BASE_URL = "http://localhost:8000/api/v1"


def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print(f"{'=' * 60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


def test_health():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)
    return response.status_code == 200


def test_create_farm():
    """Test creating a farm"""
    farm_data = {
        "name": "Green Valley Farm",
        "address": "123 Farm Road, Rural County, State 12345",
        "latitude": 34.0522,
        "longitude": -118.2437,
        "total_area_hectares": 50.5,
        "timezone": "America/Los_Angeles"
    }

    response = requests.post(f"{BASE_URL}/farms", json=farm_data)
    print_response("Create Farm", response)

    if response.status_code == 201:
        farm_id = response.json()["data"]["id"]
        print(f"\n✓ Farm created with ID: {farm_id}")
        return farm_id
    return None


def test_list_farms():
    """Test listing farms"""
    response = requests.get(f"{BASE_URL}/farms?page=1&page_size=10")
    print_response("List Farms", response)
    return response.status_code == 200


def test_get_farm(farm_id):
    """Test getting a specific farm"""
    response = requests.get(f"{BASE_URL}/farms/{farm_id}")
    print_response(f"Get Farm {farm_id}", response)
    return response.status_code == 200


def test_update_farm(farm_id):
    """Test updating a farm"""
    update_data = {
        "name": "Green Valley Farm - Updated",
        "total_area_hectares": 55.0
    }

    response = requests.put(f"{BASE_URL}/farms/{farm_id}", json=update_data)
    print_response(f"Update Farm {farm_id}", response)
    return response.status_code == 200


def test_create_plot(farm_id):
    """Test creating a plot"""
    plot_data = {
        "farm_id": farm_id,
        "name": "North Field",
        "plot_number": "NF-01",
        "area_hectares": 2.5,
        "elevation_meters": 150.0,
        "slope_degrees": 5.2
    }

    response = requests.post(f"{BASE_URL}/plots", json=plot_data)
    print_response("Create Plot", response)

    if response.status_code == 201:
        plot_id = response.json()["data"]["id"]
        print(f"\n✓ Plot created with ID: {plot_id}")
        return plot_id
    return None


def test_list_plots(farm_id=None):
    """Test listing plots"""
    url = f"{BASE_URL}/plots?page=1&page_size=10"
    if farm_id:
        url += f"&farm_id={farm_id}"

    response = requests.get(url)
    print_response("List Plots", response)
    return response.status_code == 200


def test_delete_plot(plot_id):
    """Test deleting a plot"""
    response = requests.delete(f"{BASE_URL}/plots/{plot_id}")
    print_response(f"Delete Plot {plot_id}", response)
    return response.status_code == 200


def test_delete_farm(farm_id):
    """Test deleting a farm"""
    response = requests.delete(f"{BASE_URL}/farms/{farm_id}")
    print_response(f"Delete Farm {farm_id}", response)
    return response.status_code == 200


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("FarmFactory API Test Suite")
    print("=" * 60)

    try:
        # Test health check
        print("\n1. Testing Health Check...")
        if not test_health():
            print("✗ Health check failed!")
            return

        # Test farm CRUD
        print("\n2. Testing Farm Creation...")
        farm_id = test_create_farm()
        if not farm_id:
            print("✗ Farm creation failed!")
            return

        print("\n3. Testing List Farms...")
        test_list_farms()

        print("\n4. Testing Get Farm...")
        test_get_farm(farm_id)

        print("\n5. Testing Update Farm...")
        test_update_farm(farm_id)

        # Test plot CRUD
        print("\n6. Testing Plot Creation...")
        plot_id = test_create_plot(farm_id)
        if not plot_id:
            print("✗ Plot creation failed!")
            return

        print("\n7. Testing List Plots...")
        test_list_plots()

        print("\n8. Testing List Plots by Farm...")
        test_list_plots(farm_id)

        # Cleanup
        print("\n9. Testing Plot Deletion...")
        test_delete_plot(plot_id)

        print("\n10. Testing Farm Deletion...")
        test_delete_farm(farm_id)

        print("\n" + "=" * 60)
        print("✓ All tests completed!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API at", BASE_URL)
        print("Make sure the API is running with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")


if __name__ == "__main__":
    main()
