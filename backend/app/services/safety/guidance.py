from typing import List, Dict

# Official Disaster Guidance and NDMA Dos & Don'ts Knowledge Base
# Source: NDMA (National Disaster Management Authority) / SACHET (https://sachet.ndma.gov.in/DosDont)

HAZARD_SAFETY_PRECAUTIONS: Dict[str, List[str]] = {
    "flood": [
        "Avoid wading or driving through flooded roads, causeways, and underpasses.",
        "Move to higher ground or designated shelter immediately if local authorities advise evacuation.",
        "Do not touch fallen electric power lines or submerged electrical appliances.",
        "Drink only boiled or chemically treated water; avoid contaminated floodwaters.",
        "Keep an emergency kit ready with battery torches, potable water, essential medicines, and waterproof bags for documents.",
        "Follow official warnings and alerts broadcast by SDMA, IMD, and NDMA."
    ],
    "heavy rain": [
        "Stay indoors during torrential downpours unless evacuation is required.",
        "Clear drainage and downspouts around residential properties to avoid localized inundation.",
        "Avoid traveling on waterlogged highway corridors and rural culverts.",
        "Unplug non-essential electrical equipment during severe downpours.",
        "Farmers should postpone spraying pesticides and ensure field discharge channels are free of debris.",
        "Monitor local weather bulletins and traffic advisories."
    ],
    "thunderstorm": [
        "Seek substantial indoor shelter immediately upon hearing thunder or observing lightning.",
        "Avoid taking shelter under tall, isolated trees or open metal structures.",
        "Stay away from open bodies of water, swimming pools, wire fences, and metallic towers.",
        "Unplug computers, televisions, and air conditioners to guard against lightning power surges.",
        "If caught outdoors without shelter, crouch low on the balls of your feet with your head tucked; do not lie flat.",
        "Avoid using corded landline telephones during active lightning discharge."
    ],
    "lightning": [
        "Follow the 30-30 rule: If thunder sounds within 30 seconds of lightning flash, seek immediate indoor shelter.",
        "Stay indoors for at least 30 minutes after the last clap of thunder.",
        "Avoid touching plumbing pipes, metal window frames, and electrical outlets.",
        "Do not operate tractors or metal farm machinery in open fields during convective storms.",
        "If someone is struck by lightning, call emergency services immediately; lightning victims carry no electrical charge and require immediate CPR."
    ],
    "heat wave": [
        "Avoid direct exposure to solar radiation between 12:00 PM and 4:00 PM.",
        "Drink sufficient water and oral rehydration solutions (ORS, buttermilk, lemon water) even if not feeling thirsty.",
        "Wear lightweight, loose-fitting, light-colored cotton garments and use umbrellas or hats outdoors.",
        "Never leave children, senior citizens, or pets unattended in parked vehicles.",
        "Reschedule heavy outdoor manual labor to cooler morning or late evening hours.",
        "Watch for heat exhaustion signs (dizziness, nausea, headache, excessive thirst) and seek immediate medical attention."
    ],
    "cyclone": [
        "Check roof, window shutters, and doors; secure loose rooftop objects and tin sheets.",
        "Keep emergency battery lights, first-aid kits, non-perishable food, and drinking water stocked for at least 72 hours.",
        "Fishermen must heed IMD coastal warnings and strictly refrain from venturing into sea.",
        "If living in a low-lying coastal zone, evacuate promptly to designated cyclone storm shelters upon government orders.",
        "Do not step outside during the calm 'eye of the cyclone'; winds will reverse with extreme violence within minutes.",
        "Beware of damaged structures, uprooted trees, and live dangling electric cables after the storm passes."
    ],
    "strong wind": [
        "Stay away from temporary billboards, construction scaffoldings, and fragile corrugated sheet sheds.",
        "Secure outdoor furniture, trash bins, and antennas on roofs.",
        "Drive at reduced speeds and maintain a firm grip on the steering wheel, particularly on open bridges and expressways.",
        "Park vehicles away from large old trees and power transmission pylons."
    ],
    "dense fog": [
        "Use low-beam headlights and dedicated fog lights while driving; never use high beams in dense fog.",
        "Maintain a generous braking distance from vehicles ahead and follow road lane markings.",
        "Avoid overtaking, abrupt braking, or pulling over on active highway lanes without hazard lights.",
        "Pedestrians and cyclists should wear reflective clothing or carry illumination."
    ],
    "cold wave": [
        "Dress in multiple layers of warm woolen clothing rather than a single heavy garment.",
        "Protect extremities by wearing gloves, warm caps, and insulated footwear.",
        "Ensure adequate room ventilation if using charcoal embers, kerosene heaters, or room fires to prevent carbon monoxide poisoning.",
        "Provide warm shelter and adequate feed for domestic livestock and pets."
    ],
    "landslide": [
        "Stay alert for signs of slope movement such as tilted trees, cracked road surfaces, or sudden muddy water runoff.",
        "Evacuate rapidly perpendicular to the path of potential debris flow.",
        "Avoid traveling on hilly or mountain passes during and immediately following prolonged heavy precipitation.",
        "Listen to unusual sounds that might indicate moving debris, such as trees cracking or boulders knocking together."
    ],
    "tsunami": [
        "If you feel strong earth shaking near the coast or see the ocean water recede abruptly, move inland and to high ground immediately.",
        "Do not wait for an official tsunami siren if coastal waters exhibit rapid anomalous withdrawal.",
        "Stay away from beaches and coastal inlets; a tsunami is a series of powerful waves that can last for hours.",
        "Do not return to coastal zones until emergency management authorities officially announce all-clear."
    ],
    "earthquake": [
        "Drop, Cover, and Hold On: Take cover under sturdy furniture and protect your head and neck.",
        "Stay away from glass windows, exterior walls, and tall furniture that could tip over.",
        "Do not use elevators during or immediately after seismic tremors; use designated stairwells.",
        "If outdoors, move to an open area away from buildings, streetlights, and utility wires."
    ],
    "general": [
        "Stay calm and stay informed through official government disaster alert portals (NDMA, SACHET, IMD).",
        "Keep mobile phones charged and emergency contact numbers readily accessible.",
        "Assist vulnerable neighbors, including children, pregnant women, the elderly, and persons with disabilities.",
        "Follow official evacuation directives issued by District Disaster Management Authorities (DDMA)."
    ]
}

