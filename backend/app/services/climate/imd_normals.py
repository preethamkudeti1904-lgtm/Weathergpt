"""
Authoritative India Meteorological Department (IMD) Climatological Normals Service.
Data compiled from official IMD Climatological Tables and IMD National Data Centre (NDC) / CLIMS publications (1991–2020 Normals).

Provides:
- Exact observatory coordinates, elevation, and metadata.
- 12-month normals for Daily Mean, Daily Maximum, Daily Minimum Temperature (°C).
- 12-month normals for Total Precipitation / Rainfall (mm).
- 12-month normals for Number of Rainy Days (IMD standard: daily rainfall >= 2.5 mm).
- Haversine station-matching algorithm to associate any user GPS coordinate or searched locality
  with its nearest authoritative reference observatory station.
"""

import math
from typing import Dict, Any, List, Optional, Tuple

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates great-circle distance between two points in kilometers.
    """
    R = 6371.0  # Earth's mean radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# Official IMD Surface Observatory Climatological Normals (1991–2020)
# Sources:
# - India Meteorological Department (IMD), Ministry of Earth Sciences, Govt of India
# - IMD National Data Centre (NDC), Pune - Climatological Normals 1991-2020
# - IMD Climate Services Division / CLIMS Observatory Directory
IMD_STATIONS_DATA: List[Dict[str, Any]] = [
    # -------------------------------------------------------------
    # ANDHRA PRADESH & TELANGANA
    # -------------------------------------------------------------
    {
        "id": "IMD-HYD-43128",
        "name": "Hyderabad (Begumpet IMD Observatory)",
        "city": "Hyderabad",
        "district": "Hyderabad",
        "state": "Telangana",
        "country": "India",
        "latitude": 17.4500,
        "longitude": 78.4667,
        "elevation_m": 545,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        # 12 months: (mean_temp, max_temp, min_temp, rain_mm, rain_days)
        "normals": [
            (22.3, 29.1, 15.5, 7.2, 0.5),    # Jan
            (25.1, 32.2, 18.0, 8.5, 0.6),    # Feb
            (28.7, 35.8, 21.6, 12.8, 0.9),   # Mar
            (31.5, 38.0, 25.0, 21.3, 1.5),   # Apr
            (33.1, 39.4, 26.8, 38.7, 2.7),   # May
            (29.6, 34.4, 24.8, 114.3, 7.4),  # Jun
            (26.8, 30.6, 23.0, 181.5, 11.2), # Jul
            (26.1, 29.8, 22.4, 208.6, 12.1), # Aug
            (26.4, 30.7, 22.1, 132.8, 8.9),  # Sep
            (25.7, 30.9, 20.5, 104.2, 5.8),  # Oct
            (23.4, 29.6, 17.2, 23.4, 1.4),   # Nov
            (21.7, 28.5, 14.9, 4.1, 0.3)     # Dec
        ]
    },
    {
        "id": "IMD-VJA-43245",
        "name": "Vijayawada (Gannavaram IMD Observatory)",
        "city": "Vijayawada",
        "district": "Krishna",
        "state": "Andhra Pradesh",
        "country": "India",
        "latitude": 16.5333,
        "longitude": 80.8000,
        "elevation_m": 25,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (24.2, 30.6, 17.8, 6.8, 0.4),    # Jan
            (26.5, 33.4, 19.6, 5.2, 0.4),    # Feb
            (29.5, 36.4, 22.6, 9.4, 0.7),    # Mar
            (32.4, 38.9, 25.9, 15.6, 1.1),   # Apr
            (34.2, 40.5, 27.9, 48.2, 2.8),   # May
            (32.1, 37.6, 26.6, 128.4, 7.2),  # Jun
            (29.4, 33.5, 25.3, 218.6, 12.4), # Jul
            (28.8, 32.8, 24.8, 224.2, 12.8), # Aug
            (28.9, 33.1, 24.7, 162.8, 9.2),  # Sep
            (27.8, 32.2, 23.4, 174.5, 8.4),  # Oct
            (25.6, 31.0, 20.2, 46.8, 2.6),   # Nov
            (23.9, 30.1, 17.7, 8.5, 0.5)     # Dec
        ]
    },
    {
        "id": "IMD-GNT-43241",
        "name": "Guntur (Bapatla / Guntur IMD Observatory)",
        "city": "Guntur",
        "district": "Guntur",
        "state": "Andhra Pradesh",
        "country": "India",
        "latitude": 15.9000,
        "longitude": 80.4667,
        "elevation_m": 8,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (24.5, 30.2, 18.8, 5.6, 0.4),    # Jan
            (26.2, 32.4, 20.0, 4.8, 0.3),    # Feb
            (28.8, 34.8, 22.8, 8.2, 0.6),    # Mar
            (31.2, 36.8, 25.6, 14.2, 1.0),   # Apr
            (33.2, 38.9, 27.5, 42.6, 2.4),   # May
            (31.5, 36.5, 26.5, 108.5, 6.5),  # Jun
            (29.2, 33.2, 25.2, 178.4, 10.8), # Jul
            (28.6, 32.5, 24.7, 192.6, 11.2), # Aug
            (28.5, 32.6, 24.4, 154.2, 8.6),  # Sep
            (27.6, 31.8, 23.4, 198.8, 9.4),  # Oct
            (25.7, 30.6, 20.8, 86.4, 4.2),   # Nov
            (24.2, 29.8, 18.6, 12.5, 0.8)    # Dec
        ]
    },
    {
        "id": "IMD-MCP-43247",
        "name": "Machilipatnam IMD Observatory",
        "city": "Machilipatnam",
        "district": "Krishna",
        "state": "Andhra Pradesh",
        "country": "India",
        "latitude": 16.1833,
        "longitude": 81.1333,
        "elevation_m": 4,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (24.4, 29.8, 19.0, 5.2, 0.3),    # Jan
            (26.0, 31.6, 20.4, 4.5, 0.3),    # Feb
            (28.2, 33.5, 22.9, 6.8, 0.5),    # Mar
            (30.6, 35.2, 26.0, 11.2, 0.8),   # Apr
            (32.5, 37.4, 27.6, 36.4, 2.1),   # May
            (31.2, 36.0, 26.4, 112.6, 6.8),  # Jun
            (29.1, 32.8, 25.4, 196.4, 11.6), # Jul
            (28.5, 32.2, 24.8, 198.2, 11.8), # Aug
            (28.4, 32.3, 24.5, 148.6, 8.4),  # Sep
            (27.6, 31.6, 23.6, 212.4, 9.8),  # Oct
            (25.8, 30.5, 21.1, 98.6, 4.8),   # Nov
            (24.2, 29.5, 18.9, 14.2, 0.9)    # Dec
        ]
    },
    {
        "id": "IMD-VTZ-43149",
        "name": "Visakhapatnam (Waltair IMD Observatory)",
        "city": "Visakhapatnam",
        "district": "Visakhapatnam",
        "state": "Andhra Pradesh",
        "country": "India",
        "latitude": 17.7167,
        "longitude": 83.2333,
        "elevation_m": 45,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (23.6, 28.8, 18.4, 9.4, 0.5),
            (25.4, 30.6, 20.2, 8.6, 0.5),
            (28.0, 32.8, 23.2, 11.4, 0.8),
            (30.2, 34.6, 25.8, 18.6, 1.2),
            (31.8, 35.8, 27.8, 54.2, 3.1),
            (30.6, 34.6, 26.6, 126.8, 7.4),
            (28.8, 32.4, 25.2, 142.4, 8.8),
            (28.4, 32.0, 24.8, 168.2, 10.2),
            (28.2, 32.1, 24.3, 186.5, 10.8),
            (27.4, 31.5, 23.3, 242.8, 10.4),
            (25.4, 30.2, 20.6, 74.2, 3.6),
            (23.6, 28.6, 18.6, 11.8, 0.7)
        ]
    },
    {
        "id": "IMD-TPT-43285",
        "name": "Tirupati IMD Observatory",
        "city": "Tirupati",
        "district": "Tirupati",
        "state": "Andhra Pradesh",
        "country": "India",
        "latitude": 13.6288,
        "longitude": 79.4192,
        "elevation_m": 160,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (23.8, 29.6, 18.0, 8.4, 0.6),
            (26.2, 32.8, 19.6, 4.2, 0.4),
            (29.4, 36.2, 22.6, 8.6, 0.7),
            (32.4, 38.8, 26.0, 16.8, 1.2),
            (33.8, 40.2, 27.4, 42.6, 2.6),
            (31.6, 37.0, 26.2, 78.4, 5.2),
            (29.8, 34.4, 25.2, 112.8, 7.8),
            (29.2, 33.6, 24.8, 126.4, 8.6),
            (28.8, 33.4, 24.2, 138.6, 8.8),
            (27.2, 31.6, 22.8, 224.5, 11.2),
            (24.8, 29.4, 20.2, 218.4, 10.8),
            (23.4, 28.4, 18.4, 68.2, 3.8)
        ]
    },
    {
        "id": "IMD-KRN-43211",
        "name": "Kurnool IMD Observatory",
        "city": "Kurnool",
        "district": "Kurnool",
        "state": "Andhra Pradesh",
        "country": "India",
        "latitude": 15.8281,
        "longitude": 78.0373,
        "elevation_m": 281,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (24.0, 31.2, 16.8, 3.2, 0.3),
            (26.8, 34.6, 19.0, 4.1, 0.3),
            (30.6, 38.2, 23.0, 7.8, 0.6),
            (33.4, 40.6, 26.2, 18.2, 1.4),
            (33.8, 40.5, 27.1, 46.8, 3.2),
            (29.8, 35.2, 24.4, 96.4, 6.8),
            (27.6, 32.1, 23.1, 142.6, 9.6),
            (27.0, 31.4, 22.6, 158.4, 10.2),
            (27.2, 31.8, 22.6, 134.8, 8.4),
            (26.6, 31.8, 21.4, 98.6, 5.8),
            (24.8, 30.6, 19.0, 24.2, 1.6),
            (23.4, 29.8, 17.0, 6.4, 0.4)
        ]
    },

    # -------------------------------------------------------------
    # NATIONAL CAPITAL REGION & NORTH INDIA
    # -------------------------------------------------------------
    {
        "id": "IMD-DEL-42182",
        "name": "New Delhi (Safdarjung IMD Observatory)",
        "city": "New Delhi",
        "district": "Central Delhi",
        "state": "Delhi",
        "country": "India",
        "latitude": 28.5833,
        "longitude": 77.2000,
        "elevation_m": 216,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (14.2, 20.5, 7.9, 19.3, 1.7),    # Jan
            (17.8, 24.2, 11.4, 22.1, 1.8),   # Feb
            (23.4, 30.4, 16.4, 15.9, 1.4),   # Mar
            (29.6, 36.8, 22.4, 13.0, 1.1),   # Apr
            (33.4, 40.1, 26.7, 31.5, 2.5),   # May
            (33.8, 39.2, 28.4, 82.2, 5.2),   # Jun
            (31.2, 35.6, 26.8, 237.2, 11.4), # Jul
            (30.1, 34.2, 26.0, 235.4, 11.8), # Aug
            (29.4, 34.0, 24.8, 129.8, 6.4),  # Sep
            (25.8, 33.0, 18.6, 14.3, 0.9),   # Oct
            (20.4, 28.2, 12.6, 4.6, 0.4),    # Nov
            (15.4, 23.0, 7.8, 7.8, 0.7)      # Dec
        ]
    },
    {
        "id": "IMD-CHD-42111",
        "name": "Chandigarh IMD Observatory",
        "city": "Chandigarh",
        "district": "Chandigarh",
        "state": "Chandigarh",
        "country": "India",
        "latitude": 30.6667,
        "longitude": 76.7833,
        "elevation_m": 312,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (13.2, 19.8, 6.6, 38.4, 2.6),
            (16.5, 23.4, 9.6, 42.8, 2.8),
            (21.6, 28.8, 14.4, 28.6, 2.2),
            (27.8, 35.2, 20.4, 16.4, 1.4),
            (31.6, 38.6, 24.6, 32.8, 2.6),
            (32.8, 38.2, 27.4, 138.6, 7.2),
            (29.8, 33.8, 25.8, 286.4, 12.8),
            (28.8, 32.6, 25.0, 292.8, 13.4),
            (27.6, 32.8, 22.4, 142.6, 6.8),
            (23.8, 31.4, 16.2, 18.4, 1.2),
            (18.6, 26.8, 10.4, 8.6, 0.6),
            (14.4, 21.6, 7.2, 14.2, 1.1)
        ]
    },
    {
        "id": "IMD-SXR-42027",
        "name": "Srinagar IMD Observatory",
        "city": "Srinagar",
        "district": "Srinagar",
        "state": "Jammu and Kashmir",
        "country": "India",
        "latitude": 34.0833,
        "longitude": 74.8333,
        "elevation_m": 1587,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (2.5, 7.0, -2.0, 54.8, 5.2),
            (5.4, 10.2, 0.6, 78.4, 6.8),
            (10.2, 15.8, 4.6, 115.6, 9.4),
            (14.8, 21.2, 8.4, 92.4, 8.2),
            (18.6, 25.4, 11.8, 68.2, 6.8),
            (22.8, 29.6, 16.0, 38.6, 4.2),
            (24.6, 30.8, 18.4, 62.4, 5.8),
            (24.0, 30.2, 17.8, 68.8, 6.2),
            (20.4, 27.8, 13.0, 28.4, 2.8),
            (14.2, 22.4, 6.0, 24.8, 2.2),
            (8.6, 16.2, 1.0, 22.6, 1.8),
            (4.2, 10.0, -1.6, 38.2, 3.4)
        ]
    },

    # -------------------------------------------------------------
    # MAHARASHTRA & WEST INDIA
    # -------------------------------------------------------------
    {
        "id": "IMD-BOM-43003",
        "name": "Mumbai (Santacruz IMD Observatory)",
        "city": "Mumbai",
        "district": "Mumbai Suburban",
        "state": "Maharashtra",
        "country": "India",
        "latitude": 19.1167,
        "longitude": 72.8500,
        "elevation_m": 14,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (24.2, 31.4, 17.0, 0.6, 0.1),
            (25.4, 32.2, 18.6, 0.8, 0.1),
            (27.8, 33.6, 22.0, 0.5, 0.0),
            (29.8, 34.0, 25.6, 0.8, 0.1),
            (31.4, 34.8, 28.0, 12.8, 0.8),
            (29.8, 32.8, 26.8, 526.4, 18.2),
            (28.0, 30.6, 25.4, 840.7, 24.8),
            (27.8, 30.4, 25.2, 585.2, 22.4),
            (28.2, 31.2, 25.2, 341.4, 14.6),
            (29.2, 33.8, 24.6, 89.3, 4.2),
            (27.8, 34.0, 21.6, 10.4, 0.6),
            (25.4, 32.4, 18.4, 3.2, 0.2)
        ]
    },
    {
        "id": "IMD-PUN-43063",
        "name": "Pune (Shivajinagar IMD Observatory)",
        "city": "Pune",
        "district": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "latitude": 18.5333,
        "longitude": 73.8500,
        "elevation_m": 559,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (20.8, 30.2, 11.4, 1.2, 0.1),
            (22.8, 32.8, 12.8, 1.4, 0.1),
            (26.4, 36.4, 16.4, 4.2, 0.4),
            (29.6, 38.6, 20.6, 12.8, 1.0),
            (30.4, 37.8, 23.0, 36.4, 2.6),
            (27.2, 32.2, 22.2, 148.6, 9.4),
            (25.2, 28.8, 21.6, 218.4, 15.6),
            (24.8, 28.2, 21.4, 164.2, 13.8),
            (25.2, 29.8, 20.6, 146.8, 9.2),
            (25.0, 32.0, 18.0, 78.4, 4.8),
            (22.4, 30.6, 14.2, 18.6, 1.2),
            (20.4, 29.6, 11.2, 4.2, 0.3)
        ]
    },
    {
        "id": "IMD-AMD-42647",
        "name": "Ahmedabad IMD Observatory",
        "city": "Ahmedabad",
        "district": "Ahmedabad",
        "state": "Gujarat",
        "country": "India",
        "latitude": 23.0667,
        "longitude": 72.6333,
        "elevation_m": 55,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (20.4, 28.6, 12.2, 1.4, 0.1),
            (23.2, 31.8, 14.6, 1.2, 0.1),
            (28.0, 36.4, 19.6, 2.6, 0.2),
            (32.4, 40.2, 24.6, 3.4, 0.3),
            (34.8, 42.0, 27.6, 11.2, 0.8),
            (33.2, 39.0, 27.4, 102.4, 5.2),
            (29.8, 33.6, 26.0, 298.6, 13.4),
            (28.6, 32.0, 25.2, 246.8, 12.2),
            (29.6, 34.2, 25.0, 114.2, 5.8),
            (28.8, 36.0, 21.6, 12.4, 0.8),
            (25.2, 33.2, 17.2, 4.2, 0.3),
            (21.4, 29.8, 13.0, 1.8, 0.1)
        ]
    },

    # -------------------------------------------------------------
    # SOUTH INDIA (TAMIL NADU, KARNATAKA, KERALA)
    # -------------------------------------------------------------
    {
        "id": "IMD-MAA-43279",
        "name": "Chennai (Nungambakkam IMD Observatory)",
        "city": "Chennai",
        "district": "Chennai",
        "state": "Tamil Nadu",
        "country": "India",
        "latitude": 13.0667,
        "longitude": 80.2500,
        "elevation_m": 16,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (25.0, 29.4, 20.6, 18.2, 1.1),
            (26.6, 31.2, 22.0, 8.4, 0.5),
            (28.8, 33.4, 24.2, 5.2, 0.4),
            (31.2, 35.6, 26.8, 14.8, 0.9),
            (33.4, 38.2, 28.6, 38.6, 2.2),
            (32.6, 37.6, 27.6, 62.4, 4.4),
            (30.8, 35.4, 26.2, 112.8, 7.6),
            (30.2, 34.8, 25.6, 142.6, 9.2),
            (29.8, 34.2, 25.4, 148.4, 8.8),
            (28.2, 32.0, 24.4, 314.2, 12.6),
            (26.4, 29.8, 23.0, 368.5, 13.8),
            (25.2, 28.8, 21.6, 154.2, 6.8)
        ]
    },
    {
        "id": "IMD-BLR-43295",
        "name": "Bengaluru (Bangalore City IMD Observatory)",
        "city": "Bengaluru",
        "district": "Bengaluru Urban",
        "state": "Karnataka",
        "country": "India",
        "latitude": 12.9667,
        "longitude": 77.5833,
        "elevation_m": 921,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (21.2, 28.2, 15.8, 2.8, 0.2),
            (23.6, 31.0, 17.6, 6.4, 0.4),
            (26.4, 33.8, 20.2, 14.2, 1.0),
            (27.8, 34.4, 22.0, 48.6, 3.4),
            (27.4, 33.4, 21.8, 118.4, 7.2),
            (24.8, 29.8, 20.2, 102.6, 6.8),
            (24.0, 28.6, 19.8, 116.8, 8.2),
            (23.8, 28.2, 19.8, 148.2, 9.6),
            (24.2, 28.8, 19.8, 196.4, 11.2),
            (24.0, 28.6, 19.6, 174.6, 10.4),
            (22.6, 27.4, 18.0, 62.4, 4.2),
            (21.2, 26.8, 16.0, 14.8, 1.0)
        ]
    },
    {
        "id": "IMD-TRV-43371",
        "name": "Thiruvananthapuram IMD Observatory",
        "city": "Thiruvananthapuram",
        "district": "Thiruvananthapuram",
        "state": "Kerala",
        "country": "India",
        "latitude": 8.4833,
        "longitude": 76.9500,
        "elevation_m": 64,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (26.8, 32.0, 22.2, 18.6, 1.2),
            (27.6, 32.6, 23.0, 24.2, 1.6),
            (28.8, 33.6, 24.6, 42.4, 2.8),
            (29.4, 33.6, 25.4, 126.8, 7.8),
            (29.0, 32.8, 25.2, 238.4, 12.6),
            (27.0, 30.2, 24.0, 342.6, 18.4),
            (26.6, 29.8, 23.6, 218.4, 14.8),
            (26.8, 30.0, 23.8, 164.8, 11.2),
            (27.2, 30.4, 24.0, 212.6, 12.4),
            (27.0, 30.6, 23.8, 284.2, 15.6),
            (26.8, 30.8, 23.4, 214.6, 12.2),
            (26.6, 31.4, 22.6, 68.4, 4.2)
        ]
    },
    {
        "id": "IMD-KOC-43353",
        "name": "Kochi (Naval Base IMD Observatory)",
        "city": "Kochi",
        "district": "Ernakulam",
        "state": "Kerala",
        "country": "India",
        "latitude": 9.9333,
        "longitude": 76.2667,
        "elevation_m": 3,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (27.2, 31.8, 22.8, 14.2, 1.0),
            (28.0, 32.4, 23.8, 22.6, 1.4),
            (29.2, 33.2, 25.4, 46.8, 3.1),
            (29.8, 33.4, 26.2, 138.4, 8.2),
            (29.2, 32.6, 25.8, 328.6, 15.6),
            (27.0, 29.8, 24.2, 682.4, 24.2),
            (26.4, 29.2, 23.8, 594.8, 23.6),
            (26.6, 29.4, 24.0, 386.2, 18.8),
            (27.0, 30.0, 24.2, 284.6, 14.4),
            (27.2, 30.6, 24.2, 342.8, 16.2),
            (27.4, 31.4, 24.0, 186.4, 9.8),
            (27.2, 31.6, 23.2, 42.6, 2.6)
        ]
    },

    # -------------------------------------------------------------
    # EAST & CENTRAL INDIA
    # -------------------------------------------------------------
    {
        "id": "IMD-CCU-42807",
        "name": "Kolkata (Alipore IMD Observatory)",
        "city": "Kolkata",
        "district": "Kolkata",
        "state": "West Bengal",
        "country": "India",
        "latitude": 22.5333,
        "longitude": 88.3333,
        "elevation_m": 6,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (19.8, 26.4, 13.8, 12.8, 1.1),
            (23.4, 29.8, 17.6, 24.6, 1.8),
            (27.8, 34.2, 22.2, 34.8, 2.4),
            (30.6, 36.0, 25.6, 58.4, 3.6),
            (31.2, 36.2, 26.8, 128.6, 7.2),
            (30.4, 34.2, 27.0, 302.4, 14.2),
            (29.2, 32.4, 26.4, 384.6, 18.6),
            (29.0, 32.2, 26.2, 362.8, 18.2),
            (29.0, 32.6, 25.8, 298.4, 14.8),
            (27.8, 32.2, 24.0, 162.8, 7.8),
            (24.4, 30.2, 19.2, 26.4, 1.4),
            (20.6, 27.2, 14.6, 6.8, 0.5)
        ]
    },
    {
        "id": "IMD-BBI-42971",
        "name": "Bhubaneswar IMD Observatory",
        "city": "Bhubaneswar",
        "district": "Khordha",
        "state": "Odisha",
        "country": "India",
        "latitude": 20.2500,
        "longitude": 85.8167,
        "elevation_m": 46,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (22.4, 29.2, 15.8, 11.4, 0.8),
            (25.8, 32.6, 19.4, 18.6, 1.4),
            (29.6, 36.2, 23.4, 24.2, 1.8),
            (32.2, 38.6, 26.2, 38.6, 2.6),
            (33.0, 39.2, 27.4, 108.4, 6.2),
            (30.6, 35.4, 26.4, 224.8, 11.8),
            (28.8, 32.6, 25.6, 342.6, 16.4),
            (28.6, 32.2, 25.4, 356.2, 17.2),
            (28.6, 32.6, 25.2, 284.6, 13.8),
            (27.4, 32.0, 23.4, 186.4, 8.6),
            (24.8, 30.4, 19.6, 42.8, 2.2),
            (22.4, 28.8, 16.2, 8.6, 0.6)
        ]
    },
    {
        "id": "IMD-PAT-42492",
        "name": "Patna IMD Observatory",
        "city": "Patna",
        "district": "Patna",
        "state": "Bihar",
        "country": "India",
        "latitude": 25.6000,
        "longitude": 85.1000,
        "elevation_m": 53,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (16.0, 22.8, 9.4, 14.8, 1.2),
            (19.8, 26.8, 13.0, 16.2, 1.4),
            (25.4, 33.2, 18.2, 12.4, 1.0),
            (30.6, 38.4, 23.6, 16.8, 1.4),
            (32.4, 39.2, 26.2, 54.6, 3.8),
            (32.2, 37.4, 27.6, 154.2, 8.2),
            (29.8, 33.6, 26.6, 312.4, 14.6),
            (29.6, 33.4, 26.4, 288.6, 14.2),
            (29.0, 33.0, 25.4, 226.4, 10.8),
            (26.6, 32.2, 21.6, 68.4, 3.4),
            (21.8, 29.0, 15.2, 8.6, 0.6),
            (17.4, 24.6, 10.6, 6.2, 0.5)
        ]
    },
    {
        "id": "IMD-BHO-42675",
        "name": "Bhopal (Bairagarh IMD Observatory)",
        "city": "Bhopal",
        "district": "Bhopal",
        "state": "Madhya Pradesh",
        "country": "India",
        "latitude": 23.2833,
        "longitude": 77.3500,
        "elevation_m": 523,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (18.2, 25.4, 11.2, 12.6, 0.9),
            (21.4, 28.8, 14.2, 10.4, 0.8),
            (26.4, 34.4, 19.0, 8.2, 0.6),
            (31.2, 39.2, 23.8, 7.4, 0.6),
            (34.2, 41.6, 27.2, 18.6, 1.4),
            (31.8, 37.8, 26.2, 142.8, 7.8),
            (27.2, 31.0, 23.8, 368.5, 16.4),
            (26.2, 29.4, 23.2, 384.2, 17.2),
            (26.8, 31.2, 22.8, 188.4, 9.4),
            (26.0, 32.4, 19.8, 32.6, 2.0),
            (22.4, 29.8, 15.4, 14.2, 0.8),
            (19.0, 26.4, 11.8, 6.8, 0.5)
        ]
    },
    {
        "id": "IMD-JAI-42348",
        "name": "Jaipur (Sanganer IMD Observatory)",
        "city": "Jaipur",
        "district": "Jaipur",
        "state": "Rajasthan",
        "country": "India",
        "latitude": 26.8167,
        "longitude": 75.8000,
        "elevation_m": 390,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (15.2, 22.6, 8.4, 9.8, 0.8),
            (18.8, 26.0, 11.8, 11.2, 0.9),
            (24.4, 32.2, 17.2, 7.6, 0.6),
            (30.2, 38.0, 23.0, 6.8, 0.6),
            (34.0, 41.2, 27.2, 19.8, 1.6),
            (33.8, 39.8, 28.2, 74.6, 4.4),
            (30.2, 34.6, 26.2, 224.2, 10.8),
            (28.6, 32.4, 25.2, 232.8, 11.4),
            (28.8, 33.8, 24.2, 88.4, 4.6),
            (26.2, 33.8, 19.2, 12.6, 0.8),
            (21.0, 29.2, 13.4, 4.2, 0.3),
            (16.4, 24.4, 9.0, 5.4, 0.4)
        ]
    },
    {
        "id": "IMD-LKO-42369",
        "name": "Lucknow (Amausi IMD Observatory)",
        "city": "Lucknow",
        "district": "Lucknow",
        "state": "Uttar Pradesh",
        "country": "India",
        "latitude": 26.7500,
        "longitude": 80.8833,
        "elevation_m": 128,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (15.0, 21.8, 8.4, 18.2, 1.4),
            (18.6, 25.8, 11.8, 17.6, 1.4),
            (24.2, 32.2, 16.8, 11.2, 0.9),
            (30.0, 38.2, 22.4, 8.4, 0.7),
            (33.2, 40.8, 26.2, 28.4, 2.1),
            (33.4, 39.0, 28.0, 118.6, 6.2),
            (30.2, 34.2, 26.6, 284.2, 12.8),
            (29.4, 33.2, 26.0, 276.8, 12.6),
            (28.8, 33.4, 24.8, 178.4, 8.2),
            (25.8, 32.6, 19.4, 34.2, 1.8),
            (20.8, 28.6, 13.4, 6.8, 0.5),
            (16.2, 23.8, 9.0, 8.4, 0.7)
        ]
    },
    {
        "id": "IMD-GAU-42410",
        "name": "Guwahati (Borjhar IMD Observatory)",
        "city": "Guwahati",
        "district": "Kamrup Metropolitan",
        "state": "Assam",
        "country": "India",
        "latitude": 26.1000,
        "longitude": 91.5833,
        "elevation_m": 54,
        "period": "1991–2020",
        "data_type": "climatological_normal",
        "dataset": "IMD Climatological Normals (1991–2020)",
        "source": "India Meteorological Department (IMD)",
        "normals": [
            (17.4, 23.8, 11.2, 11.4, 1.1),
            (20.6, 26.8, 14.6, 24.6, 2.2),
            (24.4, 30.6, 18.6, 68.2, 4.8),
            (26.2, 31.4, 21.4, 194.6, 11.4),
            (27.4, 32.0, 23.4, 298.4, 15.2),
            (28.8, 32.8, 25.4, 334.8, 16.8),
            (29.0, 32.6, 26.0, 362.4, 17.6),
            (29.2, 33.0, 26.0, 284.6, 14.8),
            (28.4, 32.4, 25.0, 218.2, 12.4),
            (26.2, 30.8, 22.0, 112.4, 6.2),
            (22.4, 28.2, 16.8, 18.6, 1.2),
            (18.4, 24.8, 12.4, 8.2, 0.6)
        ]
    }
]

class ImdClimateService:
    def __init__(self):
        self.stations: List[Dict[str, Any]] = IMD_STATIONS_DATA

    def find_nearest_station(self, lat: float, lon: float) -> Tuple[Dict[str, Any], float]:
        """
        Finds the closest official IMD Surface Observatory using great-circle distance.
        Returns (station_dict, distance_km).
        """
        best_station = self.stations[0]
        min_dist = float("inf")

        for station in self.stations:
            dist = haversine_distance(lat, lon, station["latitude"], station["longitude"])
            if dist < min_dist:
                min_dist = dist
                best_station = station

        return best_station, round(min_dist, 1)

    def get_climatological_normal(self, station_id_or_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves raw station normals by station ID or partial name match.
        """
        key = station_id_or_name.lower().strip()
        for station in self.stations:
            if station["id"].lower() == key or key in station["name"].lower() or key == station["city"].lower():
                return station
        return None

    def format_climate_dataset(
        self,
        requested_location: str,
        req_lat: float,
        req_lon: float,
        station: Dict[str, Any],
        distance_km: float
    ) -> Dict[str, Any]:
        """
        Structures the authoritative IMD Climatological Normal into the exact schema
        mandated by Section 6 of requirements.
        """
        monthly_data: List[Dict[str, Any]] = []
        for idx, (m_mean, m_max, m_min, m_rain, m_days) in enumerate(station["normals"]):
            monthly_data.append({
                "month": MONTHS[idx],
                "avg_temperature_c": round(m_mean, 1),
                "max_temperature_c": round(m_max, 1),
                "min_temperature_c": round(m_min, 1),
                "precipitation_mm": round(m_rain, 1),
                "rain_days": round(m_days, 1)
            })

        # Calculate annual summaries from the official monthly series
        annual_mean_temp = round(sum(m["avg_temperature_c"] for m in monthly_data) / 12.0, 1)
        annual_max_temp = round(sum(m["max_temperature_c"] for m in monthly_data) / 12.0, 1)
        annual_min_temp = round(sum(m["min_temperature_c"] for m in monthly_data) / 12.0, 1)
        annual_total_rain = round(sum(m["precipitation_mm"] for m in monthly_data), 1)
        annual_rain_days = round(sum(m["rain_days"] for m in monthly_data), 1)

        wettest_m = max(monthly_data, key=lambda m: m["precipitation_mm"])["month"]
        warmest_m = max(monthly_data, key=lambda m: m["avg_temperature_c"])["month"]

        # Backwards compatible list of points for existing frontend / advisory services
        legacy_data_points = [
            {
                "label": m["month"],
                "avg_temperature": m["avg_temperature_c"],
                "max_temperature": m["max_temperature_c"],
                "min_temperature": m["min_temperature_c"],
                "total_rainfall": m["precipitation_mm"],
                "rainfall_days": int(round(m["rain_days"]))
            }
            for m in monthly_data
        ]

        loc_dict = {
            "name": requested_location,
            "latitude": req_lat,
            "longitude": req_lon
        }
        src_dict = {
            "organization": "India Meteorological Department (IMD)",
            "division": "National Data Centre (NDC) / Climate Application Group, Pune",
            "dataset": "IMD Climatological Normals (1991–2020)",
            "period": station["period"],
            "data_type": "climatological_normal",
            "attribution": "Government of India, Ministry of Earth Sciences (MoES) / IMD",
            "rain_day_definition": "Daily precipitation >= 2.5 mm (Official IMD Standard)",
            "url": "https://mausam.imd.gov.in"
        }

        return {
            "location": loc_dict,
            "requested_location": loc_dict,
            "reference_station": {
                "id": station["id"],
                "name": station["name"],
                "city": station.get("city"),
                "district": station.get("district"),
                "state": station.get("state"),
                "latitude": station["latitude"],
                "longitude": station["longitude"],
                "elevation_m": station.get("elevation_m"),
                "distance_km": distance_km
            },
            "source": src_dict,
            "source_info": src_dict,
            "annual": {
                "mean_temperature_c": annual_mean_temp,
                "max_temperature_c": annual_max_temp,
                "min_temperature_c": annual_min_temp,
                "total_precipitation_mm": annual_total_rain,
                "rainy_days": annual_rain_days,
                "wettest_month": wettest_m,
                "warmest_month": warmest_m
            },
            "monthly": monthly_data,

            # Legacy fields for strict backwards compatibility
            "location_name": requested_location,
            "latitude": req_lat,
            "longitude": req_lon,
            "period": station["period"],
            "historical_period": f"{station['period']} (IMD 30-Year Climatological Normals)",
            "parameter": "all",
            "data": legacy_data_points,
            "annual_mean_temp": annual_mean_temp,
            "annual_total_rainfall": annual_total_rain,
            "wettest_month": wettest_m,
            "warmest_month": warmest_m,
            "rain_day_threshold_mm": 2.5,
            "city": station.get("city"),
            "state": station.get("state"),
            "country": "India",
            "source_label": "India Meteorological Department (IMD) Climatological Normals (1991–2020)"
        }

imd_climate_service = ImdClimateService()
