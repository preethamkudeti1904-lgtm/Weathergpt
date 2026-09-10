"""
Authoritative Agrometeorological Crop Thresholds Database
Derived from:
- Indian Council of Agricultural Research (ICAR) Crop Production Guides
- India Meteorological Department (IMD) - Gramin Krishi Mausam Sewa (GKMS)
- Acharya N.G. Ranga Agricultural University (ANGRAU), Andhra Pradesh
- Tamil Nadu Agricultural University (TNAU) Agritech Portal
- FAO Irrigation and Drainage Paper No. 56 (Crop Evapotranspiration)
"""

from typing import Dict, Any, List, Optional

# Supported Crops Registry
CROPS_REGISTRY = [
    {"id": "rice", "name": "Rice / Paddy", "scientific_name": "Oryza sativa", "category": "Cereal"},
    {"id": "cotton", "name": "Cotton", "scientific_name": "Gossypium hirsutum", "category": "Fiber"},
    {"id": "chilli", "name": "Chilli", "scientific_name": "Capsicum annuum", "category": "Spice / Cash"},
    {"id": "maize", "name": "Maize", "scientific_name": "Zea mays", "category": "Cereal / Coarse Grain"},
    {"id": "groundnut", "name": "Groundnut", "scientific_name": "Arachis hypogaea", "category": "Oilseed"},
    {"id": "sugarcane", "name": "Sugarcane", "scientific_name": "Saccharum officinarum", "category": "Sugar / Cash"},
    {"id": "turmeric", "name": "Turmeric", "scientific_name": "Curcuma longa", "category": "Spice / Cash"},
    {"id": "pulses", "name": "Pulses", "scientific_name": "Legumes (Vigna / Cajanus)", "category": "Pulse"},
    {"id": "vegetables", "name": "Vegetables", "scientific_name": "Horticultural Crops", "category": "Horticulture"},
    {"id": "tomato", "name": "Tomato", "scientific_name": "Solanum lycopersicum", "category": "Vegetable"},
    {"id": "onion", "name": "Onion", "scientific_name": "Allium cepa", "category": "Vegetable"},
    {"id": "custom", "name": "Custom Crop", "scientific_name": "Custom Agromet Profile", "category": "General"}
]

# Supported Phonological Growth Stages
GROWTH_STAGES_REGISTRY = [
    {"id": "land_preparation", "name": "Land Preparation", "description": "Tillage, plowing, leveling, and basal bed preparation"},
    {"id": "sowing", "name": "Sowing", "description": "Seed drilling, broadcasting, or direct seeding"},
    {"id": "germination", "name": "Germination", "description": "Radicle emergence and early sprout establishment"},
    {"id": "seedling", "name": "Seedling / Nursery", "description": "Early vegetative seedling growth or nursery bed phase"},
    {"id": "vegetative", "name": "Vegetative / Tillering", "description": "Rapid vegetative growth, branching, tillering, and biomass accumulation"},
    {"id": "flowering", "name": "Flowering / Anthesis", "description": "Inflorescence emergence, pollination, and fertilization"},
    {"id": "fruiting", "name": "Fruiting / Boll Development", "description": "Fruit set, pod formation, or boll swelling"},
    {"id": "grain_filling", "name": "Grain Filling / Milking", "description": "Starch translocation, milk stage to dough stage"},
    {"id": "maturity", "name": "Maturity / Ripening", "description": "Physiological maturity, color change, moisture decline"},
    {"id": "harvest", "name": "Harvest", "description": "Active reaping, threshing, lifting, or picking"},
    {"id": "post_harvest", "name": "Post-Harvest / Drying", "description": "Field drying, winnowing, curing, and bagging"}
]

