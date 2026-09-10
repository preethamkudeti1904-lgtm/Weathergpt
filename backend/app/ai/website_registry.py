"""
Website Capability Registry for WeatherGPT
Authoritative directory of all real application features, routes, controls, and workflows.
Provides verified step-by-step guidance in all 8 supported Indian languages.
"""

from typing import Dict, Any, List, Optional

CAPABILITIES: Dict[str, Dict[str, Any]] = {
    "dashboard": {
        "title": "Weather Dashboard",
        "route": "/",
        "keywords": ["dashboard", "home", "main screen", "overview", "ముఖ్యాంశాలు", "डैशबोर्ड", "முகப்பு"],
        "description": "Displays current weather conditions, 24-hour hourly forecast timeline, Threat Surveillance disaster warning card, AI meteorological insights, and quick links.",
        "how_to_use": {
            "en": "Click 'Dashboard' in the left sidebar to view the main weather summary, live temperature, hourly forecast, and active threat surveillance cards.",
            "te": "ఎడమ వైపు ఉన్న 'డ్యాష్‌బోర్డ్' (Dashboard) పై క్లిక్ చేసి ప్రస్తుత వాతావరణం, గంటల వారీ సూచన మరియు విపత్తు హెచ్చరికలను చూడవచ్చు.",
            "hi": "मुख्य मौसम सारांश, वर्तमान तापमान और आपदा निगरानी देखने के लिए बाएं साइडबार में 'डैशबोर्ड' पर क्लिक करें।",
            "ta": "முக்கிய வானிலை சுருக்கம் மற்றும் எச்சரிக்கைகளைக் காண இடது பக்கப்பட்டியில் உள்ள 'Dashboard' என்பதைக் கிளிக் செய்க.",
            "kn": "ಮುಖ್ಯ ಹವಾಮಾನ ಸಾರಾಂಶ ಮತ್ತು ಎಚ್ಚರಿಕೆಗಳನ್ನು ವೀಕ್ಷಿಸಲು ಎಡ ಸೈಡ್‌ಬಾರ್‌ನಲ್ಲಿರುವ 'Dashboard' ಕ್ಲಿಕ್ ಮಾಡಿ.",
            "ml": "പ്രധാന കാലാവസ്ഥ വിവരങ്ങളും മുന്നറിയിപ്പുകളും കാണാൻ ഇടത് സൈഡ്ബാറിലെ 'Dashboard' ക്ലിക്ക് ചെയ്യുക.",
            "mr": "मुख्य हवामान सारांश आणि सक्रिय इशारे पाहण्यासाठी डाव्या साइडबारमधील 'डॅशबोर्ड' वर क्लिक करा.",
            "bn": "প্রধান আবহাওয়া সারাংশ এবং সক্রিয় সতর্কতা দেখতে বাম সাইডবারের 'ড্যাশবোর্ড'-এ ক্লিক করুন।"
        }
    },
    "current_weather": {
        "title": "Current Weather",
        "route": "/weather",
        "keywords": ["current weather", "real time", "now", "atmospheric", "ప్రస్తుత వాతావరణం", "वर्तमान मौसम", "தற்போதைய வானிலை"],
        "description": "Detailed real-time atmospheric metrics including feels-like temperature, humidity, pressure, wind velocity & direction, cloud cover, visibility, UV index, and sunrise/sunset times.",
        "how_to_use": {
            "en": "Click 'Current Weather' in the sidebar to inspect complete meteorological parameters including atmospheric pressure, humidity, UV index, and wind vectors.",
            "te": "సైడ్‌బార్‌లోని 'ప్రస్తుత వాతావరణం' పై క్లిక్ చేయడం ద్వారా తేమ, గాలి వేగం, పీడనం మరియు UV సూచికలను వివరంగా పరిశీలించవచ్చు.",
            "hi": "हवा का दबाव, आर्द्रता, यूवी इंडेक्स और हवा की दिशा जैसे विस्तृत मानकों को देखने के लिए साइडबार में 'वर्तमान मौसम' पर क्लिक करें।",
            "ta": "முழுமையான வானிலை அளவுருக்களை ஆய்வு செய்ய பக்கப்பட்டியில் உள்ள 'Current Weather' என்பதைக் கிளிக் செய்க.",
            "kn": "ಸಂಪೂರ್ಣ ಹವಾಮಾನ ನಿಯತಾಂಕಗಳನ್ನು ವೀಕ್ಷಿಸಲು ಸೈಡ್‌ಬಾರ್‌ನಲ್ಲಿರುವ 'Current Weather' ಕ್ಲಿಕ್ ಮಾಡಿ.",
            "ml": "വിശദമായ കാലാവസ്ഥാ സൂചികകൾ കാണാൻ സൈഡ്ബാറിലെ 'Current Weather' ക്ലിക്ക് ചെയ്യുക.",
            "mr": "सविस्तर हवामान घटक तपासण्यासाठी साइडबारमधील 'सध्याचे हवामान' वर क्लिक करा.",
            "bn": "সম্পূর্ণ আবহাওয়া পরামিতি পর্যবেক্ষণ করতে সাইডবারের 'বর্তমান আবহাওয়া'-তে ক্লিক করুন।"
        }
    },
    "forecast": {
        "title": "7-Day & Hourly Forecast",
        "route": "/forecast",
        "keywords": ["forecast", "7 days", "tomorrow", "weekly", "hourly", "వర్ష సూచన", "पूर्वानुमान", "வானிலை முன்னறிவிப்பு"],
        "description": "7-day meteorological outlook and 24-hour hourly projections for rain probability, temperature trends, and weather conditions.",
        "how_to_use": {
            "en": "Navigate to 'Forecast' in the sidebar to review day-by-day temperature highs/lows, rain probabilities, and hourly meteorological transitions.",
            "te": "సైడ్‌బార్‌లోని 'Forecast' (వాతావరణ సూచన) కు వెళ్లి రాబోయే 7 రోజుల ఉష్ణోగ్రతలు మరియు వర్షం పడే అవకాశాలను తెలుసుకోవచ్చు.",
            "hi": "आगामी 7 दिनों के अधिकतम/न्यूनतम तापमान और वर्षा की संभावना देखने के लिए साइडबार में 'पूर्वानुमान' (Forecast) पर जाएं।",
            "ta": "அடுத்த 7 நாட்களின் வெப்பநிலை மற்றும் மழை வாய்ப்புகளை அறிய பக்கப்பட்டியில் 'Forecast' என்பதைக் கிளிக் செய்க.",
            "kn": "ಮುಂದಿನ 7 ದಿನಗಳ ತಾಪಮಾನ ಮತ್ತು ಮಳೆಯ ಸಾಧ್ಯತೆಯನ್ನು ನೋಡಲು ಸೈಡ್‌ಬಾರ್‌ನಲ್ಲಿ 'Forecast' ಕ್ಲಿಕ್ ಮಾಡಿ.",
            "ml": "അടുത്ത 7 ദിവസത്തെ താപനിലയും മഴ സാധ്യതയും അറിയാൻ സൈഡ്ബാറിലെ 'Forecast' ക്ലിക്ക് ചെയ്യുക.",
            "mr": "पुढील 7 दिवसांचे तापमान आणि पावसाची शक्यता जाणून घेण्यासाठी साइडबारमध्ये 'पूर्वानुमान' वर जा.",
            "bn": "পরবর্তী 7 দিনের তাপমাত্রা এবং বৃষ্টির সম্ভাবনা জানতে সাইডবারের 'পূর্বাভাস'-এ যান।"
        }
    },
    "alerts": {
        "title": "Threat Surveillance & Disaster Alerts",
        "route": "/alerts",
        "keywords": ["alert", "alerts", "warning", "disaster", "sachet", "ndma", "imd", "danger", "hazard", "flood", "cyclone", "హెచ్చరికలు", "चेतावनी", "அபாய எச்சரிக்கை"],
        "description": "Real-time official disaster warnings from SACHET, NDMA, IMD, and CWC. Includes active warning cards, validity duration, hazard timeline (NOW to +7 Days), and official NDMA Dos & Don'ts safety precautions.",
        "how_to_use": {
            "en": "Click 'Alerts' in the sidebar to open the Threat Surveillance portal. Here you can inspect official NDMA/IMD warnings, check the chronological hazard timeline, and read life-saving Dos and Don'ts.",
            "te": "సైడ్‌బార్‌లోని 'Alerts' పై క్లిక్ చేసి అధికారిక NDMA/IMD హెచ్చరికలు, ప్రమాద కాలక్రమం (Hazard Timeline) మరియు పాటించవలసిన భద్రతా జాగ్రత్తలను చూడవచ్చు.",
            "hi": "आधिकारिक NDMA/IMD चेतावनियां, आपदा समयरेखा और जीवन रक्षक सावधानियां (Dos & Don'ts) देखने के लिए साइडबार में 'अलर्ट्स' पर क्लिक करें।",
            "ta": "அதிகாரப்பூர்வ NDMA/IMD எச்சரிக்கைகள் மற்றும் பாதுகாப்பு வழிமுறைகளைக் காண பக்கப்பட்டியில் உள்ள 'Alerts' என்பதைக் கிளிக் செய்க.",
            "kn": "ಅಧಿಕೃತ NDMA/IMD ಎಚ್ಚರಿಕೆಗಳು ಮತ್ತು ಸುರಕ್ಷತಾ ಮುನ್ನೆಚ್ಚರಿಕೆಗಳನ್ನು ವೀಕ್ಷಿಸಲು ಸೈಡ್‌ಬಾರ್‌ನಲ್ಲಿರುವ 'Alerts' ಕ್ಲಿಕ್ ಮಾಡಿ.",
            "ml": "ഔദ്യോഗിക NDMA/IMD മുന്നറിയിപ്പുകളും സുരക്ഷാ നിർദ്ദേശങ്ങളും കാണാൻ സൈഡ്ബാറിലെ 'Alerts' ക്ലിക്ക് ചെയ്യുക.",
            "mr": "अधिकृत सरकारी इशारे, आपत्कालीन वेळरेखा आणि सुरक्षा नियम पाहण्यासाठी साइडबारमधील 'इशारे' (Alerts) वर क्लिक करा.",
            "bn": "সরকারী NDMA/IMD সতর্কতা এবং জীবন রক্ষাকারী নির্দেশিকা দেখতে সাইডবারের 'সতর্কতা' (Alerts)-এ ক্লিক করুন।"
        }
    },
    "weather_map": {
        "title": "Interactive Weather & Hazard Map",
        "route": "/map",
        "keywords": ["map", "weather map", "radar", "satellite", "warning zone", "మ్యాప్", "नक्शा", "வரைபடம்"],
        "description": "Full-screen interactive Leaflet map displaying live temperature overlays, active disaster warning zones, pulsing alert markers, and click-to-inspect popups.",
        "how_to_use": {
            "en": "Click 'Weather Map' in the sidebar. You can pan and zoom, toggle Roadmap/Satellite views, inspect red/amber disaster warning circles, or click 'Follow My Location' to track your GPS position.",
            "te": "సైడ్‌బార్‌లోని 'Weather Map' పై క్లిక్ చేయండి. మ్యాప్‌ను జూమ్ చేసి విపత్తు హెచ్చరిక జోన్‌లు (Warning Zones) మరియు మీ లొకేషన్‌ను ప్రత్యక్షంగా పరిశీలించవచ్చు.",
            "hi": "साइडबार में 'वेदर मैप' (Weather Map) पर क्लिक करें। यहां आप नक्शे पर चक्रवात/बाढ़ के चेतावनी क्षेत्र और अपना लाइव स्थान देख सकते हैं।",
            "ta": "பக்கப்பட்டியில் 'Weather Map' என்பதைக் கிளிக் செய்து, பேரிடர் எச்சரிக்கை மண்டலங்களை வரைபடத்தில் நேரடியாகக் காணலாம்.",
            "kn": "ಸೈಡ್‌ಬಾರ್‌ನಲ್ಲಿ 'Weather Map' ಕ್ಲಿಕ್ ಮಾಡಿ ನಕ್ಷೆಯಲ್ಲಿ ಎಚ್ಚರಿಕೆ ವಲಯಗಳು ಮತ್ತು ನಿಮ್ಮ ಲೈವ್ ಜಿಪಿಎಸ್ ಸ್ಥಳವನ್ನು ವೀಕ್ಷಿಸಿ.",
            "ml": "സൈഡ്ബാറിലെ 'Weather Map' ക്ലിക്ക് ചെയ്ത് മുന്നറിയിപ്പ് മേഖലകളും ലൈവ് ജിപിഎസ് ലൊക്കേഷനും മാപ്പിൽ പരിശോധിക്കുക.",
            "mr": "आपत्ती चेतावणी क्षेत्रे आणि थेट स्थान पाहण्यासाठी साइडबारमधील 'हवामान नकाशा' वर क्लिक करा.",
            "bn": "সাইডবারের 'আবহাওয়া মানচিত্র'-এ ক্লিক করে দুর্যোগ সতর্কতা অঞ্চল এবং লাইভ অবস্থান দেখুন।"
        }
    },
    "gps_location": {
        "title": "Live GPS Location Tracking",
        "route": "top_navigation",
        "keywords": ["gps", "locate me", "current position", "my location", "coordinates", "నా లొకేషన్", "मेरा स्थान", "எனது இருப்பிடம்"],
        "description": "High-accuracy browser-based GPS positioning using navigator.geolocation with accuracy radius.",
        "how_to_use": {
            "en": "To use GPS, click the 'Locate Me' (crosshairs GPS icon) in the top search bar or on the Weather Map. Allow the browser location prompt to automatically detect your precise coordinates and district.",
            "te": "టాప్ సెర్చ్ బార్‌లో లేదా మ్యాప్‌లో ఉన్న GPS ఐకాన్ (Locate Me) పై క్లిక్ చేయండి. బ్రౌజర్ అనుమతి ఇస్తే మీ ఖచ్చితమైన అక్షాంశ, రేఖాంశాలు మరియు జిల్లా స్వయంచాలకంగా ఎంపికవుతాయి.",
            "hi": "शीर्ष सर्च बार में या नक्शे पर स्थित GPS आइकन पर क्लिक करें और ब्राउज़र लोकेशन अनुमति दें ताकि आपका सटीक जिला और मौसम तुरंत प्राप्त हो सके।",
            "ta": "மேல் தேடல் பட்டியில் உள்ள GPS ஐகானைக் கிளிக் செய்து உலாவி அனுமதியை வழங்கினால் உங்கள் நேரடி இருப்பிடம் தானாகவே கண்டறியப்படும்.",
            "kn": "ಮೇಲಿನ ಹುಡುಕಾಟ ಪಟ್ಟಿಯಲ್ಲಿರುವ GPS ಐಕಾನ್ ಕ್ಲಿಕ್ ಮಾಡಿ ನಿಮ್ಮ ಪ್ರಸ್ತುತ ಸ್ಥಳವನ್ನು ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಪತ್ತೆಹಚ್ಚಿ.",
            "ml": "മുകളിലെ തിരയൽ ബാറിലെ GPS ഐക്കണിൽ ക്ലിക്കുചെയ്ത് നിങ്ങളുടെ ലൈവ് ലൊക്കേഷൻ കണ്ടെത്തുക.",
            "mr": "शीर्ष शोध पट्टीतील GPS आयकॉनवर क्लिक करा आणि आपले अचूक थेट स्थान स्वयंचलितपणे मिळवा.",
            "bn": "শীর্ষ সার্চ বারে অবস্থিত GPS আইকনে ক্লিক করে আপনার লাইভ অবস্থান স্বয়ংক্রিয়ভাবে শনাক্ত করুন।"
        }
    },
    "change_location": {
        "title": "Search & Change Location",
        "route": "top_navigation",
        "keywords": ["change location", "search city", "switch city", "find city", "నగరం మార్చడం", "स्थान बदलना", "நகரத்தை மாற்றவும்"],
        "description": "Global search bar capable of looking up any Indian district, town, or worldwide city with instant autocomplete.",
        "how_to_use": {
            "en": "Type any city or district name (e.g. 'Guntur', 'Hyderabad', 'Tokyo') in the search bar at the very top of the page and select it from the dropdown list.",
            "te": "పేజీ పైభాగంలో ఉన్న సెర్చ్ బార్‌లో ఏదైనా నగరం లేదా జిల్లా పేరు (ఉదా. 'Guntur', 'Hyderabad') టైప్ చేసి డ్రాప్‌డౌన్ నుండి ఎంచుకోండి.",
            "hi": "पेज के शीर्ष पर सर्च बार में किसी भी शहर या जिले का नाम (उदा. 'Guntur', 'Delhi') टाइप करें और सूची से चुनें।",
            "ta": "பக்கத்தின் மேற்புறத்தில் உள்ள தேடல் பட்டியில் எந்தவொரு நகரத்தின் பெயரையும் தட்டச்சு செய்து தேர்ந்தெடுக்கவும்.",
            "kn": "ಪುಟದ ಮೇಲ್ಭಾಗದಲ್ಲಿರುವ ಹುಡುಕಾಟ ಪಟ್ಟಿಯಲ್ಲಿ ಯಾವುದೇ ನಗರದ ಹೆಸರನ್ನು ಟೈಪ್ ಮಾಡಿ ಆಯ್ಕೆಮಾಡಿ.",
            "ml": "പേജിന്റെ മുകളിലുള്ള തിരയൽ ബാറിൽ ഏതെങ്കിലും നഗരത്തിന്റെ പേര് ടൈപ്പ് ചെയ്ത് തിരഞ്ഞെടുക്കുക.",
            "mr": "पृष्ठाच्या शीर्षस्थानी असलेल्या शोध पट्टीमध्ये कोणत्याही शहराचे नाव टाइप करा आणि निवडा.",
            "bn": "পৃষ্ঠার শীর্ষে অবস্থিত অনুসন্ধান বারে যেকোনো শহরের নাম টাইপ করে তালিকা থেকে নির্বাচন করুন।"
        }
    },
    "language_selector": {
        "title": "Multilingual Language Selector",
        "route": "top_navigation",
        "keywords": ["language", "change language", "telugu", "hindi", "tamil", "bengali", "భాష మార్చడం", "भाषा बदलना", "மொழியை மாற்றவும்"],
        "description": "Immediate full-UI language switching supporting 8 Indian languages: English, Hindi, Telugu, Tamil, Kannada, Malayalam, Marathi, and Bengali.",
        "how_to_use": {
            "en": "Click the Language selector dropdown in the top right navigation bar (labeled EN, हिन्दी, తెలుగు, தமிழ், etc.) and select your preferred language. The entire website and AI will instantly translate without reloading.",
            "te": "టాప్ రైట్ నేవిగేషన్ బార్‌లో ఉన్న భాషా డ్రాప్‌డౌన్ (EN, తెలుగు, हिन्दी, ইত্যাদি) పై క్లిక్ చేసి మీ భాషను ఎంచుకోండి. వెంటనే వెబ్‌సైట్ మొత్తం ఆ భాషలోకి మారుతుంది.",
            "hi": "ऊपर दाईं ओर स्थित भाषा चयनकर्ता (EN, हिन्दी, తెలుగు आदि) पर क्लिक करें और अपनी पसंदीदा भाषा चुनें। पूरी वेबसाइट तुरंत अनुवादित हो जाएगी।",
            "ta": "மேல் வலதுபுறத்தில் உள்ள மொழி தேர்வியை (EN, தமிழ், हिन्दी) கிளிக் செய்து உங்கள் விருப்பமான மொழியைத் தேர்ந்தெடுக்கவும்.",
            "kn": "ಮೇಲಿನ ಬಲ ಮೂಲೆಯಲ್ಲಿರುವ ಭಾಷಾ ಆಯ್ಕೆಗಾರ (Language Selector) ಕ್ಲಿಕ್ ಮಾಡಿ ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆರಿಸಿ.",
            "ml": "മുകളിൽ വലതുവശത്തുള്ള ഭാഷാ സെലക്ടർ ക്ലിക്ക് ചെയ്ത് നിങ്ങളുടെ ഇഷ്ടഭാഷ തിരഞ്ഞെടുക്കുക.",
            "mr": "वरच्या उजव्या बाजूला असलेल्या भाषा निवडकावर (Language Selector) क्लिक करा आणि आपली भाषा निवडा.",
            "bn": "উপরে ডানদিকের ভাষা ড্রপডাউন (EN, বাংলা, हिन्दी)-এ ক্লিক করে আপনার পছন্দের ভাষা নির্বাচন করুন।"
        }
    },
    "dark_mode": {
        "title": "Dark / Light Mode Toggle",
        "route": "top_navigation",
        "keywords": ["dark mode", "night mode", "light mode", "theme", "థీమ్", "डार्क मोड", "இரவு முறை"],
        "description": "Toggle between sleek dark theme and crisp high-contrast light theme.",
        "how_to_use": {
            "en": "Click the Sun/Moon icon in the top right navigation bar to instantly toggle between Dark Mode and Light Mode.",
            "te": "టాప్ రైట్ నేవిగేషన్ బార్‌లోని సూర్యుడు/చంద్రుడు (Sun/Moon) ఐకాన్ పై క్లిక్ చేసి డార్క్ మోడ్ మరియు లైట్ మోడ్ మధ్య మారవచ్చు.",
            "hi": "डार्क मोड और लाइट मोड के बीच स्विच करने के लिए ऊपर दाईं ओर स्थित सूर्य/चंद्रमा आइकन पर क्लिक करें।",
            "ta": "இரவு முறைக்கும் பகல் முறைக்கும் இடையில் மாற மேல் வலதுபுறத்தில் உள்ள சூரியன்/சந்திரன் ஐகானைக் கிளிக் செய்க.",
            "kn": "ಡಾರ್ಕ್ ಮೋಡ್ ಮತ್ತು ಲೈಟ್ ಮೋಡ್ ನಡುವೆ ಬದಲಾಯಿಸಲು ಮೇಲಿನ ಬಲ ಮೂಲೆಯಲ್ಲಿರುವ ಸೂರ್ಯ/ಚಂದ್ರ ಐಕಾನ್ ಕ್ಲಿಕ್ ಮಾಡಿ.",
            "ml": "ഡാർക്ക് മോഡും ലൈറ്റ് മോഡും തമ്മിൽ മാറാൻ മുകളിൽ വലതുവശത്തുള്ള സൂര്യൻ/ചന്ദ്രൻ ഐക്കണിൽ ക്ലിക്ക് ചെയ്യുക.",
            "mr": "डार्क मोड आणि लाइट मोड बदलण्यासाठी वरच्या उजव्या बाजूला असलेल्या सूर्य/चंद्र आयकॉनवर क्लिक करा.",
            "bn": "ডার্ক মোড এবং লাইট মোডের মধ্যে পরিবর্তন করতে উপরে ডানদিকে সূর্য/চাঁদ আইকনে ক্লিক করুন।"
        }
    },
    "advisory": {
        "title": "Role-Based Meteorological Advisories",
        "route": "/advisory",
        "keywords": ["advisory", "farmer", "agriculture", "aviation", "marine", "రైతు సలహాలు", "कृषि सलाह", "விவசாய ஆலோசனை"],
        "description": "Tailored advisories for specialized roles: Farmers (sowing, spraying, irrigation), Disaster Management, Aviation (METAR, crosswinds), and Marine (coastal sea state).",
        "how_to_use": {
            "en": "Click 'Advisory' in the sidebar to access persona-tailored actionable recommendations for agriculture, disaster readiness, aviation flight visibility, or maritime safety.",
            "te": "రైతులు, విపత్తు నిర్వహణ, విమానయానం మరియు మత్స్యకారుల కోసం ప్రత్యేక వాతావరణ సలహాలను చూడటానికి సైడ్‌బార్‌లోని 'Advisory' పై క్లిక్ చేయండి.",
            "hi": "किसानों, आपदा प्रबंधन, विमानन और समुद्री सुरक्षा के लिए विशेष मौसम सलाह प्राप्त करने के लिए साइडबार में 'सलाह' (Advisory) पर क्लिक करें।",
            "ta": "விவசாயிகள், பேரிடர் மேலாண்மை மற்றும் மீனவர்களுக்கான பிரத்யேக ஆலோசனைகளைக் காண பக்கப்பட்டியில் 'Advisory' என்பதைக் கிளிக் செய்க.",
            "kn": "ರೈತರು ಮತ್ತು ವಿಪತ್ತು ನಿರ್ವಹಣೆಗಾಗಿ ಸೂಕ್ತ ಹವಾಮಾನ ಸಲಹೆಗಳನ್ನು ಪಡೆಯಲು ಸೈಡ್‌ಬಾರ್‌ನಲ್ಲಿ 'Advisory' ಕ್ಲಿಕ್ ಮಾಡಿ.",
            "ml": "കർഷകർക്കും ദുരന്തനിവാരണ വിഭാഗത്തിനും വേണ്ടിയുള്ള പ്രത്യേക നിർദ്ദേശങ്ങൾക്കായി സൈഡ്ബാറിലെ 'Advisory' ക്ലിക്ക് ചെയ്യുക.",
            "mr": "शेतकरी, आपत्ती व्यवस्थापन आणि सागरी सुरक्षिततेसाठी सानुकूलित मार्गदर्शनासाठी साइडबारमधील 'सल्ला' वर क्लिक करा.",
            "bn": "কৃষক এবং দুর্যোগ ব্যবস্থাপনার জন্য উপযোগী আবহাওয়া নির্দেশিকা দেখতে সাইডবারের 'পরামর্শ' (Advisory)-তে ক্লিক করুন।"
        }
    },
    "climate_analysis": {
        "title": "Climate Analysis & Historical Trends",
        "route": "/climate",
        "keywords": ["climate", "trends", "historical anomalies", "monsoon", "వాతావరణ విశ్లేషణ", "जलवायु विश्लेषण", "காலநிலை பகுப்பாய்வு"],
        "description": "Historical temperature anomalies, rainfall departures, seasonal monsoon diagnostics, and climate resilience indices.",
        "how_to_use": {
            "en": "Click 'Climate Analysis' in the sidebar to review seasonal monsoon trends, long-term temperature anomalies, and precipitation departures.",
            "te": "దీర్ఘకాలిక రుతుపవనాల తీరు మరియు ఉష్ణోగ్రత మార్పులను విశ్లేషించడానికి సైడ్‌బార్‌లోని 'Climate Analysis' పై క్లిక్ చేయండి.",
            "hi": "दीर्घकालिक मानसूनी रुझान और तापमान विसंगतियों की समीक्षा करने के लिए साइडबार में 'जलवायु विश्लेषण' पर क्लिक करें।",
            "ta": "நீண்ட கால பருவமழை போக்குகள் மற்றும் வெப்பநிலை மாற்றங்களை அறிய பக்கப்பட்டியில் 'Climate Analysis' என்பதைக் கிளிக் செய்க.",
            "kn": "ಋತುಮಾನದ ಮಾನ್ಸೂನ್ ಪ್ರವೃತ್ತಿಗಳನ್ನು ಪರಿಶೀಲಿಸಲು ಸೈಡ್‌ಬಾರ್‌ನಲ್ಲಿ 'Climate Analysis' ಕ್ಲಿಕ್ ಮಾಡಿ.",
            "ml": "കാലാവസ്ഥാ വ്യതിയാനങ്ങളും മൺസൂൺ പ്രവണതകളും പരിശോധിക്കാൻ സൈഡ്ബാറിലെ 'Climate Analysis' ക്ലിക്ക് ചെയ്യുക.",
            "mr": "दीर्घकालीन मान्सून कल आणि हवामान बदल तपासण्यासाठी साइडबारमधील 'हवामान विश्लेषण' वर क्लिक करा.",
            "bn": "দীর্ঘমেয়াদী মৌসুমি প্রবণতা পর্যালোচনা করতে সাইডবারের 'জলবায়ু বিশ্লেষণ'-এ ক্লিক করুন।"
        }
    },
    "saved_locations": {
        "title": "Saved Locations",
        "route": "/locations",
        "keywords": ["saved locations", "favorites", "bookmarks", "cities", "సేవ్ చేసిన స్థలాలు", "सहेजे गए स्थान", "சேமிக்கப்பட்ட இடங்கள்"],
        "description": "Manage your list of frequently monitored districts and favorite cities for one-click switching.",
        "how_to_use": {
            "en": "Click 'Locations' in the sidebar to view, add, or remove your saved cities and jump to any saved location with a single click.",
            "te": "మీరు తరచుగా చూసే నగరాలను భద్రపరచుకోవడానికి మరియు సులభంగా మార్చుకోవడానికి సైడ్‌బార్‌లోని 'Locations' పై క్లిక్ చేయండి.",
            "hi": "अपने पसंदीदा शहरों को सहेजने और एक क्लिक में उन पर स्विच करने के लिए साइडबार में 'स्थान' (Locations) पर क्लिक करें।",
            "ta": "உங்களுக்கு பிடித்த நகரங்களை சேமித்து விரைவாக மாற பக்கப்பட்டியில் 'Locations' என்பதைக் கிளிக் செய்க.",
            "kn": "ನಿಮ್ಮ ನೆಚ್ಚಿನ ನಗರಗಳನ್ನು ನಿರ್ವಹಿಸಲು ಸೈಡ್‌ಬಾರ್‌ನಲ್ಲಿ 'Locations' ಕ್ಲಿಕ್ ಮಾಡಿ.",
            "ml": "സേവ് ചെയ്ത ലൊക്കേഷനുകൾ കാണാനും മാറ്റാനും സൈഡ്ബാറിലെ 'Locations' ക്ലിക്ക് ചെയ്യുക.",
            "mr": "आपली सेव्ह केलेली शहरे व्यवस्थापित करण्यासाठी साइडबारमधील 'स्थाने' वर क्लिक करा.",
            "bn": "সংরক্ষিত শহরগুলি পরিচালনা করতে সাইডবারের 'অবস্থানসমূহ'-এ ক্লিক করুন।"
        }
    }
}