def get_safety_precautions(disaster_type: str) -> List[str]:
    """
    Returns structured official safety precautions for a given disaster category.
    """
    if not disaster_type:
        return HAZARD_SAFETY_PRECAUTIONS["general"]
    
    clean = disaster_type.strip().lower()
    
    if "flood" in clean:
        return HAZARD_SAFETY_PRECAUTIONS["flood"]
    elif "cyclone" in clean:
        return HAZARD_SAFETY_PRECAUTIONS["cyclone"]
    elif "heat" in clean or "hot" in clean:
        return HAZARD_SAFETY_PRECAUTIONS["heat wave"]
    elif "lightning" in clean:
        return HAZARD_SAFETY_PRECAUTIONS["lightning"]
    elif "thunder" in clean or "storm" in clean:
        return HAZARD_SAFETY_PRECAUTIONS["thunderstorm"]
    elif "rain" in clean or "precipitation" in clean:
        return HAZARD_SAFETY_PRECAUTIONS["heavy rain"]
    elif "wind" in clean or "squall" in clean or "gale" in clean:
        return HAZARD_SAFETY_PRECAUTIONS["strong wind"]
    elif "fog" in clean or "visibility" in clean:
        return HAZARD_SAFETY_PRECAUTIONS["dense fog"]
    elif "cold" in clean or "frost" in clean:
        return HAZARD_SAFETY_PRECAUTIONS["cold wave"]
    elif "landslide" in clean or "mudslide" in clean:
        return HAZARD_SAFETY_PRECAUTIONS["landslide"]
    elif "tsunami" in clean:
        return HAZARD_SAFETY_PRECAUTIONS["tsunami"]
    elif "quake" in clean or "earthquake" in clean:
        return HAZARD_SAFETY_PRECAUTIONS["earthquake"]
    
    return HAZARD_SAFETY_PRECAUTIONS["general"]

class SafetyGuidanceService:
    def get_precautions_for_hazard(self, disaster_type: str) -> List[str]:
        return get_safety_precautions(disaster_type)

safety_guidance = SafetyGuidanceService()
