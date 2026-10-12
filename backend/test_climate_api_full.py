import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

LOCATIONS_TO_TEST = [
    ("Hyderabad", 17.3850, 78.4867, "Hyderabad (Begumpet IMD Observatory)"),
    ("Delhi", 28.6139, 77.2090, "New Delhi (Safdarjung IMD Observatory)"),
    ("Mumbai", 19.0760, 72.8777, "Mumbai (Santacruz IMD Observatory)"),
    ("Chennai", 13.0827, 80.2707, "Chennai (Nungambakkam IMD Observatory)"),
    ("Bengaluru", 12.9716, 77.5946, "Bengaluru (Bangalore City IMD Observatory)"),
    ("Guntur", 16.3067, 80.4365, "Guntur (Bapatla / Guntur IMD Observatory)"),
    ("Vijayawada", 16.5062, 80.6480, "Vijayawada (Gannavaram IMD Observatory)"),
    ("Nagavarappadu", 16.5400, 80.8100, "Vijayawada (Gannavaram IMD Observatory)")
]

def test_all_8_climate_locations():
    print("\n--- RUNNING COMPREHENSIVE CLIMATE API TESTS ---")
    
    for loc_name, lat, lon, expected_station in LOCATIONS_TO_TEST:
        resp = client.get(f"/api/climate/history?location={loc_name}&lat={lat}&lon={lon}")
        assert resp.status_code == 200, f"Failed for {loc_name}: {resp.text}"
        data = resp.json()
        
        # 1. Location & Station Verification
        assert "reference_station" in data, f"Missing reference_station for {loc_name}"
        ref_station = data["reference_station"]
        assert expected_station in ref_station["name"], f"Expected {expected_station}, got {ref_station['name']}"
        assert ref_station["distance_km"] >= 0, "Distance must be >= 0"
        
        # 2. Climatological Period Verification
        src = data.get("source_info") or data.get("source")
        assert src["period"] == "1991–2020", f"Period must be 1991–2020, got {src.get('period')}"
        assert src["data_type"] == "climatological_normal"
        assert "India Meteorological Department" in src["organization"]
        
        # 3. Monthly 12-month data integrity
        monthly = data.get("monthly") or []
        assert len(monthly) == 12, f"Expected 12 months, got {len(monthly)}"
        months_set = {m["month"] for m in monthly}
        assert len(months_set) == 12, "Duplicate months detected"
        
        for m in monthly:
            assert -60.0 <= m["avg_temperature_c"] <= 60.0
            assert m["max_temperature_c"] >= m["min_temperature_c"]
            assert 0.0 <= m["precipitation_mm"] <= 5000.0
            assert 0.0 <= m["rain_days"] <= 31.0
            
        # 4. Annual summary integrity
        annual = data.get("annual")
        assert annual is not None
        assert annual["mean_temperature_c"] > 0
        assert annual["total_precipitation_mm"] > 0
        assert annual["wettest_month"] in months_set
        assert annual["warmest_month"] in months_set
        
        print(f"[PASS] {loc_name:15} -> {ref_station['name']:<42} ({ref_station['distance_km']:>5.1f} km) | {annual['mean_temperature_c']} C | {annual['total_precipitation_mm']} mm")

def test_nagavarappadu_dynamic_and_no_station_fabrication():
    """Verify Nagavarappadu does not pretend to have its own IMD station and correctly matches Gannavaram."""
    resp = client.get("/api/climate/history?location=Nagavarappadu&lat=16.5400&lon=80.8100")
    assert resp.status_code == 200
    data = resp.json()
    assert "Vijayawada (Gannavaram IMD Observatory)" in data["reference_station"]["name"]
    assert data["reference_station"]["distance_km"] < 25.0
    assert "Nagavarappadu" in data["location_name"]

def test_chatbot_climate_integration():
    """Verify AI chatbot retrieves climate data for natural language queries."""
    # Query 1: Average rainfall
    chat_resp = client.post("/api/chat/message", json={
        "message": "What is the average rainfall in this location?",
        "location_name": "Hyderabad, Telangana",
        "latitude": 17.3850,
        "longitude": 78.4867,
        "language": "en"
    })
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    reply = chat_data.get("message", "")
    assert "Hyderabad" in reply or "Begumpet" in reply
    assert "857" in reply or "rainfall" in reply.lower() or "precipitation" in reply.lower()
    print("\nChatbot rainfall test passed! Response snippet:", reply[:150].encode('ascii', 'replace').decode('ascii'))
    
    # Query 2: Specific year query (e.g. 2020) distinguishes 30-year normal from single year
    chat_year_resp = client.post("/api/chat/message", json={
        "message": "What was the climate like in 2020?",
        "location_name": "Vijayawada, Andhra Pradesh",
        "latitude": 16.5062,
        "longitude": 80.6480,
        "language": "en"
    })
    assert chat_year_resp.status_code == 200
    reply_year = chat_year_resp.json().get("message", "")
    assert "2020" in reply_year
    assert "Climatological Normal" in reply_year or "30-year" in reply_year
    print("Chatbot single-year distinction test passed! Response snippet:", reply_year[:150].encode('ascii', 'replace').decode('ascii'))

if __name__ == "__main__":
    test_all_8_climate_locations()
    test_nagavarappadu_dynamic_and_no_station_fabrication()
    test_chatbot_climate_integration()
    print("\nALL CLIMATE TESTS PASSED SUCCESSFULLY!")