def get_website_assistance(query: str, language: str = "en") -> Optional[str]:
    """
    Match user query against real capabilities and return localized instructions.
    """
    q_lower = query.lower()
    lang = language if language in ["en", "hi", "te", "ta", "kn", "ml", "mr", "bn"] else "en"

    best_match = None
    for cap_id, cap in CAPABILITIES.items():
        if any(kw in q_lower for kw in cap["keywords"]):
            best_match = cap
            break

    if not best_match:
        # Check generic website help terms
        if any(w in q_lower for w in ["how do i", "how to use", "where is", "where can i", "website help", "ఎలా ఉపయోగించాలి", "कैन यू हेल्प", "ఎలా"]):
            # Return general navigation overview
            if lang == "te":
                return "WeatherGPT లో ముఖ్యమైన విభాగాలు: \n• డ్యాష్‌బోర్డ్: ప్రస్తుత వాతావరణం & గంటల సూచన\n• Alerts: అధికారిక NDMA/IMD విపత్తు హెచ్చరికలు\n• Weather Map: ప్రత్యక్ష నక్షా మరియు GPS లొకేషన్\n• Forecast: రాబోయే 7 రోజుల వర్ష సూచన\n• భాష మార్చుటకు టాప్ రైట్‌లోని Language సెలెక్టర్ ఉపయోగించండి."
            elif lang == "hi":
                return "WeatherGPT के मुख्य फीचर्स:\n• डैशबोर्ड: वर्तमान मौसम व प्रति घंटा पूर्वानुमान\n• अलर्ट्स: आधिकारिक NDMA/IMD आपदा चेतावनियां\n• वेदर मैप: लाइव नक्शा और जीपीएस ट्रैकिंग\n• पूर्वानुमान: आगामी 7 दिनों का मौसम\n• भाषा बदलने के लिए ऊपर दाईं ओर Language विकल्प चुनें।"
            else:
                return "WeatherGPT Key Features Overview:\n• Dashboard: Real-time observations, hourly forecast & Threat Surveillance\n• Alerts: Live official NDMA/IMD disaster warnings & safety checklists\n• Weather Map: Interactive radar & warning zone map with GPS locate\n• Forecast: 7-day extended forecast & rain probabilities\n• Top Navigation: Search any global city, toggle Dark Mode, or switch between 8 languages."

    how_to = best_match["how_to_use"].get(lang, best_match["how_to_use"]["en"])
    return f"🌐 {best_match['title']}:\n{how_to}"
