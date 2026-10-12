import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_nagavarappadu_across_years():
    """Verify Nagavarappadu for 2021, 2022, 2023, 2024 returns distinct, authentic historical observations."""
    years = [2021, 2022, 2023, 2024]
    results = {}

    for y in years:
        resp = client.get(f"/api/climate/historical?location=Nagavarappadu&lat=16.5400&lon=80.8100&year={y}")
        assert resp.status_code == 200, f"Failed for year {y}: {resp.text}"
        data = resp.json()

        assert data["year"] == y
        assert "Vijayawada (Gannavaram IMD Observatory)" in data["source"]["station"]
        assert data["source"]["distance_km"] < 25.0
        assert len(data["monthly"]) == 12

        summ = data["summary"]
        assert summ["annual_average_temperature"] > 20.0
        assert summ["annual_rainfall"] > 500.0
        assert summ["highest_temperature"] > 35.0
        assert summ["total_rainy_days"] > 20

        results[y] = {
            "rain": summ["annual_rainfall"],
            "temp": summ["annual_average_temperature"],
            "high": summ["highest_temperature"],
            "wettest": summ["wettest_month"]
        }
        print(f"[PASS] Nagavarappadu {y}: Rain={summ['annual_rainfall']}mm | Avg Temp={summ['annual_average_temperature']} C | Peak High={summ['highest_temperature']} C | Wettest={summ['wettest_month']}")

    # Verify that changing year produces different data
    assert results[2022]["rain"] != results[2023]["rain"], "2022 and 2023 rainfall must not be identical"
    assert results[2022]["temp"] != results[2023]["temp"], "2022 and 2023 temperature must not be identical"
    assert results[2023]["rain"] != results[2024]["rain"], "2023 and 2024 rainfall must not be identical"

def test_other_locations_for_year_2022():
    """Test Hyderabad, Chennai, Delhi, Mumbai, Bengaluru for 2022."""
    locations = [
        ("Hyderabad", 17.3850, 78.4867, "Begumpet"),
        ("Chennai", 13.0827, 80.2707, "Nungambakkam"),
        ("Delhi", 28.6139, 77.2090, "Safdarjung"),
        ("Mumbai", 19.0760, 72.8777, "Santacruz"),
        ("Bengaluru", 12.9716, 77.5946, "Bangalore City")
    ]

    for loc, lat, lon, exp_station in locations:
        resp = client.get(f"/api/climate/historical?location={loc}&latitude={lat}&longitude={lon}&year=2022")
        assert resp.status_code == 200, f"Failed for {loc}: {resp.text}"
        data = resp.json()

        assert data["year"] == 2022
        assert exp_station in data["source"]["station"]
        assert len(data["monthly"]) == 12
        assert data["summary"]["annual_rainfall"] > 0

        print(f"[PASS] {loc:12} (2022) -> {data['source']['station']:<42} | Rain={data['summary']['annual_rainfall']}mm | Temp={data['summary']['annual_average_temperature']} C")

def test_chatbot_year_specific_query():
    """Verify AI chatbot answers single-year historical questions using the exact year dataset."""
    chat_resp = client.post("/api/chat/message", json={
        "message": "What was the rainfall here in 2022?",
        "location_name": "Nagavarappadu, Andhra Pradesh",
        "latitude": 16.5400,
        "longitude": 80.8100,
        "language": "en"
    })
    assert chat_resp.status_code == 200
    reply = chat_resp.json().get("message", "")
    assert "2022" in reply
    assert "Rainfall" in reply or "rainfall" in reply
    print("[PASS] Chatbot year query response snippet:", reply[:150].encode('ascii', 'replace').decode('ascii'))

if __name__ == "__main__":
    print("\n--- RUNNING LOCATION + YEAR HISTORICAL CLIMATE TESTS ---")
    test_nagavarappadu_across_years()
    test_other_locations_for_year_2022()
    test_chatbot_year_specific_query()
    print("\nALL LOCATION + YEAR CLIMATE TESTS PASSED SUCCESSFULLY!")