# Baseline agrometeorological thresholds per crop and growth stage
CROP_THRESHOLDS: Dict[str, Dict[str, Any]] = {
    "rice": {
        "scientific_name": "Oryza sativa",
        "reference_source": "ICAR-National Rice Research Institute (NRRI) & ANGRAU Rice Package",
        "stages": {
            "land_preparation": {
                "kc": 1.05,
                "temp_opt_min": 22.0, "temp_opt_max": 34.0, "temp_heat_stress": 38.0, "temp_cold_stress": 18.0,
                "rain_critical_daily_mm": 50.0, "rain_waterlogging_tolerance_days": 10,
                "humidity_disease_risk_min": 85,
                "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 40.0,
                "soil_moisture_pref": "Saturated to flooded puddle",
                "stage_key_risks": "Excessive downpours disrupt bund strengthening and plowing; prolonged rain delays field leveling."
            },
            "sowing": {
                "kc": 1.10,
                "temp_opt_min": 22.0, "temp_opt_max": 32.0, "temp_heat_stress": 36.0, "temp_cold_stress": 18.0,
                "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 2,
                "humidity_disease_risk_min": 85,
                "wind_spraying_max_kmh": 12.0, "wind_lodging_risk_kmh": 35.0,
                "soil_moisture_pref": "Moist, shallow puddle",
                "stage_key_risks": "Heavy rainfall causes seed displacement, burying seeds in silt, or rotting pre-germinated seed."
            },
            "germination": {
                "kc": 1.10,
                "temp_opt_min": 24.0, "temp_opt_max": 33.0, "temp_heat_stress": 37.0, "temp_cold_stress": 19.0,
                "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 2,
                "humidity_disease_risk_min": 85,
                "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 35.0,
                "soil_moisture_pref": "Thin water film (1-2 cm)",
                "stage_key_risks": "Deep submergence restricts oxygen diffusion and causes poor coleoptile emergence."
            },
            "seedling": {
                "kc": 1.12,
                "temp_opt_min": 23.0, "temp_opt_max": 33.0, "temp_heat_stress": 36.0, "temp_cold_stress": 17.0,
                "rain_critical_daily_mm": 35.0, "rain_waterlogging_tolerance_days": 3,
                "humidity_disease_risk_min": 82,
                "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 35.0,
                "soil_moisture_pref": "Standing water 2-3 cm",
                "stage_key_risks": "Submergence in muddy floodwaters causes damping off and seedling wash-away; chilling below 17°C stunts growth."
            },
            "vegetative": {
                "kc": 1.15,
                "temp_opt_min": 24.0, "temp_opt_max": 34.0, "temp_heat_stress": 37.0, "temp_cold_stress": 18.0,
                "rain_critical_daily_mm": 50.0, "rain_waterlogging_tolerance_days": 5,
                "humidity_disease_risk_min": 80,
                "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 38.0,
                "soil_moisture_pref": "Standing water 3-5 cm",
                "stage_key_risks": "High canopy humidity (>80%) with overcast skies triggers blast (Pyricularia oryzae) and bacterial leaf blight (Xanthomonas)."
            },
            "flowering": {
                "kc": 1.20,
                "temp_opt_min": 24.0, "temp_opt_max": 31.0, "temp_heat_stress": 35.0, "temp_cold_stress": 20.0,
                "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 4,
                "humidity_disease_risk_min": 80,
                "wind_spraying_max_kmh": 12.0, "wind_lodging_risk_kmh": 25.0,
                "soil_moisture_pref": "Standing water 5 cm",
                "stage_key_risks": "Highly critical stage: rain during anthesis washes away pollen; temperatures >35°C or <20°C cause severe spikelet sterility."
            },
            "fruiting": {
                "kc": 1.18,
                "temp_opt_min": 23.0, "temp_opt_max": 32.0, "temp_heat_stress": 36.0, "temp_cold_stress": 19.0,
                "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 4,
                "humidity_disease_risk_min": 80,
                "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 30.0,
                "soil_moisture_pref": "Saturated soil",
                "stage_key_risks": "Continuous cloudy damp weather favors sheath blight and false smut development."
            },
            "grain_filling": {
                "kc": 1.15,
                "temp_opt_min": 22.0, "temp_opt_max": 32.0, "temp_heat_stress": 35.0, "temp_cold_stress": 18.0,
                "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 4,
                "humidity_disease_risk_min": 82,
                "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 28.0,
                "soil_moisture_pref": "Saturated to moist (drain gradually)",
                "stage_key_risks": "Squall winds (>28 km/h) cause physical panicle lodging and grain shattering."
            },
            "maturity": {
                "kc": 0.90,
                "temp_opt_min": 20.0, "temp_opt_max": 33.0, "temp_heat_stress": 37.0, "temp_cold_stress": 16.0,
                "rain_critical_daily_mm": 10.0, "rain_waterlogging_tolerance_days": 2,
                "humidity_disease_risk_min": 80,
                "wind_spraying_max_kmh": 18.0, "wind_lodging_risk_kmh": 25.0,
                "soil_moisture_pref": "Dry field (drain 10 days before harvest)",
                "stage_key_risks": "Standing water or rainfall at maturity triggers viviparous grain sprouting and fungal discoloration."
            },
            "harvest": {
                "kc": 0.70,
                "temp_opt_min": 18.0, "temp_opt_max": 35.0, "temp_heat_stress": 38.0, "temp_cold_stress": 15.0,
                "rain_critical_daily_mm": 3.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 75,
                "wind_spraying_max_kmh": 20.0, "wind_lodging_risk_kmh": 22.0,
                "soil_moisture_pref": "Firm, dry soil surface",
                "stage_key_risks": "Rainfall severely disrupts combine harvesting, causes grain shedding, and prevents field drying."
            },
            "post_harvest": {
                "kc": 0.50,
                "temp_opt_min": 20.0, "temp_opt_max": 36.0, "temp_heat_stress": 40.0, "temp_cold_stress": 14.0,
                "rain_critical_daily_mm": 2.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 70,
                "wind_spraying_max_kmh": 25.0, "wind_lodging_risk_kmh": 35.0,
                "soil_moisture_pref": "Dry threshing yards",
                "stage_key_risks": "Rain on harvested paddy heaps causes heating, mycotoxin accumulation, and quality deterioration."
            }
        }
    },

    "cotton": {
        "scientific_name": "Gossypium hirsutum",
        "reference_source": "ICAR-Central Institute for Cotton Research (CICR) & ANGRAU Cotton Guide",
        "stages": {
            "land_preparation": {
                "kc": 0.50,
                "temp_opt_min": 20.0, "temp_opt_max": 35.0, "temp_heat_stress": 40.0, "temp_cold_stress": 15.0,
                "rain_critical_daily_mm": 35.0, "rain_waterlogging_tolerance_days": 4,
                "humidity_disease_risk_min": 85,
                "wind_spraying_max_kmh": 18.0, "wind_lodging_risk_kmh": 35.0,
                "soil_moisture_pref": "Dry to friable",
                "stage_key_risks": "Wet soil leads to clod formation during deep summer plowing."
            },
            "sowing": {
                "kc": 0.55,
                "temp_opt_min": 22.0, "temp_opt_max": 34.0, "temp_heat_stress": 38.0, "temp_cold_stress": 18.0,
                "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 85,
                "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 30.0,
                "soil_moisture_pref": "Wapsa (optimal moisture condition)",
                "stage_key_risks": "Heavy rain immediately after sowing creates soil crusting in black cotton soil, trapping germinating shoots."
            },
            "germination": {
                "kc": 0.60,
                "temp_opt_min": 24.0, "temp_opt_max": 35.0, "temp_heat_stress": 39.0, "temp_cold_stress": 18.0,
                "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 82,
                "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0,
                "soil_moisture_pref": "Well drained, moist",
                "stage_key_risks": "Waterlogging for >24 hours suffocates emerging seedlings and induces Pythium/Rhizoctonia collar rot."
            },
            "seedling": {
                "kc": 0.70,
                "temp_opt_min": 24.0, "temp_opt_max": 35.0, "temp_heat_stress": 38.0, "temp_cold_stress": 17.0,
                "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 2,
                "humidity_disease_risk_min": 80,
                "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0,
                "soil_moisture_pref": "Moist, zero standing water",
                "stage_key_risks": "Water stagnation causes leaf chlorosis and root hypoxia; dry spells favor early thrips infestation."
            },
            "vegetative": {
                "kc": 0.85,
                "temp_opt_min": 25.0, "temp_opt_max": 35.0, "temp_heat_stress": 38.0, "temp_cold_stress": 18.0,
                "rain_critical_daily_mm": 40.0, "rain_waterlogging_tolerance_days": 2,
                "humidity_disease_risk_min": 78,
                "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 35.0,
                "soil_moisture_pref": "Adequate root-zone moisture",
                "stage_key_risks": "Humid overcast conditions trigger bacterial blight (Xanthomonas malvacearum) and grey mildew."
            },
            "flowering": {
                "kc": 1.15,
                "temp_opt_min": 25.0, "temp_opt_max": 34.0, "temp_heat_stress": 36.0, "temp_cold_stress": 19.0,
                "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 80,
                "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 28.0,
                "soil_moisture_pref": "Consistent moisture, well aerated",
                "stage_key_risks": "High sensitivity: waterlogging or sudden moisture stress causes massive square and flower bud shed."
            },
            "fruiting": {
                "kc": 1.20,
                "temp_opt_min": 26.0, "temp_opt_max": 35.0, "temp_heat_stress": 37.0, "temp_cold_stress": 19.0,
                "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 2,
                "humidity_disease_risk_min": 80,
                "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0,
                "soil_moisture_pref": "Moist, aerated",
                "stage_key_risks": "Warm humid conditions (>80% RH) accelerate boll rot complexes (Phomopsis, Fusarium, Colletotrichum)."
            },
            "grain_filling": {
                "kc": 1.05,
                "temp_opt_min": 24.0, "temp_opt_max": 35.0, "temp_heat_stress": 38.0, "temp_cold_stress": 17.0,
                "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 2,
                "humidity_disease_risk_min": 78,
                "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 32.0,
                "soil_moisture_pref": "Moderate moisture",
                "stage_key_risks": "Moisture deficit reduces fiber elongation; excess moisture causes boll shed."
            },
            "maturity": {
                "kc": 0.80,
                "temp_opt_min": 22.0, "temp_opt_max": 35.0, "temp_heat_stress": 39.0, "temp_cold_stress": 15.0,
                "rain_critical_daily_mm": 5.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 75,
                "wind_spraying_max_kmh": 18.0, "wind_lodging_risk_kmh": 25.0,
                "soil_moisture_pref": "Dry soil condition",
                "stage_key_risks": "Rain on bursting bolls permanently stains lint, lowers ginning out-turn, and degrades fiber tensile strength."
            },
            "harvest": {
                "kc": 0.60,
                "temp_opt_min": 20.0, "temp_opt_max": 36.0, "temp_heat_stress": 40.0, "temp_cold_stress": 14.0,
                "rain_critical_daily_mm": 2.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 70,
                "wind_spraying_max_kmh": 20.0, "wind_lodging_risk_kmh": 25.0,
                "soil_moisture_pref": "Dry field conditions",
                "stage_key_risks": "Picking must be done only when bolls are fully dry; picking damp cotton promotes fungal rot in storage."
            },
            "post_harvest": {
                "kc": 0.40,
                "temp_opt_min": 20.0, "temp_opt_max": 38.0, "temp_heat_stress": 42.0, "temp_cold_stress": 12.0,
                "rain_critical_daily_mm": 2.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 65,
                "wind_spraying_max_kmh": 22.0, "wind_lodging_risk_kmh": 35.0,
                "soil_moisture_pref": "Dry storage yard",
                "stage_key_risks": "Moisture ingress in storage causes spontaneous heating and seed discoloration."
            }
        }
    },

    "chilli": {
        "scientific_name": "Capsicum annuum",
        "reference_source": "ICAR-Indian Institute of Spices Research (IISR) & ANGRAU Guntur Chilli Research Station",
        "stages": {
            "land_preparation": {
                "kc": 0.45,
                "temp_opt_min": 20.0, "temp_opt_max": 34.0, "temp_heat_stress": 38.0, "temp_cold_stress": 16.0,
                "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 2,
                "humidity_disease_risk_min": 85,
                "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 35.0,
                "soil_moisture_pref": "Friable, deep tillage",
                "stage_key_risks": "Heavy rain delays ridge and furrow formation."
            },
            "sowing": {
                "kc": 0.50,
                "temp_opt_min": 22.0, "temp_opt_max": 32.0, "temp_heat_stress": 36.0, "temp_cold_stress": 18.0,
                "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 85,
                "wind_spraying_max_kmh": 12.0, "wind_lodging_risk_kmh": 30.0,
                "soil_moisture_pref": "Finely pulverized, moist",
                "stage_key_risks": "Small chilli seeds wash away or rot under heavy rain; damping-off risk high in waterlogged nursery."
            },
            "germination": {
                "kc": 0.55,
                "temp_opt_min": 22.0, "temp_opt_max": 32.0, "temp_heat_stress": 36.0, "temp_cold_stress": 18.0,
                "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 85,
                "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 30.0,
                "soil_moisture_pref": "Moist, raised nursery bed",
                "stage_key_risks": "High humidity + saturated beds trigger Pythium aphanidermatum damping-off in 24 hours."
            },
            "seedling": {
                "kc": 0.65,
                "temp_opt_min": 22.0, "temp_opt_max": 33.0, "temp_heat_stress": 36.0, "temp_cold_stress": 16.0,
                "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 80,
                "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0,
                "soil_moisture_pref": "Raised bed, excellent drainage",
                "stage_key_risks": "Transplanting in heavy rain causes transplanting shock and root mortality."
            },
            "vegetative": {
                "kc": 0.85,
                "temp_opt_min": 22.0, "temp_opt_max": 34.0, "temp_heat_stress": 37.0, "temp_cold_stress": 16.0,
                "rain_critical_daily_mm": 35.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 78,
                "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0,
                "soil_moisture_pref": "Moist root zone, zero ponding",
                "stage_key_risks": "Continuous humidity triggers Cercospora leaf spot; dry warm weather with wind triggers thrips and yellow mite buildup."
            },
            "flowering": {
                "kc": 1.05,
                "temp_opt_min": 22.0, "temp_opt_max": 32.0, "temp_heat_stress": 35.0, "temp_cold_stress": 15.0,
                "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 80,
                "wind_spraying_max_kmh": 12.0, "wind_lodging_risk_kmh": 25.0,
                "soil_moisture_pref": "Moderate, regular irrigation",
                "stage_key_risks": "Temperatures >35°C or <15°C induce severe blossom drop and poor fruit set; heavy rain washes flowers."
            },
            "fruiting": {
                "kc": 1.15,
                "temp_opt_min": 22.0, "temp_opt_max": 33.0, "temp_heat_stress": 36.0, "temp_cold_stress": 15.0,
                "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 80,
                "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 28.0,
                "soil_moisture_pref": "Consistent moisture",
                "stage_key_risks": "Warm humid conditions (>80% RH) accelerate anthracnose (fruit rot / die-back caused by Colletotrichum capsici)."
            },
            "grain_filling": {
                "kc": 1.00,
                "temp_opt_min": 22.0, "temp_opt_max": 34.0, "temp_heat_stress": 37.0, "temp_cold_stress": 15.0,
                "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 78,
                "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 28.0,
                "soil_moisture_pref": "Controlled moisture",
                "stage_key_risks": "Water fluctuations cause fruit cracking and blossom end rot."
            },
            "maturity": {
                "kc": 0.85,
                "temp_opt_min": 20.0, "temp_opt_max": 35.0, "temp_heat_stress": 38.0, "temp_cold_stress": 14.0,
                "rain_critical_daily_mm": 8.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 75,
                "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 25.0,
                "soil_moisture_pref": "Drier soil profile",
                "stage_key_risks": "Rain on ripening red chillies causes pod discoloration, mold growth, and loss of pungent capsaicin quality."
            },
            "harvest": {
                "kc": 0.65,
                "temp_opt_min": 20.0, "temp_opt_max": 36.0, "temp_heat_stress": 39.0, "temp_cold_stress": 14.0,
                "rain_critical_daily_mm": 2.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 70,
                "wind_spraying_max_kmh": 18.0, "wind_lodging_risk_kmh": 25.0,
                "soil_moisture_pref": "Dry field",
                "stage_key_risks": "Harvesting must halt under damp/rainy weather; wet picking causes immediate fungal rot of harvested pods."
            },
            "post_harvest": {
                "kc": 0.40,
                "temp_opt_min": 22.0, "temp_opt_max": 38.0, "temp_heat_stress": 42.0, "temp_cold_stress": 12.0,
                "rain_critical_daily_mm": 1.0, "rain_waterlogging_tolerance_days": 1,
                "humidity_disease_risk_min": 65,
                "wind_spraying_max_kmh": 20.0, "wind_lodging_risk_kmh": 35.0,
                "soil_moisture_pref": "Concrete drying yard / tarpaulin",
                "stage_key_risks": "Sun drying of red chillies critically demands 100% rainless skies; sudden showers ruin commercial export grade."
            }
        }
    },

    "maize": {
        "scientific_name": "Zea mays",
        "reference_source": "ICAR-Indian Institute of Maize Research (IIMR) & PAU Guidance",
        "stages": {
            "land_preparation": { "kc": 0.50, "temp_opt_min": 18.0, "temp_opt_max": 34.0, "temp_heat_stress": 38.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 35.0, "rain_waterlogging_tolerance_days": 3, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 18.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Well drained", "stage_key_risks": "Excess moisture prevents fine seedbed preparation." },
            "sowing": { "kc": 0.55, "temp_opt_min": 20.0, "temp_opt_max": 32.0, "temp_heat_stress": 36.0, "temp_cold_stress": 14.0, "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Adequate moisture", "stage_key_risks": "Standing water causes seed decay and fungal rotting." },
            "germination": { "kc": 0.60, "temp_opt_min": 21.0, "temp_opt_max": 33.0, "temp_heat_stress": 37.0, "temp_cold_stress": 14.0, "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 82, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist, aerated", "stage_key_risks": "Oxygen depletion in saturated soil kills sprouting radicles." },
            "seedling": { "kc": 0.70, "temp_opt_min": 22.0, "temp_opt_max": 34.0, "temp_heat_stress": 37.0, "temp_cold_stress": 13.0, "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Well drained", "stage_key_risks": "Stagnant water causes chlorosis; dry spells trigger fall armyworm invasion." },
            "vegetative": { "kc": 0.90, "temp_opt_min": 22.0, "temp_opt_max": 35.0, "temp_heat_stress": 38.0, "temp_cold_stress": 14.0, "rain_critical_daily_mm": 45.0, "rain_waterlogging_tolerance_days": 3, "humidity_disease_risk_min": 78, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Well watered", "stage_key_risks": "High humidity favors maydis leaf blight and banded leaf and sheath blight." },
            "flowering": { "kc": 1.20, "temp_opt_min": 22.0, "temp_opt_max": 32.0, "temp_heat_stress": 35.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 12.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Critical water requirement (no stress)", "stage_key_risks": "Tasseling/Silking is most sensitive: temperatures >35°C or hot dry winds desiccate silks and kill pollen viability." },
            "fruiting": { "kc": 1.15, "temp_opt_min": 22.0, "temp_opt_max": 34.0, "temp_heat_stress": 37.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Adequate moisture", "stage_key_risks": "Strong winds (>28 km/h) cause severe root and stalk lodging." },
            "grain_filling": { "kc": 1.10, "temp_opt_min": 22.0, "temp_opt_max": 34.0, "temp_heat_stress": 36.0, "temp_cold_stress": 14.0, "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 3, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Moist soil", "stage_key_risks": "Water stress leads to poor cob filling and light test weight." },
            "maturity": { "kc": 0.85, "temp_opt_min": 20.0, "temp_opt_max": 35.0, "temp_heat_stress": 38.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 10.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 75, "wind_spraying_max_kmh": 18.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Drying field", "stage_key_risks": "Rain promotes ear rot (Fusarium/Aspergillus) and kernel sprouting." },
            "harvest": { "kc": 0.60, "temp_opt_min": 18.0, "temp_opt_max": 36.0, "temp_heat_stress": 40.0, "temp_cold_stress": 10.0, "rain_critical_daily_mm": 3.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 70, "wind_spraying_max_kmh": 20.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Dry soil", "stage_key_risks": "Requires clear weather for mechanical cob plucking and field movement." },
            "post_harvest": { "kc": 0.40, "temp_opt_min": 18.0, "temp_opt_max": 38.0, "temp_heat_stress": 42.0, "temp_cold_stress": 10.0, "rain_critical_daily_mm": 2.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 65, "wind_spraying_max_kmh": 22.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Dry yard", "stage_key_risks": "Grain moisture must be brought down below 12% to prevent aflatoxin contamination." }
        }
    },

    "groundnut": {
        "scientific_name": "Arachis hypogaea",
        "reference_source": "ICAR-Directorate of Groundnut Research (DGR) & ANGRAU Oilseeds",
        "stages": {
            "land_preparation": { "kc": 0.45, "temp_opt_min": 20.0, "temp_opt_max": 34.0, "temp_heat_stress": 38.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 3, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Deep, loose, friable", "stage_key_risks": "Soil must be pulverized for easy gynophore peg penetration later." },
            "sowing": { "kc": 0.50, "temp_opt_min": 22.0, "temp_opt_max": 32.0, "temp_heat_stress": 36.0, "temp_cold_stress": 18.0, "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist, well drained", "stage_key_risks": "Excess rain rots seed kernels and induces collar rot (Aspergillus niger)." },
            "germination": { "kc": 0.55, "temp_opt_min": 22.0, "temp_opt_max": 33.0, "temp_heat_stress": 36.0, "temp_cold_stress": 18.0, "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 82, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist, loose", "stage_key_risks": "Waterlogging for 24 hours destroys germinating radicles." },
            "seedling": { "kc": 0.65, "temp_opt_min": 22.0, "temp_opt_max": 34.0, "temp_heat_stress": 37.0, "temp_cold_stress": 16.0, "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist", "stage_key_risks": "Dry spells favor leaf miner and thrips (vector of PBND)." },
            "vegetative": { "kc": 0.80, "temp_opt_min": 24.0, "temp_opt_max": 34.0, "temp_heat_stress": 38.0, "temp_cold_stress": 16.0, "rain_critical_daily_mm": 40.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 78, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Adequate moisture", "stage_key_risks": "Warm humid conditions favor early and late tikka leaf spot (Cercospora) and rust." },
            "flowering": { "kc": 1.05, "temp_opt_min": 24.0, "temp_opt_max": 32.0, "temp_heat_stress": 35.0, "temp_cold_stress": 18.0, "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 12.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Moist soil (critical for peg entry)", "stage_key_risks": "Dry hard surface soil arrests peg penetration into the ground; heat >35°C lowers pollen fertility." },
            "fruiting": { "kc": 1.15, "temp_opt_min": 24.0, "temp_opt_max": 33.0, "temp_heat_stress": 36.0, "temp_cold_stress": 17.0, "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Adequate moisture in pod zone", "stage_key_risks": "Waterlogging in pod zone causes pod rotting (Sclerotium rolfsii stem rot)." },
            "grain_filling": { "kc": 1.00, "temp_opt_min": 22.0, "temp_opt_max": 33.0, "temp_heat_stress": 36.0, "temp_cold_stress": 16.0, "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 78, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moderate moisture", "stage_key_risks": "Terminal drought results in ill-filled pops (empty pods)." },
            "maturity": { "kc": 0.75, "temp_opt_min": 20.0, "temp_opt_max": 34.0, "temp_heat_stress": 38.0, "temp_cold_stress": 14.0, "rain_critical_daily_mm": 10.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 75, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Slightly dry surface", "stage_key_risks": "Rain at maturity induces viviparous seed dormancy breakdown and in-situ sprouting in Spanish bunch types." },
            "harvest": { "kc": 0.55, "temp_opt_min": 18.0, "temp_opt_max": 36.0, "temp_heat_stress": 40.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 2.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 70, "wind_spraying_max_kmh": 18.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Moderate soil moisture for pulling", "stage_key_risks": "Harvesting in bone-dry soil breaks pods in the ground; rain after pod lifting causes Aspergillus flavus aflatoxin." },
            "post_harvest": { "kc": 0.35, "temp_opt_min": 20.0, "temp_opt_max": 38.0, "temp_heat_stress": 42.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 1.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 65, "wind_spraying_max_kmh": 20.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Dry drying floor", "stage_key_risks": "Pod drying demands bright sun to reduce moisture from 40% to <8% for safe storage." }
        }
    },

    "sugarcane": {
        "scientific_name": "Saccharum officinarum",
        "reference_source": "ICAR-Sugarcane Breeding Institute (SBI), Coimbatore",
        "stages": {
            "land_preparation": { "kc": 0.50, "temp_opt_min": 20.0, "temp_opt_max": 35.0, "temp_heat_stress": 40.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 40.0, "rain_waterlogging_tolerance_days": 5, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 18.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Deep furrowing", "stage_key_risks": "Heavy rain floods deep furrows and delays sett planting." },
            "sowing": { "kc": 0.55, "temp_opt_min": 24.0, "temp_opt_max": 35.0, "temp_heat_stress": 38.0, "temp_cold_stress": 18.0, "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 3, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist furrows", "stage_key_risks": "Waterlogged furrows rot sett buds (sett rot / Ceratocystis paradoxa)." },
            "germination": { "kc": 0.60, "temp_opt_min": 25.0, "temp_opt_max": 35.0, "temp_heat_stress": 39.0, "temp_cold_stress": 18.0, "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 3, "humidity_disease_risk_min": 82, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist, aerated", "stage_key_risks": "Temperatures below 18°C severely delay sett eye germination." },
            "seedling": { "kc": 0.70, "temp_opt_min": 25.0, "temp_opt_max": 36.0, "temp_heat_stress": 39.0, "temp_cold_stress": 16.0, "rain_critical_daily_mm": 35.0, "rain_waterlogging_tolerance_days": 3, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Adequate moisture", "stage_key_risks": "Early shoot borer (Chilo infuscatellus) attack surges during dry hot spells (>35°C)." },
            "vegetative": { "kc": 1.05, "temp_opt_min": 26.0, "temp_opt_max": 36.0, "temp_heat_stress": 40.0, "temp_cold_stress": 16.0, "rain_critical_daily_mm": 60.0, "rain_waterlogging_tolerance_days": 7, "humidity_disease_risk_min": 78, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 38.0, "soil_moisture_pref": "High water demand", "stage_key_risks": "Grand growth stage: requires abundant moisture; high humidity with rain fosters red rot and smut." },
            "flowering": { "kc": 1.25, "temp_opt_min": 24.0, "temp_opt_max": 34.0, "temp_heat_stress": 38.0, "temp_cold_stress": 16.0, "rain_critical_daily_mm": 40.0, "rain_waterlogging_tolerance_days": 5, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Moist soil", "stage_key_risks": "Arrowing (flowering) is undesired in commercial cane; lodging risk increases due to tall heavy stalks." },
            "fruiting": { "kc": 1.15, "temp_opt_min": 24.0, "temp_opt_max": 35.0, "temp_heat_stress": 38.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 40.0, "rain_waterlogging_tolerance_days": 5, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Moist", "stage_key_risks": "High winds cause severe stalk snap and lodging in propping-neglected fields." },
            "grain_filling": { "kc": 1.05, "temp_opt_min": 22.0, "temp_opt_max": 35.0, "temp_heat_stress": 38.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 35.0, "rain_waterlogging_tolerance_days": 5, "humidity_disease_risk_min": 78, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moderate moisture", "stage_key_risks": "Internode elongation and sucrose synthesis require warm days and mild nights." },
            "maturity": { "kc": 0.85, "temp_opt_min": 18.0, "temp_opt_max": 32.0, "temp_heat_stress": 38.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 3, "humidity_disease_risk_min": 75, "wind_spraying_max_kmh": 18.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Dry period before harvest (stop irrigation 15-20 days prior)", "stage_key_risks": "Rain at maturity reduces juice brix and recovery percentage by inverting sucrose into glucose." },
            "harvest": { "kc": 0.65, "temp_opt_min": 16.0, "temp_opt_max": 35.0, "temp_heat_stress": 39.0, "temp_cold_stress": 10.0, "rain_critical_daily_mm": 5.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 70, "wind_spraying_max_kmh": 20.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Dry soil for transport", "stage_key_risks": "Muddy fields prevent tractor/truck cane transport to crushing mills; post-cut cane must reach mill in 24h." },
            "post_harvest": { "kc": 0.50, "temp_opt_min": 18.0, "temp_opt_max": 36.0, "temp_heat_stress": 40.0, "temp_cold_stress": 10.0, "rain_critical_daily_mm": 5.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 65, "wind_spraying_max_kmh": 22.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Ratoon stubble management", "stage_key_risks": "Ratoon stubble shaving requires dry sunny weather to prevent fungal rotting of stool buds." }
        }
    },

    "turmeric": {
        "scientific_name": "Curcuma longa",
        "reference_source": "ICAR-IISR & Tamil Nadu Agricultural University (TNAU)",
        "stages": {
            "land_preparation": { "kc": 0.50, "temp_opt_min": 20.0, "temp_opt_max": 34.0, "temp_heat_stress": 38.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 35.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Raised broad beds, loose soil", "stage_key_risks": "Excess soil wetness impedes broad bed and furrow preparation." },
            "sowing": { "kc": 0.55, "temp_opt_min": 24.0, "temp_opt_max": 34.0, "temp_heat_stress": 38.0, "temp_cold_stress": 18.0, "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist, loose bed", "stage_key_risks": "Heavy rain causes seed rhizome rotting before sprout establishment." },
            "germination": { "kc": 0.60, "temp_opt_min": 25.0, "temp_opt_max": 34.0, "temp_heat_stress": 38.0, "temp_cold_stress": 18.0, "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 82, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist under mulch", "stage_key_risks": "Rhizomes rot rapidly under stagnant water (Pythium soft rot)." },
            "seedling": { "kc": 0.70, "temp_opt_min": 24.0, "temp_opt_max": 35.0, "temp_heat_stress": 38.0, "temp_cold_stress": 17.0, "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Good drainage", "stage_key_risks": "Leaf spot (Colletotrichum) and leaf blotch (Taphrina) surface in rainy spells." },
            "vegetative": { "kc": 0.95, "temp_opt_min": 25.0, "temp_opt_max": 35.0, "temp_heat_stress": 38.0, "temp_cold_stress": 17.0, "rain_critical_daily_mm": 45.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 32.0, "soil_moisture_pref": "Abundant moisture with zero ponding", "stage_key_risks": "Water stagnation during active tiller emergence induces rhizome rot (soft rot)." },
            "flowering": { "kc": 1.10, "temp_opt_min": 24.0, "temp_opt_max": 34.0, "temp_heat_stress": 37.0, "temp_cold_stress": 17.0, "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Moist", "stage_key_risks": "Continuous rainfall encourages shoot borer (Conogethes punctiferalis) activity." },
            "fruiting": { "kc": 1.15, "temp_opt_min": 24.0, "temp_opt_max": 34.0, "temp_heat_stress": 37.0, "temp_cold_stress": 16.0, "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Moist soil (rhizome enlargement phase)", "stage_key_risks": "Rhizome swelling demands aerated moist soil; waterlogging causes massive crop collapse." },
            "grain_filling": { "kc": 1.05, "temp_opt_min": 22.0, "temp_opt_max": 33.0, "temp_heat_stress": 36.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 78, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moderate moisture", "stage_key_risks": "Curcumin synthesis proceeds best with cooling nights (18-22°C)." },
            "maturity": { "kc": 0.80, "temp_opt_min": 20.0, "temp_opt_max": 34.0, "temp_heat_stress": 37.0, "temp_cold_stress": 14.0, "rain_critical_daily_mm": 10.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 75, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Drying field (withhold irrigation)", "stage_key_risks": "Leaves turn dry and yellow; soil must dry out for digging." },
            "harvest": { "kc": 0.60, "temp_opt_min": 18.0, "temp_opt_max": 35.0, "temp_heat_stress": 39.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 3.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 70, "wind_spraying_max_kmh": 18.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Dry soil", "stage_key_risks": "Harvesting in wet soil causes rhizome skin peeling and high soil adherence." },
            "post_harvest": { "kc": 0.35, "temp_opt_min": 20.0, "temp_opt_max": 38.0, "temp_heat_stress": 42.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 1.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 65, "wind_spraying_max_kmh": 20.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Curing and boiling floor", "stage_key_risks": "Sun-drying of boiled turmeric fingers demands 10-15 continuous days of rainless weather." }
        }
    },

    "pulses": {
        "scientific_name": "Legumes (Cajanus / Vigna)",
        "reference_source": "ICAR-Indian Institute of Pulses Research (IIPR), Kanpur",
        "stages": {
            "land_preparation": { "kc": 0.45, "temp_opt_min": 20.0, "temp_opt_max": 34.0, "temp_heat_stress": 38.0, "temp_cold_stress": 14.0, "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Well drained", "stage_key_risks": "Heavy rain delays ridge planting essential for pulse drainage." },
            "sowing": { "kc": 0.50, "temp_opt_min": 22.0, "temp_opt_max": 32.0, "temp_heat_stress": 36.0, "temp_cold_stress": 16.0, "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist (not soaked)", "stage_key_risks": "Pulse seed coats easily burst and decompose in waterlogged seedbeds." },
            "germination": { "kc": 0.55, "temp_opt_min": 22.0, "temp_opt_max": 33.0, "temp_heat_stress": 36.0, "temp_cold_stress": 16.0, "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 82, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist, aerated", "stage_key_risks": "Root hypoxia within 24 hours induces collar rot (Rhizoctonia/Sclerotium)." },
            "seedling": { "kc": 0.65, "temp_opt_min": 22.0, "temp_opt_max": 34.0, "temp_heat_stress": 37.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Well drained", "stage_key_risks": "Water stagnation causes root nodule decay and nitrogen starvation." },
            "vegetative": { "kc": 0.85, "temp_opt_min": 24.0, "temp_opt_max": 35.0, "temp_heat_stress": 38.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 35.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 78, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 32.0, "soil_moisture_pref": "Moderate moisture", "stage_key_risks": "Cloudy humid weather triggers phytophthora blight and sterility mosaic." },
            "flowering": { "kc": 1.10, "temp_opt_min": 22.0, "temp_opt_max": 32.0, "temp_heat_stress": 35.0, "temp_cold_stress": 16.0, "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 12.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Critical moisture, zero ponding", "stage_key_risks": "Flowering is extremely sensitive: rain washes flowers; heat >35°C causes severe flower drop; humidity attracts Maruca pod borer." },
            "fruiting": { "kc": 1.15, "temp_opt_min": 22.0, "temp_opt_max": 33.0, "temp_heat_stress": 36.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Moderate moisture", "stage_key_risks": "Pod borer (Helicoverpa) proliferation favored under cloudy humid spells." },
            "grain_filling": { "kc": 1.00, "temp_opt_min": 22.0, "temp_opt_max": 33.0, "temp_heat_stress": 36.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 78, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Moderate moisture", "stage_key_risks": "Powdery mildew builds up rapidly when days are warm and nights are humid." },
            "maturity": { "kc": 0.75, "temp_opt_min": 20.0, "temp_opt_max": 34.0, "temp_heat_stress": 38.0, "temp_cold_stress": 13.0, "rain_critical_daily_mm": 8.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 75, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Dry field", "stage_key_risks": "Rain on mature dry pods causes pod shattering and viviparous germination." },
            "harvest": { "kc": 0.55, "temp_opt_min": 18.0, "temp_opt_max": 36.0, "temp_heat_stress": 40.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 2.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 70, "wind_spraying_max_kmh": 18.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Dry field", "stage_key_risks": "Requires clear sunshine; damp harvested pods decay rapidly." },
            "post_harvest": { "kc": 0.35, "temp_opt_min": 18.0, "temp_opt_max": 38.0, "temp_heat_stress": 42.0, "temp_cold_stress": 10.0, "rain_critical_daily_mm": 1.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 65, "wind_spraying_max_kmh": 20.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Dry threshing floor", "stage_key_risks": "Dry grains to <9% moisture to prevent bruchid beetle infestation in storage." }
        }
    },

    "vegetables": {
        "scientific_name": "Horticultural Crops",
        "reference_source": "ICAR-Indian Institute of Vegetable Research (IIVR), Varanasi",
        "stages": {
            "land_preparation": { "kc": 0.45, "temp_opt_min": 18.0, "temp_opt_max": 32.0, "temp_heat_stress": 36.0, "temp_cold_stress": 14.0, "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Raised beds", "stage_key_risks": "Drainage channels must be prepared before transplanting." },
            "sowing": { "kc": 0.50, "temp_opt_min": 20.0, "temp_opt_max": 30.0, "temp_heat_stress": 35.0, "temp_cold_stress": 16.0, "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist nursery media", "stage_key_risks": "Small seeds wash out in intense rain." },
            "germination": { "kc": 0.55, "temp_opt_min": 20.0, "temp_opt_max": 30.0, "temp_heat_stress": 35.0, "temp_cold_stress": 16.0, "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 82, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist, aerated", "stage_key_risks": "Damping-off risk very high under warm damp conditions." },
            "seedling": { "kc": 0.65, "temp_opt_min": 20.0, "temp_opt_max": 32.0, "temp_heat_stress": 35.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist", "stage_key_risks": "Transplant shock elevated if daytime temp >34°C." },
            "vegetative": { "kc": 0.85, "temp_opt_min": 20.0, "temp_opt_max": 32.0, "temp_heat_stress": 36.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 78, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Consistent moisture", "stage_key_risks": "Foliar blights develop under overcast humid days." },
            "flowering": { "kc": 1.05, "temp_opt_min": 20.0, "temp_opt_max": 30.0, "temp_heat_stress": 34.0, "temp_cold_stress": 14.0, "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 12.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Regular micro-irrigation", "stage_key_risks": "Blossom drop occurs if temp >34°C or during rain storms." },
            "fruiting": { "kc": 1.15, "temp_opt_min": 20.0, "temp_opt_max": 32.0, "temp_heat_stress": 35.0, "temp_cold_stress": 14.0, "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Uniform moisture", "stage_key_risks": "Moisture stress alternating with rain causes fruit cracking." },
            "grain_filling": { "kc": 1.05, "temp_opt_min": 20.0, "temp_opt_max": 32.0, "temp_heat_stress": 35.0, "temp_cold_stress": 14.0, "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 78, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Moderate", "stage_key_risks": "Fruit enlargement phase." },
            "maturity": { "kc": 0.85, "temp_opt_min": 18.0, "temp_opt_max": 33.0, "temp_heat_stress": 36.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 10.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 75, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Controlled moisture", "stage_key_risks": "Rain on ripe vegetables causes rot and fruit borer damage." },
            "harvest": { "kc": 0.65, "temp_opt_min": 16.0, "temp_opt_max": 34.0, "temp_heat_stress": 37.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 2.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 70, "wind_spraying_max_kmh": 18.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Dry field conditions", "stage_key_risks": "Pick produce when morning dew has dried; wet vegetables rot in transit." },
            "post_harvest": { "kc": 0.40, "temp_opt_min": 15.0, "temp_opt_max": 35.0, "temp_heat_stress": 38.0, "temp_cold_stress": 10.0, "rain_critical_daily_mm": 1.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 65, "wind_spraying_max_kmh": 20.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Shaded sorting area", "stage_key_risks": "Keep harvested produce in shade; direct sun causes weight loss and wilting." }
        }
    },

    "tomato": {
        "scientific_name": "Solanum lycopersicum",
        "reference_source": "ICAR-IIVR Tomato Agronomy & Plant Protection Guidelines",
        "stages": {
            "land_preparation": { "kc": 0.45, "temp_opt_min": 18.0, "temp_opt_max": 32.0, "temp_heat_stress": 35.0, "temp_cold_stress": 14.0, "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Raised beds with drip lines", "stage_key_risks": "Tomato cannot tolerate standing water at any phase." },
            "sowing": { "kc": 0.50, "temp_opt_min": 20.0, "temp_opt_max": 30.0, "temp_heat_stress": 34.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist pro-trays / nursery", "stage_key_risks": "Damping off in heavy downpours." },
            "germination": { "kc": 0.55, "temp_opt_min": 20.0, "temp_opt_max": 30.0, "temp_heat_stress": 34.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 82, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist", "stage_key_risks": "Seedling decay in saturated media." },
            "seedling": { "kc": 0.65, "temp_opt_min": 20.0, "temp_opt_max": 32.0, "temp_heat_stress": 35.0, "temp_cold_stress": 14.0, "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Well drained", "stage_key_risks": "High temp (>35°C) scorched transplanted seedlings." },
            "vegetative": { "kc": 0.85, "temp_opt_min": 20.0, "temp_opt_max": 32.0, "temp_heat_stress": 35.0, "temp_cold_stress": 14.0, "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 78, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist, staked plants", "stage_key_risks": "Early blight (Alternaria solani) triggers when RH >80% and temps 24-28°C." },
            "flowering": { "kc": 1.10, "temp_opt_min": 20.0, "temp_opt_max": 30.0, "temp_heat_stress": 34.0, "temp_cold_stress": 13.0, "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 12.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Consistent moisture", "stage_key_risks": "Day temp >34°C or night temp >24°C impairs pollination and causes flower drop." },
            "fruiting": { "kc": 1.20, "temp_opt_min": 20.0, "temp_opt_max": 30.0, "temp_heat_stress": 34.0, "temp_cold_stress": 13.0, "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Steady soil moisture", "stage_key_risks": "Late blight (Phytophthora infestans) explodes in cool humid overcast spells; fruit borer (Helicoverpa) active." },
            "grain_filling": { "kc": 1.10, "temp_opt_min": 20.0, "temp_opt_max": 32.0, "temp_heat_stress": 35.0, "temp_cold_stress": 13.0, "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 78, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Moderate", "stage_key_risks": "Fruit sizing phase." },
            "maturity": { "kc": 0.85, "temp_opt_min": 18.0, "temp_opt_max": 32.0, "temp_heat_stress": 35.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 8.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 75, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Avoid over-irrigation", "stage_key_risks": "Rain on breaker/red fruits causes concentric and radial fruit cracking." },
            "harvest": { "kc": 0.65, "temp_opt_min": 16.0, "temp_opt_max": 34.0, "temp_heat_stress": 36.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 2.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 70, "wind_spraying_max_kmh": 18.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Dry field", "stage_key_risks": "Pick at breaker stage for long transport; harvest in dry hours." },
            "post_harvest": { "kc": 0.40, "temp_opt_min": 15.0, "temp_opt_max": 34.0, "temp_heat_stress": 36.0, "temp_cold_stress": 10.0, "rain_critical_daily_mm": 1.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 65, "wind_spraying_max_kmh": 20.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Cool packing shed", "stage_key_risks": "High temp causes rapid soft rot; cool storage (12-15°C) required." }
        }
    },

    "onion": {
        "scientific_name": "Allium cepa",
        "reference_source": "ICAR-Directorate of Onion and Garlic Research (DOGR), Rajgurunagar",
        "stages": {
            "land_preparation": { "kc": 0.45, "temp_opt_min": 15.0, "temp_opt_max": 30.0, "temp_heat_stress": 35.0, "temp_cold_stress": 10.0, "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Raised beds, fine tilth", "stage_key_risks": "Soil compaction hampers bulb development." },
            "sowing": { "kc": 0.50, "temp_opt_min": 18.0, "temp_opt_max": 28.0, "temp_heat_stress": 34.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist nursery", "stage_key_risks": "Rain crusting hinders emergence." },
            "germination": { "kc": 0.55, "temp_opt_min": 18.0, "temp_opt_max": 28.0, "temp_heat_stress": 34.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 82, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist", "stage_key_risks": "Damping off under high humidity." },
            "seedling": { "kc": 0.65, "temp_opt_min": 18.0, "temp_opt_max": 30.0, "temp_heat_stress": 35.0, "temp_cold_stress": 10.0, "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Raised bed", "stage_key_risks": "Transplant seedlings at pencil thickness; standing water causes root rot." },
            "vegetative": { "kc": 0.80, "temp_opt_min": 18.0, "temp_opt_max": 30.0, "temp_heat_stress": 35.0, "temp_cold_stress": 10.0, "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 78, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moderate moisture", "stage_key_risks": "Warm dry spells favor thrips (Thrips tabaci); cloudy humid weather induces purple blotch (Alternaria porri)." },
            "flowering": { "kc": 0.95, "temp_opt_min": 18.0, "temp_opt_max": 30.0, "temp_heat_stress": 34.0, "temp_cold_stress": 10.0, "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 12.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Moist (bolting undesirable)", "stage_key_risks": "Premature bolting happens if prolonged chill <10°C occurs." },
            "fruiting": { "kc": 1.05, "temp_opt_min": 20.0, "temp_opt_max": 32.0, "temp_heat_stress": 36.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Adequate moisture (bulb enlargement)", "stage_key_risks": "Bulb initiation requires longer day length and warm temperature (25-30°C)." },
            "grain_filling": { "kc": 0.95, "temp_opt_min": 20.0, "temp_opt_max": 32.0, "temp_heat_stress": 36.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 78, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Controlled moisture", "stage_key_risks": "Waterlogging causes basal bulb rot (Fusarium oxysporum)." },
            "maturity": { "kc": 0.75, "temp_opt_min": 20.0, "temp_opt_max": 34.0, "temp_heat_stress": 37.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 5.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 75, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Withhold irrigation 10-15 days prior", "stage_key_risks": "Rain at neck fall stage causes second growth, thick necks, and rotting." },
            "harvest": { "kc": 0.50, "temp_opt_min": 18.0, "temp_opt_max": 35.0, "temp_heat_stress": 38.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 1.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 70, "wind_spraying_max_kmh": 18.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Dry field for pulling", "stage_key_risks": "Pull bulbs when 50% tops have fallen; wet soil harvest ruins storage life." },
            "post_harvest": { "kc": 0.30, "temp_opt_min": 20.0, "temp_opt_max": 36.0, "temp_heat_stress": 40.0, "temp_cold_stress": 10.0, "rain_critical_daily_mm": 1.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 65, "wind_spraying_max_kmh": 20.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Well-ventilated curing shed", "stage_key_risks": "Field curing requires 3-5 dry sunny days under foliage cover to seal bulb necks." }
        }
    },

    "custom": {
        "scientific_name": "Agricultural Crop",
        "reference_source": "General Agrometeorological Guidelines (FAO-56 & ICAR General Agronomy)",
        "stages": {
            "land_preparation": { "kc": 0.50, "temp_opt_min": 18.0, "temp_opt_max": 34.0, "temp_heat_stress": 38.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 30.0, "rain_waterlogging_tolerance_days": 3, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Tillage tilth", "stage_key_risks": "Excessive rainfall prevents tractor operations." },
            "sowing": { "kc": 0.55, "temp_opt_min": 20.0, "temp_opt_max": 32.0, "temp_heat_stress": 36.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 18.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 85, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist seedbed", "stage_key_risks": "Rain wash-off and crusting risk." },
            "germination": { "kc": 0.60, "temp_opt_min": 20.0, "temp_opt_max": 32.0, "temp_heat_stress": 36.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 20.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 82, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Moist", "stage_key_risks": "Seedling collar rot risk." },
            "seedling": { "kc": 0.70, "temp_opt_min": 20.0, "temp_opt_max": 34.0, "temp_heat_stress": 36.0, "temp_cold_stress": 14.0, "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 30.0, "soil_moisture_pref": "Adequate", "stage_key_risks": "Transplant or root establishment." },
            "vegetative": { "kc": 0.85, "temp_opt_min": 22.0, "temp_opt_max": 34.0, "temp_heat_stress": 37.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 35.0, "rain_waterlogging_tolerance_days": 3, "humidity_disease_risk_min": 78, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 32.0, "soil_moisture_pref": "Moist", "stage_key_risks": "Rapid biomass growth; foliar disease risk in humid cloudy periods." },
            "flowering": { "kc": 1.15, "temp_opt_min": 22.0, "temp_opt_max": 32.0, "temp_heat_stress": 35.0, "temp_cold_stress": 16.0, "rain_critical_daily_mm": 15.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 12.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Adequate moisture (high sensitivity)", "stage_key_risks": "Flower drop or pollination failure under high temperatures or intense rains." },
            "fruiting": { "kc": 1.15, "temp_opt_min": 22.0, "temp_opt_max": 33.0, "temp_heat_stress": 36.0, "temp_cold_stress": 15.0, "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 80, "wind_spraying_max_kmh": 14.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Moist", "stage_key_risks": "Fruit, pod, or head sizing." },
            "grain_filling": { "kc": 1.05, "temp_opt_min": 20.0, "temp_opt_max": 33.0, "temp_heat_stress": 36.0, "temp_cold_stress": 14.0, "rain_critical_daily_mm": 25.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 78, "wind_spraying_max_kmh": 15.0, "wind_lodging_risk_kmh": 28.0, "soil_moisture_pref": "Moderate", "stage_key_risks": "Seed translocation." },
            "maturity": { "kc": 0.80, "temp_opt_min": 18.0, "temp_opt_max": 34.0, "temp_heat_stress": 37.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 10.0, "rain_waterlogging_tolerance_days": 2, "humidity_disease_risk_min": 75, "wind_spraying_max_kmh": 16.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Drying", "stage_key_risks": "Quality degradation if rain falls on mature standing crop." },
            "harvest": { "kc": 0.60, "temp_opt_min": 16.0, "temp_opt_max": 35.0, "temp_heat_stress": 38.0, "temp_cold_stress": 12.0, "rain_critical_daily_mm": 3.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 70, "wind_spraying_max_kmh": 18.0, "wind_lodging_risk_kmh": 25.0, "soil_moisture_pref": "Dry field", "stage_key_risks": "Requires clear dry skies for cutting and gathering." },
            "post_harvest": { "kc": 0.35, "temp_opt_min": 16.0, "temp_opt_max": 37.0, "temp_heat_stress": 40.0, "temp_cold_stress": 10.0, "rain_critical_daily_mm": 1.0, "rain_waterlogging_tolerance_days": 1, "humidity_disease_risk_min": 65, "wind_spraying_max_kmh": 20.0, "wind_lodging_risk_kmh": 35.0, "soil_moisture_pref": "Dry storage / curing area", "stage_key_risks": "Safe drying and storage protection." }
        }
    }
}

def resolve_crop_key(crop_input: str) -> str:
    """Matches any crop string or alias to our canonical crop key."""
    if not crop_input:
        return "rice"
    c = crop_input.strip().lower()
    if any(x in c for x in ["rice", "paddy", "వరి", "धान", "நெல்"]):
        return "rice"
    if any(x in c for x in ["cotton", "పత్తి", "कपास", "பருத்தி"]):
        return "cotton"
    if any(x in c for x in ["chilli", "chili", "pepper", "మిరప", "मिर्च", "மிளகாய்"]):
        return "chilli"
    if any(x in c for x in ["maize", "corn", "మొక్కజొన్న", "मक्का", "மக்காச்சோளம்"]):
        return "maize"
    if any(x in c for x in ["groundnut", "peanut", "వేరుశనగ", "मूंगफली", "வேர்க்கடலை"]):
        return "groundnut"
    if any(x in c for x in ["sugarcane", "చెరకు", "गन्ना", "கரும்பு"]):
        return "sugarcane"
    if any(x in c for x in ["turmeric", "పసుపు", "हल्दी", "மஞ்சள்"]):
        return "turmeric"
    if any(x in c for x in ["pulse", "dal", "gram", "పప్పు", "दाल", "பயறு"]):
        return "pulses"
    if any(x in c for x in ["tomato", "టమోటా", "टमाटर", "தக்காளி"]):
        return "tomato"
    if any(x in c for x in ["onion", "ఉల్లి", "प्याज़", "வெங்காயம்"]):
        return "onion"
    if any(x in c for x in ["veg", "కూరగాయ", "सब्जी", "காய்கறி"]):
        return "vegetables"
    return "custom"

def resolve_stage_key(stage_input: str) -> str:
    """Matches any growth stage string or alias to our canonical stage key."""
    if not stage_input:
        return "vegetative"
    s = stage_input.strip().lower().replace("-", "_").replace(" ", "_")
    valid_stages = [st["id"] for st in GROWTH_STAGES_REGISTRY]
    for st in valid_stages:
        if st in s or s in st:
            return st
    if "prep" in s or "land" in s or "plow" in s:
        return "land_preparation"
    if "sow" in s or "plant" in s or "seed" in s and "ling" not in s:
        return "sowing"
    if "germ" in s or "sprout" in s:
        return "germination"
    if "seedling" in s or "nursery" in s:
        return "seedling"
    if "veg" in s or "tiller" in s or "branch" in s or "growth" in s:
        return "vegetative"
    if "flower" in s or "anthesis" in s or "bloom" in s:
        return "flowering"
    if "fruit" in s or "boll" in s or "pod" in s:
        return "fruiting"
    if "grain" in s or "milk" in s or "fill" in s:
        return "grain_filling"
    if "matur" in s or "ripen" in s:
        return "maturity"
    if "harvest" in s or "pick" in s or "reap" in s:
        return "harvest"
    if "post" in s or "dry" in s or "cure" in s:
        return "post_harvest"
    return "vegetative"

def get_crop_threshold(crop_key: str, stage_key: str) -> Dict[str, Any]:
    """Retrieves specific stage thresholds, falling back safely to custom crop if missing."""
    crop_data = CROP_THRESHOLDS.get(crop_key) or CROP_THRESHOLDS["custom"]
    stages = crop_data.get("stages", {})
    return stages.get(stage_key) or stages.get("vegetative") or CROP_THRESHOLDS["custom"]["stages"]["vegetative"]
