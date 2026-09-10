import sys
import io
import urllib.request
import json
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_URL = "http://127.0.0.1:8080/api/chat"
CONV_URL = "http://127.0.0.1:8080/api/chat/conversations"

def send_chat(message, session_id=None, location_name="Guntur, Andhra Pradesh", language="en"):
    payload = {
        "message": message,
        "session_id": session_id,
        "location_name": location_name,
        "language": language
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode('utf-8'))

results = []

print("=" * 70)
print("RUNNING 15 TEST SCENARIOS FROM SECTION 35")
print("=" * 70)

# TEST 1: "Hi"
t1 = send_chat("Hi")
r1 = (t1["intent"] == "GREETING" and not t1["requires_weather_data"] and len(t1["tool_results"]) == 0)
results.append(("TEST 1: 'Hi'", r1, t1['intent'], t1['requires_weather_data'], t1['message'][:60]))

# TEST 2: "Have you ate?"
t2 = send_chat("Have you ate?")
r2 = (t2["intent"] == "CASUAL_CONVERSATION" and not t2["requires_weather_data"] and len(t2["tool_results"]) == 0 and "°C" not in t2["message"])
results.append(("TEST 2: 'Have you ate?'", r2, t2['intent'], t2['requires_weather_data'], t2['message'][:60]))

# TEST 3: "How are you?"
t3 = send_chat("How are you?")
r3 = (t3["intent"] == "CASUAL_CONVERSATION" and not t3["requires_weather_data"] and len(t3["tool_results"]) == 0 and "°C" not in t3["message"])
results.append(("TEST 3: 'How are you?'", r3, t3['intent'], t3['requires_weather_data'], t3['message'][:60]))

# TEST 4: "Tell me a joke."
t4 = send_chat("Tell me a joke.")
r4 = (not t4["requires_weather_data"] and len(t4["tool_results"]) == 0 and "°C" not in t4["message"])
results.append(("TEST 4: 'Tell me a joke.'", r4, t4['intent'], t4['requires_weather_data'], t4['message'][:60]))

# TEST 5: "What is the temperature?"
t5 = send_chat("What is the temperature?")
r5 = (t5["intent"] == "WEATHER_CURRENT" and t5["requires_weather_data"] and len(t5["tool_results"]) > 0 and "°C" in t5["message"])
results.append(("TEST 5: 'What is the temperature?'", r5, t5['intent'], t5['requires_weather_data'], t5['message'][:60]))

# TEST 6: "Will it rain tomorrow?"
t6 = send_chat("Will it rain tomorrow?")
r6 = (t6["intent"] == "WEATHER_FORECAST" and t6["requires_weather_data"] and len(t6["tool_results"]) > 0)
results.append(("TEST 6: 'Will it rain tomorrow?'", r6, t6['intent'], t6['requires_weather_data'], t6['message'][:60]))

# TEST 7: "Any disaster alerts?"
t7 = send_chat("Any disaster alerts?")
r7 = (t7["intent"] == "WEATHER_ALERT" and t7["requires_weather_data"] and len(t7["tool_results"]) > 0)
results.append(("TEST 7: 'Any disaster alerts?'", r7, t7['intent'], t7['requires_weather_data'], t7['message'][:60]))

# TEST 8: "Has this location experienced floods before?"
t8 = send_chat("Has this location experienced floods before?")
r8 = (t8["intent"] in ["HISTORICAL_DISASTER", "HISTORICAL_WEATHER"] and t8["requires_weather_data"])
results.append(("TEST 8: 'Has this location experienced floods before?'", r8, t8['intent'], t8['requires_weather_data'], t8['message'][:60]))

# TEST 9: "How do I use the map?"
t9 = send_chat("How do I use the map?")
r9 = (t9["intent"] == "WEBSITE_HELP" and not t9["requires_weather_data"] and t9.get("grounded_weather") is None)
results.append(("TEST 9: 'How do I use the map?'", r9, t9['intent'], t9['requires_weather_data'], t9['message'][:60]))

