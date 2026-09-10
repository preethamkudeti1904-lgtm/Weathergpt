"""
Historical Disaster Database and Information Retrieval Service
Authoritative historical disaster records compiled from NDMA, IMD, CWC, INCOIS, and State DMAs.
"""

from typing import Dict, Any, List, Optional
import math

class HistoricalDisasterService:
    def __init__(self):
        # Curated authoritative historical records from official government reports
        self.records: List[Dict[str, Any]] = [
            # --- ANDHRA PRADESH & TELANGANA ---
            {
                "id": "ap_cyclone_michaung_2023",
                "event_name": "Severe Cyclonic Storm Michaung",
                "event_type": "Cyclone",
                "year": 2023,
                "start_date": "2023-12-03",
                "end_date": "2023-12-06",
                "location": "Bapatla, Guntur, Krishna, Nellore, Coastal Andhra Pradesh",
                "districts": ["guntur", "bapatla", "krishna", "spsr nellore", "prakasam"],
                "state": "Andhra Pradesh",
                "country": "India",
                "latitude": 15.9042,
                "longitude": 80.4674,
                "severity": "Severe",
                "rainfall_wind_metrics": "Wind gusts up to 110 km/h; peak 24h rainfall 200-390 mm across coastal mandals",
                "casualties": "17 fatalities across Tamil Nadu and Andhra Pradesh",
                "damage_info": "Substantial agricultural inundation across 400,000+ hectares of paddy and horticulture in coastal AP",
                "source": "India Meteorological Department (IMD) / NDMA / AP SDMA",
                "source_url": "https://sachet.ndma.gov.in/",
                "description": "Cyclonic storm Michaung made landfall close to Bapatla in south coastal Andhra Pradesh, generating severe gale winds and intense torrential precipitation across Guntur and Krishna delta basins."
            },
            {
                "id": "ap_krishna_flood_2019",
                "event_name": "Krishna River Major Flood",
                "event_type": "Flood",
                "year": 2019,
                "start_date": "2019-08-10",
                "end_date": "2019-08-18",
                "location": "Guntur, Vijayawada, Krishna River Basin, Andhra Pradesh",
                "districts": ["guntur", "krishna", "vijayawada", "amaravati"],
                "state": "Andhra Pradesh",
                "country": "India",
                "latitude": 16.5062,
                "longitude": 80.6480,
                "severity": "Very High",
                "rainfall_wind_metrics": "Prakasam Barrage peak discharge of 821,000 cusecs; heavy upper catchment rainfall in Western Ghats",
                "casualties": "No major casualties due to early CWC telemetry warnings and timely evacuation",
                "damage_info": "Submergence of riverbank villages, island habitations (Lanka villages), and crop inundation in Guntur and Krishna districts",
                "source": "Central Water Commission (CWC) / Andhra Pradesh Water Resources Dept",
                "source_url": "http://cwc.gov.in/",
                "description": "Unprecedented monsoon inflow into Nagarjuna Sagar and Srisailam reservoirs forced massive surplus discharge through Prakasam Barrage, causing extensive flooding across riparian areas of Guntur and Krishna."
            },
            {
                "id": "ap_cyclone_hudhud_2014",
                "event_name": "Extremely Severe Cyclonic Storm Hudhud",
                "event_type": "Cyclone",
                "year": 2014,
                "start_date": "2014-10-08",
                "end_date": "2014-10-14",
                "location": "Visakhapatnam, Vizianagaram, Srikakulam, Coastal Andhra Pradesh",
                "districts": ["visakhapatnam", "vizianagaram", "srikakulam", "east godavari"],
                "state": "Andhra Pradesh",
                "country": "India",
                "latitude": 17.6868,
                "longitude": 83.2185,
                "severity": "Extreme",
                "rainfall_wind_metrics": "Landfall sustained winds 185 km/h, gusts exceeding 215 km/h; rainfall exceeding 380 mm",
                "casualties": "124 fatalities in India",
                "damage_info": "Massive damage to Visakhapatnam urban infrastructure, electric power grid collapse, airport terminal roof collapse; $3.58 billion USD in economic losses",
                "source": "IMD Tropical Cyclone Report / NDMA Post-Disaster Assessment",
                "source_url": "https://rsmcnewdelhi.imd.gov.in/",
                "description": "Hudhud was a Category 4-equivalent tropical cyclone that made landfall directly over Kailasagiri, Visakhapatnam, causing historic wind destruction across north coastal Andhra Pradesh."
            },
            {
                "id": "ap_krishna_flood_2009",
                "event_name": "Historic Krishna & Tungabhadra Mega Flood",
                "event_type": "Flood",
                "year": 2009,
                "start_date": "2009-10-01",
                "end_date": "2009-10-07",
                "location": "Kurnool, Mahabubnagar, Guntur, Vijayawada, Andhra Pradesh",
                "districts": ["guntur", "kurnool", "krishna", "mahabubnagar"],
                "state": "Andhra Pradesh",
                "country": "India",
                "latitude": 15.8281,
                "longitude": 78.0373,
                "severity": "Extreme",
                "rainfall_wind_metrics": "Historic record discharge exceeding 1,110,000 cusecs at Prakasam Barrage; 24h rainfall up to 350 mm in Kurnool",
                "casualties": "Over 300 fatalities across Andhra Pradesh and Karnataka",
                "damage_info": "Complete submergence of Kurnool town under 10 feet of floodwaters; severe inundation of low-lying Guntur and Krishna riparian agricultural zones",
                "source": "Central Water Commission (CWC) Special Flood Memoir / NDMA",
                "source_url": "http://cwc.gov.in/",
                "description": "A rare deep depression triggered unprecedented rainfall over the lower Tungabhadra and Krishna basins, causing the largest recorded discharge in 100 years and massive inundation."
            },
            {
                "id": "ap_diviseema_cyclone_1977",
                "event_name": "1977 Andhra Pradesh / Diviseema Super Cyclone",
                "event_type": "Cyclone",
                "year": 1977,
                "start_date": "1977-11-14",
                "end_date": "1977-11-20",
                "location": "Diviseema, Krishna, Guntur, Coastal Andhra Pradesh",
                "districts": ["krishna", "guntur", "bapatla"],
                "state": "Andhra Pradesh",
                "country": "India",
                "latitude": 15.9800,
                "longitude": 80.8500,
                "severity": "Catastrophic",
                "rainfall_wind_metrics": "Sustained winds 200+ km/h; 5-6 meter high storm surge penetrating 40 km inland",
                "casualties": "Over 10,000 lives lost primarily due to the catastrophic tidal surge",
                "damage_info": "Complete destruction of seaside villages and severe crop salinity across Diviseema, Repalle, and Bapatla taluks",
                "source": "IMD Historical Monographs / AP State Archives",
                "source_url": "https://mausam.imd.gov.in/",
                "description": "One of the deadliest cyclones in modern Indian history. A massive storm surge swept across Diviseema island and the coastal fringes of Guntur and Krishna districts."
            },
            {
                "id": "tg_hyderabad_floods_2020",
                "event_name": "2020 Hyderabad Cloudburst & Urban Flash Floods",
                "event_type": "Flash Flood",
                "year": 2020,
                "start_date": "2020-10-13",
                "end_date": "2020-10-15",
                "location": "Hyderabad, Secunderabad, Telangana",
                "districts": ["hyderabad", "rangareddy", "medchal-malkajgiri"],
                "state": "Telangana",
                "country": "India",
                "latitude": 17.3850,
                "longitude": 78.4867,
                "severity": "Very High",
                "rainfall_wind_metrics": "24-hour rainfall of 241.5 mm at Begumpet and 320 mm at Ghatkesar; highest October rainfall in over a century",
                "casualties": "Over 50 fatalities",
                "damage_info": "Severe urban inundation of 40,000+ homes; major roads, cellars, and underpasses flooded; Musi river overtopped retaining banks",
                "source": "IMD Hyderabad Meteorological Centre / GHMC / NDMA",
                "source_url": "https://sachet.ndma.gov.in/",
                "description": "Remnants of a deep depression over the Bay of Bengal stalled over Telangana, dumping historic torrential downpours that overwhelmed Hyderabad's stormwater drainage network."
            },

            # --- TAMIL NADU ---
            {
                "id": "tn_chennai_floods_2015",
                "event_name": "2015 South India & Chennai Mega Floods",
                "event_type": "Flood",
                "year": 2015,
                "start_date": "2015-11-08",
                "end_date": "2015-12-04",
                "location": "Chennai, Kanchipuram, Tiruvallur, Cuddalore, Tamil Nadu",
                "districts": ["chennai", "kanchipuram", "tiruvallur", "cuddalore", "chengalpattu"],
                "state": "Tamil Nadu",
                "country": "India",
                "latitude": 13.0827,
                "longitude": 80.2707,
                "severity": "Catastrophic",
                "rainfall_wind_metrics": "494 mm single-day rainfall on 1 December 2015 at Tambaram; Adyar River peak flow 100,000 cusecs",
                "casualties": "Over 500 fatalities across south India",
                "damage_info": "Chennai International Airport submerged and closed for days; city power and cell grid collapsed; economic damage exceeding ₹20,000 crore",
                "source": "IMD Climate Diagnostics / CWC Special Report / NDMA",
                "source_url": "https://mausam.imd.gov.in/",
                "description": "Vigorous Northeast Monsoon conditions compounded by an intense coastal low pressure system delivered unprecedented record rainfall, triggering catastrophic urban flooding across the Adyar and Cooum basins."
            },
            {
                "id": "tn_cyclone_vardah_2016",
                "event_name": "Very Severe Cyclonic Storm Vardah",
                "event_type": "Cyclone",
                "year": 2016,
                "start_date": "2016-12-06",
                "end_date": "2016-12-13",
                "location": "Chennai, Tiruvallur, Kanchipuram, Tamil Nadu",
                "districts": ["chennai", "tiruvallur", "kanchipuram"],
                "state": "Tamil Nadu",
                "country": "India",
                "latitude": 13.0827,
                "longitude": 80.2707,
                "severity": "Very High",
                "rainfall_wind_metrics": "Sustained winds 130 km/h, gusts 155 km/h; 200 mm rainfall",
                "casualties": "18 fatalities in Tamil Nadu",
                "damage_info": "Uprooting of over 100,000 trees across Chennai metropolitan area, widespread telecommunications and power blackout",
                "source": "IMD / Tamil Nadu State Disaster Management Authority (TNSDMA)",
                "source_url": "https://tnsdma.tn.gov.in/",
                "description": "Vardah made landfall directly over northern Chennai, causing severe tree fall, building facade destruction, and urban utility outages."
            },
            {
                "id": "tn_tsunami_2004",
                "event_name": "2004 Indian Ocean Tsunami",
                "event_type": "Tsunami",
                "year": 2004,
                "start_date": "2004-12-26",
                "end_date": "2004-12-26",
                "location": "Nagapattinam, Kanyakumari, Cuddalore, Chennai, Coastal Tamil Nadu",
                "districts": ["nagapattinam", "cuddalore", "kanyakumari", "chennai", "villupuram"],
                "state": "Tamil Nadu",
                "country": "India",
                "latitude": 10.7656,
                "longitude": 79.8424,
                "severity": "Catastrophic",
                "rainfall_wind_metrics": "Tsunami run-up heights of 3 to 10 meters following Mw 9.1-9.3 Sumatra-Andaman megathrust earthquake",
                "casualties": "Over 10,000 fatalities in India (over 6,000 in Nagapattinam alone)",
                "damage_info": "Total devastation of fishing villages, catamarans, and coastal settlements across 1,000+ km of coastline",
                "source": "INCOIS / Survey of India / NDMA",
                "source_url": "https://incois.gov.in/",
                "description": "The catastrophic undersea earthquake off northern Sumatra triggered massive trans-oceanic tsunami waves that struck coastal Tamil Nadu without warning, leading to the creation of INCOIS's National Tsunami Early Warning System."
            },

            # --- MAHARASHTRA ---
            {
                "id": "mh_mumbai_cloudburst_2005",
                "event_name": "2005 Mumbai Mega Cloudburst & Deluge",
                "event_type": "Cloudburst",
                "year": 2005,
                "start_date": "2005-07-26",
                "end_date": "2005-07-27",
                "location": "Mumbai, Thane, Raigad, Maharashtra",
                "districts": ["mumbai", "mumbai suburban", "thane", "raigad"],
                "state": "Maharashtra",
                "country": "India",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "severity": "Catastrophic",
                "rainfall_wind_metrics": "944.2 mm of rainfall in 24 hours at Santacruz observatory; highest recorded in Mumbai's modern history",
                "casualties": "Over 1,000 fatalities across Maharashtra",
                "damage_info": "Complete urban gridlock, overflowing Mithi river, thousands of vehicles submerged, local trains and air traffic grounded for 48 hours",
                "source": "IMD Historical Data / Government of Maharashtra Fact-Finding Committee",
                "source_url": "https://mausam.imd.gov.in/",
                "description": "A mesoscale convective system anchored over Mumbai dumped nearly a meter of water in one day during high tide, resulting in catastrophic urban submergence."
            },
            {
                "id": "mh_cyclone_nisarga_2020",
                "event_name": "Severe Cyclonic Storm Nisarga",
                "event_type": "Cyclone",
                "year": 2020,
                "start_date": "2020-06-01",
                "end_date": "2020-06-04",
                "location": "Shrivardhan, Raigad, Mumbai, Ratnagiri, Maharashtra",
                "districts": ["raigad", "mumbai", "ratnagiri", "pune"],
                "state": "Maharashtra",
                "country": "India",
                "latitude": 18.0500,
                "longitude": 73.0100,
                "severity": "Very High",
                "rainfall_wind_metrics": "Landfall sustained winds 110-120 km/h; heavy rainfall up to 150-200 mm",
                "casualties": "6 fatalities in Maharashtra",
                "damage_info": "Extensive damage to betel nut, coconut plantations, and tin roofs across Raigad; electricity infrastructure damaged",
                "source": "IMD Tropical Cyclone Report / SDMA Maharashtra",
                "source_url": "https://rsmcnewdelhi.imd.gov.in/",
                "description": "Nisarga was the strongest cyclone to strike Maharashtra's Konkan coast near Mumbai since 1891, making landfall south of Alibag."
            },

            # --- WEST BENGAL & ODISHA ---
            {
                "id": "wb_super_cyclone_amphan_2020",
                "event_name": "Super Cyclonic Storm Amphan",
                "event_type": "Cyclone",
                "year": 2020,
                "start_date": "2020-05-16",
                "end_date": "2020-05-21",
                "location": "Sundarbans, Kolkata, South & North 24 Parganas, East Midnapore, West Bengal",
                "districts": ["kolkata", "south 24 parganas", "north 24 parganas", "purba medinipur", "murshidabad"],
                "state": "West Bengal",
                "country": "India",
                "latitude": 21.6500,
                "longitude": 88.3500,
                "severity": "Catastrophic",
                "rainfall_wind_metrics": "Landfall sustained winds 155-165 km/h with gusts to 185 km/h; storm surge of 4-5 meters in Sundarbans",
                "casualties": "98 fatalities in West Bengal",
                "damage_info": "Over ₹1 lakh crore in economic losses; over 10 million people impacted; major electricity and water disruption in Kolkata for a week",
                "source": "IMD / NDMA / West Bengal Disaster Management Dept",
                "source_url": "https://sachet.ndma.gov.in/",
                "description": "Amphan was the first Super Cyclonic Storm in the Bay of Bengal since 1999, tearing through coastal delta areas and wreaking havoc across metropolitan Kolkata."
            },
            {
                "id": "wb_murshidabad_floods_2000",
                "event_name": "2000 West Bengal Mega Inundation",
                "event_type": "Flood",
                "year": 2000,
                "start_date": "2000-09-18",
                "end_date": "2000-09-28",
                "location": "Murshidabad, Nadia, Birbhum, Malda, West Bengal",
                "districts": ["murshidabad", "nadia", "birbhum", "malda", "hooghly"],
                "state": "West Bengal",
                "country": "India",
                "latitude": 24.1759,
                "longitude": 88.2802,
                "severity": "Catastrophic",
                "rainfall_wind_metrics": "Continuous downpours exceeding 400 mm in 4 days across Gangetic basin; Bhagirathi and Jalangi breached embankments",
                "casualties": "Over 1,200 fatalities",
                "damage_info": "Over 20 million people marooned; widespread agricultural submergence in Murshidabad and Nadia",
                "source": "Central Water Commission (CWC) / Irrigation & Waterways Dept WB",
                "source_url": "http://cwc.gov.in/",
                "description": "Unprecedented monsoon rainfall caused major river breaches along the Bhagirathi, Padma, and Mayurakshi rivers, inundating vast tracts of Murshidabad district."
            },
            {
                "id": "od_super_cyclone_1999",
                "event_name": "1999 Odisha Super Cyclone",
                "event_type": "Cyclone",
                "year": 1999,
                "start_date": "1999-10-25",
                "end_date": "1999-11-04",
                "location": "Paradip, Jagatsinghpur, Kendrapara, Puri, Cuttack, Bhubaneswar, Odisha",
                "districts": ["jagatsinghpur", "kendrapara", "puri", "cuttack", "khordha"],
                "state": "Odisha",
                "country": "India",
                "latitude": 20.3168,
                "longitude": 86.6114,
                "severity": "Catastrophic",
                "rainfall_wind_metrics": "Sustained winds 260 km/h; tidal surge up to 7-8 meters penetrating 20 km inland; 400-800 mm rainfall",
                "casualties": "9,887 confirmed fatalities (primarily in Jagatsinghpur)",
                "damage_info": "Complete destruction of 1.6 million homes, loss of 400,000+ livestock, total collapse of regional economy",
                "source": "IMD Historical Memoirs / OSDMA / NDMA",
                "source_url": "https://osdma.org/",
                "description": "The strongest recorded tropical cyclone in the North Indian Ocean basin. It transformed disaster management in India and led directly to the creation of NDMA and OSDMA."
            },
            {
                "id": "od_cyclone_fani_2019",
                "event_name": "Extremely Severe Cyclonic Storm Fani",
                "event_type": "Cyclone",
                "year": 2019,
                "start_date": "2019-04-26",
                "end_date": "2019-05-04",
                "location": "Puri, Bhubaneswar, Cuttack, Coastal Odisha",
                "districts": ["puri", "khordha", "cuttack", "ganjam"],
                "state": "Odisha",
                "country": "India",
                "latitude": 19.8135,
                "longitude": 85.8312,
                "severity": "Extreme",
                "rainfall_wind_metrics": "Landfall sustained winds 175-185 km/h with gusts to 205 km/h",
                "casualties": "64 fatalities (kept minimal by pre-emptive evacuation of 1.2 million citizens)",
                "damage_info": "Massive destruction of electrical transmission towers, water supply, and building roofs across Puri and Bhubaneswar",
                "source": "IMD / OSDMA / NDMA",
                "source_url": "https://sachet.ndma.gov.in/",
                "description": "Fani was a rare pre-monsoon Category 4-equivalent cyclone that hit Puri with immense destructive power; praised globally for Odisha's zero-casualty evacuation mission."
            },

            # --- KERALA ---
            {
                "id": "kl_mega_floods_2018",
                "event_name": "2018 Great Kerala Floods",
                "event_type": "Flood",
                "year": 2018,
                "start_date": "2018-08-08",
                "end_date": "2018-08-20",
                "location": "Idukki, Ernakulam, Wayanad, Alappuzha, Pathanamthitta, Thrissur, Kerala",
                "districts": ["idukki", "ernakulam", "wayanad", "alappuzha", "pathanamthitta", "thrissur", "kottayam"],
                "state": "Kerala",
                "country": "India",
                "latitude": 9.8500,
                "longitude": 76.9667,
                "severity": "Catastrophic",
                "rainfall_wind_metrics": "State received 2,346 mm of monsoon rainfall (42% above normal); 35 dams opened simultaneously including Idukki and Mullaperiyar",
                "casualties": "483 fatalities; 140 missing",
                "damage_info": "Over 1.45 million people sheltered in relief camps; Kochi Airport submerged; ₹40,000 crore estimated economic reconstruction need",
                "source": "IMD / Central Water Commission / Kerala State Disaster Management Authority (KSDMA)",
                "source_url": "https://sdma.kerala.gov.in/",
                "description": "The worst flooding in Kerala in nearly a century (since the Great Flood of 99 in 1924), triggered by persistent active monsoon spells and filled reservoirs."
            },
            {
                "id": "kl_wayanad_landslides_2024",
                "event_name": "2024 Wayanad Landslide Tragedy",
                "event_type": "Landslide",
                "year": 2024,
                "start_date": "2024-07-30",
                "end_date": "2024-08-05",
                "location": "Chooralmala, Mundakkai, Meppadi, Wayanad, Kerala",
                "districts": ["wayanad"],
                "state": "Kerala",
                "country": "India",
                "latitude": 11.5367,
                "longitude": 76.1260,
                "severity": "Catastrophic",
                "rainfall_wind_metrics": "Over 572 mm of rainfall recorded in 48 hours in the Western Ghats catchment above Meppadi",
                "casualties": "Over 400 lives lost",
                "damage_info": "Complete destruction of Chooralmala bridge, Mundakkai township, schools, and tea estate residential quarters",
                "source": "Geological Survey of India (GSI) / IMD / NDMA / KSDMA",
                "source_url": "https://sachet.ndma.gov.in/",
                "description": "One of the deadliest slope-failure disasters in Indian history. Two sequential catastrophic debris flows swept through Mundakkai and Chooralmala at night following relentless torrential rains."
            },

            # --- NORTH INDIA (DELHI, UTTARAKHAND, HP) ---
            {
                "id": "del_yamuna_flood_2023",
                "event_name": "2023 Delhi Yamuna River Record Inundation",
                "event_type": "Flood",
                "year": 2023,
                "start_date": "2023-07-09",
                "end_date": "2023-07-16",
                "location": "Old Delhi, Kashmere Gate, Red Fort, Civil Lines, Yamuna Bazar, Delhi",
                "districts": ["central delhi", "north delhi", "north east delhi", "east delhi", "delhi", "new delhi"],
                "state": "Delhi",
                "country": "India",
                "latitude": 28.6139,
                "longitude": 77.2090,
                "severity": "Very High",
                "rainfall_wind_metrics": "Yamuna water level reached all-time historic high of 208.66 meters, breaking 45-year-old record (207.49 m in 1978); 350,000+ cusecs discharge from Hathnikund",
                "casualties": "Zero direct casualties due to preemptive evacuation of 25,000+ riverbed residents",
                "damage_info": "Water entered Supreme Court perimeter, Red Fort premises, Ring Road submerged, Chandrawal and Wazirabad water treatment plants halted",
                "source": "Central Water Commission (CWC) Delhi / Delhi Disaster Management Authority (DDMA)",
                "source_url": "http://cwc.gov.in/",
                "description": "Extreme torrential rainfall over Himachal Pradesh and Uttarakhand flowed into the Hathnikund Barrage, generating a massive crest downstream that broke Delhi's all-time flood height record."
            },
            {
                "id": "uk_kedarnath_disaster_2013",
                "event_name": "2013 Uttarakhand Multi-River Flash Floods & Cloudburst",
                "event_type": "Cloudburst",
                "year": 2013,
                "start_date": "2013-06-14",
                "end_date": "2013-06-18",
                "location": "Kedarnath, Mandakini, Alaknanda, Chamoli, Rudraprayag, Uttarkashi, Uttarakhand",
                "districts": ["rudraprayag", "chamoli", "uttarkashi", "pithoragarh", "dehradun"],
                "state": "Uttarakhand",
                "country": "India",
                "latitude": 30.7346,
                "longitude": 79.0669,
                "severity": "Catastrophic",
                "rainfall_wind_metrics": "375% of normal monsoon precipitation in 3 days; Chorabari glacial lake breach dumped millions of cubic meters of mud and boulders in minutes",
                "casualties": "Estimated over 5,700 fatalities",
                "damage_info": "Complete destruction of Rambara town, Kedarnath pilgrimage pedestrian path, dozens of bridges, hotels, and roadways; largest aerial rescue operation in military history (Operation Surya Hope)",
                "source": "Wadia Institute of Himalayan Geology / IMD / NDMA / CWC",
                "source_url": "https://sachet.ndma.gov.in/",
                "description": "An early monsoon cloudburst combined with melting glacial snowpack and the bursting of Chorabari Lake devastated the Kedarnath temple town and the entire Mandakini valley."
            },
            {
                "id": "as_brahmaputra_floods_2022",
                "event_name": "2022 Assam Floods & Silchar Inundation",
                "event_type": "Flood",
                "year": 2022,
                "start_date": "2022-05-15",
                "end_date": "2022-06-30",
                "location": "Silchar, Cachar, Barpeta, Nagaon, Kamrup, Brahmaputra & Barak Valleys, Assam",
                "districts": ["cachar", "barpeta", "nagaon", "kamrup", "guwahati", "dhubri"],
                "state": "Assam",
                "country": "India",
                "latitude": 26.1445,
                "longitude": 91.7362,
                "severity": "Catastrophic",
                "rainfall_wind_metrics": "Cherrapunji recorded 972 mm in 24h; Barak river breached Bethukandi dyke; Brahmaputra flowing above danger mark at 12 stations",
                "casualties": "Over 190 fatalities",
                "damage_info": "Silchar town submerged for 10 consecutive days under 5-8 feet of floodwater; 5.4 million people impacted across 32 districts",
                "source": "Central Water Commission (CWC) Assam / ASDMA / NDMA",
                "source_url": "http://cwc.gov.in/",
                "description": "Dual waves of pre-monsoon and monsoon flooding submerged vast portions of Assam, with unprecedented catastrophic inundation of Silchar city in the Barak valley."
            },

            # --- BENCHMARK GLOBAL CITIES ---
            {
                "id": "us_hurricane_sandy_2012",
                "event_name": "Hurricane Sandy (Superstorm Sandy)",
                "event_type": "Cyclone",
                "year": 2012,
                "start_date": "2012-10-22",
                "end_date": "2012-11-02",
                "location": "New York City, New Jersey, Long Island, United States",
                "districts": ["new york", "kings", "queens", "bronx", "richmond"],
                "state": "New York",
                "country": "United States",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "severity": "Catastrophic",
                "rainfall_wind_metrics": "Storm surge of 4.3 meters (14 feet) at The Battery, Manhattan; peak wind gusts 130 km/h",
                "casualties": "233 fatalities across 8 countries (44 in NYC)",
                "damage_info": "Flooding of 7 NYC subway tunnels, Wall Street financial district submerged, widespread electrical blackouts; $65 billion USD damage",
                "source": "National Oceanic and Atmospheric Administration (NOAA) / National Weather Service (NWS)",
                "source_url": "https://www.nhc.noaa.gov/",
                "description": "Post-tropical cyclone Sandy generated an unprecedented record storm surge that flooded lower Manhattan, subway tubes, and coastal Brooklyn and Queens."
            },
            {
                "id": "uk_north_sea_flood_1953",
                "event_name": "1953 North Sea Flood & London Storm Surge",
                "event_type": "Storm Surge",
                "year": 1953,
                "start_date": "1953-01-31",
                "end_date": "1953-02-01",
                "location": "Thames Estuary, London, East Coast, United Kingdom",
                "districts": ["london", "essex", "kent", "norfolk"],
                "state": "England",
                "country": "United Kingdom",
                "latitude": 51.5074,
                "longitude": -0.1278,
                "severity": "Catastrophic",
                "rainfall_wind_metrics": "Storm surge of 3.35 meters combined with spring high tide; northerly gale winds over 120 km/h",
                "casualties": "307 fatalities in the UK; 1,800+ in the Netherlands",
                "damage_info": "Breach of 1,200 sea defenses; inundated 160,000 acres; spurred the construction of the Thames Barrier",
                "source": "UK Met Office / UK Environment Agency",
                "source_url": "https://www.metoffice.gov.uk/",
                "description": "The catastrophic North Sea storm surge funneled massive sea waters into the Thames estuary, transforming British coastal engineering and flood defense."
            },
            {
                "id": "jp_typhoon_hagibis_2019",
                "event_name": "2019 Typhoon Hagibis (Reiwa 1 East Japan Typhoon)",
                "event_type": "Cyclone",
                "year": 2019,
                "start_date": "2019-10-06",
                "end_date": "2019-10-13",
                "location": "Tokyo, Kanagawa, Shizuoka, Nagano, Japan",
                "districts": ["tokyo", "kanagawa", "nagano", "shizuoka"],
                "state": "Kanto",
                "country": "Japan",
                "latitude": 35.6762,
                "longitude": 139.6503,
                "severity": "Extreme",
                "rainfall_wind_metrics": "Record 48h rainfall of 1,000 mm in Hakone; sustained winds 150 km/h with gusts over 210 km/h; 140 river dyke breaches",
                "casualties": "98 fatalities in Japan",
                "damage_info": "Submergence of Hokuriku Shinkansen bullet train depot; severe flooding of Chikuma and Tama river basins; $15 billion USD damage",
                "source": "Japan Meteorological Agency (JMA)",
                "source_url": "https://www.jma.go.jp/",
                "description": "Hagibis was one of the largest and most destructive typhoons to strike the Greater Tokyo metropolitan area and eastern Japan in decades."
            }
        ]

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def get_historical_disasters(
        self,
        location_name: str,
        district: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = "India",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        event_type: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Query verified historical disaster records matching the target location.
        Priority:
        1. Exact district/city match (Highest relevance)
        2. Proximity distance (Haversine <= 250 km)
        3. State match
        4. Country match (only if explicit search)
        """
        loc_lower = location_name.lower().strip()
        dist_lower = (district or "").lower().strip()
        state_lower = (state or "").lower().strip()
        cntry_lower = (country or "India").lower().strip()

        matched: List[Dict[str, Any]] = []

        for rec in self.records:
            score = 0
            rec_districts = [d.lower() for d in rec.get("districts", [])]
            rec_state = rec.get("state", "").lower()
            rec_country = rec.get("country", "").lower()
            rec_loc = rec.get("location", "").lower()

            # Event type filter if specified
            if event_type:
                if event_type.lower() not in rec.get("event_type", "").lower():
                    continue

            # 1. District or city direct match
            if any(d in loc_lower for d in rec_districts) or (dist_lower and dist_lower in rec_districts):
                score += 100
            elif any(d in rec_loc for d in [loc_lower, dist_lower]) if (loc_lower or dist_lower) else False:
                score += 80

            # 2. Coordinates proximity match (if provided)
            if latitude is not None and longitude is not None:
                dist_km = self._haversine_distance(latitude, longitude, rec["latitude"], rec["longitude"])
                if dist_km <= 75:
                    score += 90
                elif dist_km <= 150:
                    score += 60
                elif dist_km <= 300:
                    score += 30

            # 3. State match
            if state_lower and (state_lower in rec_state or rec_state in state_lower):
                score += 40
            elif any(word in rec_loc for word in state_lower.split()):
                score += 25

            # 4. Country match
            if cntry_lower and cntry_lower == rec_country:
                score += 10

            if score > 30:
                rec_copy = dict(rec)
                rec_copy["relevance_score"] = score
                matched.append(rec_copy)

        # Sort by relevance score desc, then by year desc
        matched.sort(key=lambda x: (x["relevance_score"], x["year"]), reverse=True)
        final_list = matched[:limit]

        return {
            "location_queried": location_name,
            "district": district,
            "state": state,
            "country": country,
            "total_found": len(final_list),
            "events": final_list,
            "has_records": len(final_list) > 0,
            "status": "records_found" if final_list else "no_historical_records_for_locality"
        }

historical_disaster_service = HistoricalDisasterService()
