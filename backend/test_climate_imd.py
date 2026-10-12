import asyncio
import sys
from app.weather.service import weather_service

TEST_LOCATIONS = [
    "Hyderabad",
    "Delhi",
    "Mumbai",
    "Chennai",
    "Bengaluru",
    "Guntur",
    "Vijayawada",
    "Nagavarappadu"
]

async def run_tests():
    print("=================================================================")
    print("VERIFYING IMD CLIMATOLOGICAL NORMALS SERVICE FOR TEST LOCATIONS")
    print("=================================================================")
    
    results = {}
    for loc in TEST_LOCATIONS:
        print(f"\nTesting location: '{loc}'...")
        res = await weather_service.get_historical_climate(loc)
        
        # Verify required fields
        assert res.period == "1991–2020", f"Expected 1991–2020, got {res.period}"
        assert res.reference_station is not None, "Missing reference_station"
        assert res.annual is not None, "Missing annual summary"
        assert res.monthly is not None and len(res.monthly) == 12, "Monthly must have 12 entries"
        
        ref_st = res.reference_station
        ann = res.annual
        src = res.source_info
        
        print(f"  -> Requested Loc: {res.location_name} ({res.latitude:.4f}, {res.longitude:.4f})")
        print(f"  -> Reference Station: {ref_st.name} [ID: {ref_st.id}]")
        print(f"  -> Distance: {ref_st.distance_km:.2f} km")
        print(f"  -> Period: {src.period} ({src.data_type})")
        print(f"  -> Source: {src.organization}")
        print(f"  -> Annual Mean Temp: {ann.mean_temperature_c}°C (Max: {ann.max_temperature_c}°C, Min: {ann.min_temperature_c}°C)")
        print(f"  -> Annual Precip: {ann.total_precipitation_mm} mm across {ann.rainy_days} rainy days")
        print(f"  -> Warmest Month: {ann.warmest_month} | Wettest Month: {ann.wettest_month}")
        
        results[loc] = {
            "ref_name": ref_st.name,
            "dist_km": ref_st.distance_km,
            "mean_temp": ann.mean_temperature_c,
            "precip": ann.total_precipitation_mm,
            "period": src.period
        }
        
    print("\n=================================================================")
    print("VERIFICATION SUMMARY:")
    for loc, data in results.items():
        print(f"{loc:15} -> {data['ref_name']:<42} {data['dist_km']:>6.1f} km | {data['mean_temp']:>4.1f}°C | {data['precip']:>6.1f} mm | {data['period']}")
    print("=================================================================")
    print("ALL 8 LOCATIONS TESTED AND VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_tests())