# TEST 10: Follow-up context: Guntur weather -> "What about tomorrow?"
t10_1 = send_chat("What is the weather in Guntur?")
sid_10 = t10_1["session_id"]
t10_2 = send_chat("What about tomorrow?", session_id=sid_10)
r10 = (t10_2["intent"] == "WEATHER_FORECAST" and t10_2["requires_weather_data"] and "Guntur" in t10_2["message"])
results.append(("TEST 10: Follow-up 'What about tomorrow?'", r10, t10_2['intent'], t10_2['requires_weather_data'], t10_2['message'][:60]))

# TEST 11: "Thanks"
t11 = send_chat("Thanks", session_id=sid_10)
r11 = (t11["intent"] == "CASUAL_CONVERSATION" and not t11["requires_weather_data"] and len(t11["tool_results"]) == 0 and "°C" not in t11["message"])
results.append(("TEST 11: 'Thanks'", r11, t11['intent'], t11['requires_weather_data'], t11['message'][:60]))

# TEST 12: Location change: Guntur -> Hyderabad, Then: "What is the temperature?"
t12 = send_chat("What is the temperature?", location_name="Hyderabad, Telangana")
r12 = (t12["intent"] == "WEATHER_CURRENT" and t12["requires_weather_data"] and "Hyderabad" in t12["message"])
results.append(("TEST 12: Location change to Hyderabad", r12, t12['intent'], t12['requires_weather_data'], t12['message'][:60]))

# TEST 13: Open older conversation. Ask: "What is the temperature now?" -> Fresh current weather!
t13_1 = send_chat("What is the temperature?")
sid_13 = t13_1["session_id"]
t13_2 = send_chat("What is the temperature now?", session_id=sid_13)
r13 = (t13_2["intent"] == "WEATHER_CURRENT" and t13_2["requires_weather_data"] and len(t13_2["tool_results"]) > 0)
results.append(("TEST 13: Fresh temperature in old conversation", r13, t13_2['intent'], t13_2['requires_weather_data'], t13_2['message'][:60]))

# TEST 14: Telugu casual: "ఎలా ఉన్నావు?"
t14 = send_chat("ఎలా ఉన్నావు?", language="te")
r14 = (t14["intent"] == "CASUAL_CONVERSATION" and not t14["requires_weather_data"] and len(t14["tool_results"]) == 0 and "°C" not in t14["message"])
results.append(("TEST 14: Telugu casual 'ఎలా ఉన్నావు?'", r14, t14['intent'], t14['requires_weather_data'], t14['message'][:60]))

# TEST 15: Telugu weather: "గుంటూరులో ఇప్పుడు ఉష్ణోగ్రత ఎంత?"
t15 = send_chat("గుంటూరులో ఇప్పుడు ఉష్ణోగ్రత ఎంత?", language="te")
r15 = (t15["intent"] == "WEATHER_CURRENT" and t15["requires_weather_data"] and len(t15["tool_results"]) > 0 and "°C" in t15["message"])
results.append(("TEST 15: Telugu weather 'గుంటూరులో ఇప్పుడు ఉష్ణోగ్రత ఎంత?'", r15, t15['intent'], t15['requires_weather_data'], t15['message'][:60]))

print("\nTEST RESULTS:")
all_passed = True
for name, passed, intent, req_weather, snippet in results:
    status = "PASS [OK]" if passed else "FAIL [X]"
    if not passed:
        all_passed = False
    print(f"{status:10} | {name:42} | Intent: {intent:20} | RequiresWeather: {str(req_weather):5} | Response: {snippet}")

print("=" * 70)
if all_passed:
    print("ALL 15 TEST CASES PASSED PERFECTLY!")
else:
    print("SOME TEST CASES FAILED - CHECK OUTPUT ABOVE")
print("=" * 70)
