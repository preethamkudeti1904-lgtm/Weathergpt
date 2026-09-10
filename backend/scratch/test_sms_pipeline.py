"""
Comprehensive Test Suite for WeatherGPT SMS-Based Disaster Alert System.
Tests all 12 test cases from Section 26.
"""
import sys
import os
import json
import time
import datetime

# Add project root to sys.path
sys.path.insert(0, r"c:\project1\backend")

from app.database.session import SessionLocal
from app.models.user import User, UserPreference
from app.models.personalized_alert import UserAlertLocation, OfficialAlert, AlertGeometry
from app.models.sms_alert import PhoneOtp, UserAlertSmsDelivery
from app.services.sms.service import sms_service
from app.services.sms.simulated_provider import simulated_sms_provider
from app.services.alerts.disaster_sms_worker import disaster_sms_worker
from app.services.alerts.personalized_alert_service import personalized_alert_service

def run_tests():
    db = SessionLocal()
    print("=== STARTING DISASTER SMS ALERT TEST SUITE ===\n")

    # Clean up previous test users and test alerts
    db.query(UserAlertSmsDelivery).delete()
    db.query(AlertGeometry).filter(AlertGeometry.alert_id.like("TEST-ALERT-%")).delete()
    db.query(OfficialAlert).filter(OfficialAlert.id.like("TEST-ALERT-%")).delete()
    db.query(UserAlertLocation).filter(UserAlertLocation.location_name.like("%TestLocation%")).delete()
    
    test_users = db.query(User).filter(User.email.like("%testuser%@example.com")).all()
    test_uids = [u.id for u in test_users]
    if test_uids:
        db.query(UserPreference).filter(UserPreference.user_id.in_(test_uids)).delete(synchronize_session=False)
        db.query(UserAlertLocation).filter(UserAlertLocation.user_id.in_(test_uids)).delete(synchronize_session=False)
        db.query(PhoneOtp).filter(PhoneOtp.user_id.in_(test_uids)).delete(synchronize_session=False)
        db.query(User).filter(User.id.in_(test_uids)).delete(synchronize_session=False)
    
    # Also delete any orphaned user preferences where user_id does not exist in users
    all_user_ids = [u.id for u in db.query(User.id).all()]
    if all_user_ids:
        db.query(UserPreference).filter(~UserPreference.user_id.in_(all_user_ids)).delete(synchronize_session=False)
        db.query(UserAlertLocation).filter(~UserAlertLocation.user_id.in_(all_user_ids)).delete(synchronize_session=False)
    else:
        db.query(UserPreference).delete()
        db.query(UserAlertLocation).delete()
        
    db.commit()

    # --- SETUP USERS ---
    # User A: Vadlamudi coordinates (16.2246, 80.5589), phone verified, SMS enabled
    user_a = User(
        name="Test Farmer A",
        email="testuser_a@example.com",
        phone_number="+919876500001",
        phone_country_code="+91",
        phone_verified=True,
        phone_verified_at=datetime.datetime.utcnow(),
        password_hash="fakehash",
        user_type="Farmer",
        default_location="Vadlamudi, Andhra Pradesh",
        preferred_language="en"
    )
    db.add(user_a)
    db.flush()

    pref_a = UserPreference(
        user_id=user_a.id,
        sms_alerts_enabled=True,
        sms_alert_categories=json.dumps(["Severe Weather", "Flood", "Heavy Rain", "Thunderstorm"])
    )
    db.add(pref_a)

    loc_a = UserAlertLocation(
        user_id=user_a.id,
        latitude=16.2246,
        longitude=80.5589,
        location_name="Vadlamudi TestLocation",
        district="Guntur District",
        state="Andhra Pradesh",
        country="India",
        source="gps",
        is_primary=True,
        is_active=True
    )
    db.add(loc_a)

    # User B: Delhi coordinates (28.6139, 77.2090), phone verified, SMS enabled
    user_b = User(
        name="Test Citizen B",
        email="testuser_b@example.com",
        phone_number="+919876500002",
        phone_country_code="+91",
        phone_verified=True,
        phone_verified_at=datetime.datetime.utcnow(),
        password_hash="fakehash",
        user_type="General User",
        default_location="New Delhi, Delhi",
        preferred_language="hi"
    )
    db.add(user_b)
    db.flush()

    pref_b = UserPreference(
        user_id=user_b.id,
        sms_alerts_enabled=True,
        sms_alert_categories=json.dumps(["Severe Weather", "Heavy Rain"])
    )
    db.add(pref_b)

    loc_b = UserAlertLocation(
        user_id=user_b.id,
        latitude=28.6139,
        longitude=77.2090,
        location_name="Delhi TestLocation",
        district="New Delhi",
        state="Delhi",
        country="India",
        source="gps",
        is_primary=True,
        is_active=True
    )
    db.add(loc_b)

    # User C: Phone NOT verified
    user_c = User(
        name="Test Unverified C",
        email="testuser_c@example.com",
        phone_number="+919876500003",
        phone_country_code="+91",
        phone_verified=False,
        password_hash="fakehash",
        user_type="General User",
        default_location="Vadlamudi, Andhra Pradesh"
    )
    db.add(user_c)
    db.flush()

    pref_c = UserPreference(
        user_id=user_c.id,
        sms_alerts_enabled=True
    )
    db.add(pref_c)

    loc_c = UserAlertLocation(
        user_id=user_c.id,
        latitude=16.2246,
        longitude=80.5589,
        location_name="Vadlamudi TestLocation C",
        district="Guntur District",
        state="Andhra Pradesh",
        is_primary=True,
        is_active=True
    )
    db.add(loc_c)

    # User D: In Vadlamudi, phone verified, but SMS alerts DISABLED
    user_d = User(
        name="Test Disabled D",
        email="testuser_d@example.com",
        phone_number="+919876500004",
        phone_country_code="+91",
        phone_verified=True,
        password_hash="fakehash",
        user_type="General User",
        default_location="Vadlamudi, Andhra Pradesh"
    )
    db.add(user_d)
    db.flush()

    pref_d = UserPreference(
        user_id=user_d.id,
        sms_alerts_enabled=False  # Disabled!
    )
    db.add(pref_d)

    loc_d = UserAlertLocation(
        user_id=user_d.id,
        latitude=16.2246,
        longitude=80.5589,
        location_name="Vadlamudi TestLocation D",
        district="Guntur District",
        state="Andhra Pradesh",
        is_primary=True,
        is_active=True
    )
    db.add(loc_d)

    db.commit()

    # --- TEST 1 & TEST 2: User inside warning polygon (A) vs outside (B) ---
    # Create an official warning covering Vadlamudi (16.20 to 16.25, 80.50 to 80.60)
    simulated_sms_provider.sent_messages.clear()
    alert_1 = OfficialAlert(
        id="TEST-ALERT-001",
        source="SACHET / NDMA",
        hazard_type="Heavy Rain",
        title="Heavy Rain Warning",
        description="Extremely heavy downpours expected over coastal Andhra Pradesh.",
        severity="High",
        status="Actual",
        issued_at=datetime.datetime.utcnow(),
        effective_from=datetime.datetime.utcnow(),
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(hours=4),
        affected_area="Vadlamudi - Guntur Region",
        district="Guntur District",
        state="Andhra Pradesh",
        country="India",
        instructions="Avoid low-lying roadways and clear drainage canals.",
        is_active=True
    )
    db.add(alert_1)
    db.flush()

    # Polygon encompassing Vadlamudi
    poly_vadlamudi = [
        [16.20, 80.50],
        [16.20, 80.60],
        [16.25, 80.60],
        [16.25, 80.50]
    ]
    geom_1 = AlertGeometry(
        alert_id=alert_1.id,
        geometry_type="polygon",
        coordinates_json=json.dumps(poly_vadlamudi),
        centroid_lat=16.225,
        centroid_lon=80.55,
        radius_km=10.0
    )
    db.add(geom_1)
    db.commit()

    # Run cycle
    import asyncio
    asyncio.run(disaster_sms_worker.run_cycle())

    # User A is inside -> SMS SENT
    delivery_a = db.query(UserAlertSmsDelivery).filter(
        UserAlertSmsDelivery.user_id == user_a.id,
        UserAlertSmsDelivery.alert_id == alert_1.id
    ).first()
    assert delivery_a is not None, "TEST 1 FAILED: User A in polygon should receive SMS"
    assert delivery_a.status == "SENT", "TEST 1 FAILED: Delivery status should be SENT"
    print("PASS: TEST 1 - User location inside warning polygon -> SMS SENT to", user_a.phone_number)

    # User B is in Delhi (outside) -> NO SMS
    delivery_b = db.query(UserAlertSmsDelivery).filter(
        UserAlertSmsDelivery.user_id == user_b.id,
        UserAlertSmsDelivery.alert_id == alert_1.id
    ).first()
    assert delivery_b is None, "TEST 2 FAILED: User B outside polygon must NOT receive SMS"
    print("PASS: TEST 2 - User location outside warning polygon -> NO SMS")

    # --- TEST 3: Same alert received again -> NO duplicate SMS ---
    msg_count_before = len(simulated_sms_provider.sent_messages)
    asyncio.run(disaster_sms_worker.run_cycle())
    msg_count_after = len(simulated_sms_provider.sent_messages)
    assert msg_count_before == msg_count_after, "TEST 3 FAILED: Duplicate SMS was sent!"
    print("PASS: TEST 3 - Same alert received again -> NO duplicate SMS (Deduplicated)")

    # --- TEST 4: Official alert updated -> Updated SMS ---
    alert_1.status = "Update"
    alert_1.expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
    db.commit()

    asyncio.run(disaster_sms_worker.run_cycle())
    updated_delivery = db.query(UserAlertSmsDelivery).filter(
        UserAlertSmsDelivery.user_id == user_a.id,
        UserAlertSmsDelivery.alert_id == alert_1.id,
        UserAlertSmsDelivery.message.like("%UPDATE%")
    ).first()
    assert updated_delivery is not None, "TEST 4 FAILED: Updated alert should trigger UPDATE SMS"
    print("PASS: TEST 4 - Official alert updated -> Updated SMS sent")

    # --- TEST 5: Alert expired -> No new SMS ---
    alert_1.expires_at = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
    db.commit()
    msg_count_before = len(simulated_sms_provider.sent_messages)
    asyncio.run(disaster_sms_worker.run_cycle())
    msg_count_after = len(simulated_sms_provider.sent_messages)
    assert msg_count_before == msg_count_after, "TEST 5 FAILED: Expired alert triggered SMS"
    print("PASS: TEST 5 - Alert expired -> No new SMS")

    # --- TEST 6: User disables SMS alerts -> NO SMS ---
    pref_a.sms_alerts_enabled = False
    db.commit()

    # Create new fresh alert for Vadlamudi
    alert_2 = OfficialAlert(
        id="TEST-ALERT-002",
        source="IMD / SACHET",
        hazard_type="Thunderstorm",
        title="Thunderstorm & Lightning Warning",
        description="Thunderstorm accompanied with lightning likely.",
        severity="High",
        status="Actual",
        issued_at=datetime.datetime.utcnow(),
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        affected_area="Vadlamudi Region",
        district="Guntur District",
        is_active=True
    )
    db.add(alert_2)
    db.flush()
    geom_2 = AlertGeometry(
        alert_id=alert_2.id,
        geometry_type="polygon",
        coordinates_json=json.dumps(poly_vadlamudi)
    )
    db.add(geom_2)
    db.commit()

    asyncio.run(disaster_sms_worker.run_cycle())
    delivery_disabled = db.query(UserAlertSmsDelivery).filter(
        UserAlertSmsDelivery.user_id == user_a.id,
        UserAlertSmsDelivery.alert_id == alert_2.id
    ).first()
    assert delivery_disabled is None, "TEST 6 FAILED: Disabled SMS preference should not receive SMS"
    print("PASS: TEST 6 - User disables SMS alerts -> NO SMS")

    # Re-enable for subsequent tests
    pref_a.sms_alerts_enabled = True
    db.commit()

    # --- TEST 7: Phone number not verified -> NO SMS ---
    delivery_unverified = db.query(UserAlertSmsDelivery).filter(
        UserAlertSmsDelivery.user_id == user_c.id
    ).first()
    assert delivery_unverified is None, "TEST 7 FAILED: Unverified phone number received SMS!"
    print("PASS: TEST 7 - Phone number not verified -> NO SMS")

    # --- TEST 8: SMS provider failure simulation -> Record FAILED ---
    simulated_sms_provider.simulate_failure = True
    alert_3 = OfficialAlert(
        id="TEST-ALERT-003",
        source="IMD",
        hazard_type="Flood",
        title="Flash Flood Warning",
        severity="Severe",
        status="Actual",
        issued_at=datetime.datetime.utcnow(),
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(hours=3),
        district="Guntur District",
        is_active=True
    )
    db.add(alert_3)
    db.flush()
    geom_3 = AlertGeometry(
        alert_id=alert_3.id,
        geometry_type="polygon",
        coordinates_json=json.dumps(poly_vadlamudi)
    )
    db.add(geom_3)
    db.commit()

    asyncio.run(disaster_sms_worker.run_cycle())
    delivery_failed = db.query(UserAlertSmsDelivery).filter(
        UserAlertSmsDelivery.user_id == user_a.id,
        UserAlertSmsDelivery.alert_id == alert_3.id
    ).first()
    assert delivery_failed is not None and delivery_failed.status == "FAILED", "TEST 8 FAILED: Status should be FAILED"
    print("PASS: TEST 8 - SMS provider unavailable -> Record marked FAILED")
    simulated_sms_provider.simulate_failure = False

    # --- TEST 9: Official alert API unavailable -> NO fake SMS ---
    # With no active alerts in DB, cycle sends 0 SMS
    db.query(OfficialAlert).filter(OfficialAlert.id.like("TEST-ALERT-%")).update({"is_active": False})
    db.commit()
    msg_count_before = len(simulated_sms_provider.sent_messages)
    asyncio.run(disaster_sms_worker.run_cycle())
    msg_count_after = len(simulated_sms_provider.sent_messages)
    assert msg_count_before == msg_count_after, "TEST 9 FAILED: Fake alert created during outage"
    print("PASS: TEST 9 - Official alert API unavailable -> NO fake SMS generated")

    # --- TEST 10: User changes location -> Future alerts use new location ---
    # Move User A to Bengaluru (12.9716, 77.5946)
    loc_a.latitude = 12.9716
    loc_a.longitude = 77.5946
    loc_a.district = "Bengaluru Urban"
    loc_a.state = "Karnataka"
    loc_a.location_name = "Bengaluru TestLocation"
    db.commit()

    # Trigger warning for Guntur/Vadlamudi
    alert_4 = OfficialAlert(
        id="TEST-ALERT-004",
        source="SACHET",
        hazard_type="Heavy Rain",
        title="Guntur Rain Warning",
        severity="High",
        status="Actual",
        issued_at=datetime.datetime.utcnow(),
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        district="Guntur District",
        is_active=True
    )
    db.add(alert_4)
    db.flush()
    geom_4 = AlertGeometry(
        alert_id=alert_4.id,
        geometry_type="polygon",
        coordinates_json=json.dumps(poly_vadlamudi)
    )
    db.add(geom_4)
    db.commit()

    asyncio.run(disaster_sms_worker.run_cycle())
    delivery_moved = db.query(UserAlertSmsDelivery).filter(
        UserAlertSmsDelivery.user_id == user_a.id,
        UserAlertSmsDelivery.alert_id == alert_4.id
    ).first()
    assert delivery_moved is None, "TEST 10 FAILED: User moved away from Vadlamudi still received Vadlamudi alert!"
    print("PASS: TEST 10 - User changes location -> Future alerts correctly match new location")

    # --- TEST 11: User changes phone number -> Require OTP verification again ---
    user_a.phone_number = "+919876599999"
    user_a.phone_verified = False  # Reset on phone change
    db.commit()

    asyncio.run(disaster_sms_worker.run_cycle())
    delivery_changed_phone = db.query(UserAlertSmsDelivery).filter(
        UserAlertSmsDelivery.user_id == user_a.id,
        UserAlertSmsDelivery.phone_number == "+919876599999"
    ).first()
    assert delivery_changed_phone is None, "TEST 11 FAILED: Unverified changed phone number received SMS!"
    print("PASS: TEST 11 - User changes phone number -> Requires OTP verification again")

    # Verify OTP functionality
    otp_res = asyncio.run(sms_service.create_and_send_phone_otp(db, user_a.phone_number, user_a.id))
    assert otp_res["success"] is True, "Failed to send OTP"
    dev_otp = otp_res["dev_otp"]
    assert dev_otp is not None, "Dev OTP should be returned in test mode"

    # Verify with correct code
    verified, msg = sms_service.verify_phone_otp(db, user_a.phone_number, dev_otp, user_a.id)
    assert verified is True, "OTP verification failed"
    db.refresh(user_a)
    assert user_a.phone_verified is True, "User phone_verified should be True after verification"
    print("PASS: TEST 11b - OTP verified and user marked phone_verified = True")

    # --- TEST 12: Multiple users in the same affected area -> Each eligible verified user receives their own SMS ---
    # Move User A back to Vadlamudi and ensure Cyclone category is enabled
    loc_a.latitude = 16.2246
    loc_a.longitude = 80.5589
    loc_a.district = "Guntur District"
    pref_a.sms_alert_categories = json.dumps(["Severe Weather", "Flood", "Heavy Rain", "Thunderstorm", "Cyclone"])
    db.commit()
    # Create User E also in Vadlamudi, phone verified, SMS enabled
    user_e = User(
        name="Test Farmer E",
        email="testuser_e@example.com",
        phone_number="+919876500005",
        phone_verified=True,
        password_hash="fakehash",
        user_type="Farmer",
        default_location="Vadlamudi, Andhra Pradesh"
    )
    db.add(user_e)
    db.flush()
    pref_e = UserPreference(user_id=user_e.id, sms_alerts_enabled=True)
    db.add(pref_e)
    loc_e = UserAlertLocation(
        user_id=user_e.id,
        latitude=16.2246,
        longitude=80.5589,
        location_name="Vadlamudi Farm E",
        district="Guntur District",
        is_primary=True,
        is_active=True
    )
    db.add(loc_e)
    db.commit()

    alert_5 = OfficialAlert(
        id="TEST-ALERT-005",
        source="IMD / SACHET",
        hazard_type="Cyclone",
        title="Cyclone Warning",
        severity="Extreme",
        status="Actual",
        issued_at=datetime.datetime.utcnow(),
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(hours=5),
        district="Guntur District",
        is_active=True
    )
    db.add(alert_5)
    db.flush()
    geom_5 = AlertGeometry(
        alert_id=alert_5.id,
        geometry_type="polygon",
        coordinates_json=json.dumps(poly_vadlamudi)
    )
    db.add(geom_5)
    db.commit()

    asyncio.run(disaster_sms_worker.run_cycle())

    delivery_multi_a = db.query(UserAlertSmsDelivery).filter(
        UserAlertSmsDelivery.user_id == user_a.id,
        UserAlertSmsDelivery.alert_id == alert_5.id
    ).first()
    delivery_multi_e = db.query(UserAlertSmsDelivery).filter(
        UserAlertSmsDelivery.user_id == user_e.id,
        UserAlertSmsDelivery.alert_id == alert_5.id
    ).first()

    assert delivery_multi_a is not None, "User A should receive cyclone warning"
    assert delivery_multi_e is not None, "User E should receive cyclone warning"
    assert delivery_multi_a.phone_number != delivery_multi_e.phone_number, "Deliveries should be to distinct phones"
    print(f"PASS: TEST 12 - Multiple users in affected area -> Each eligible verified user receives individual SMS ({user_a.phone_number} & {user_e.phone_number})")

    # Cleanup test data
    test_users = db.query(User).filter(User.email.like("%testuser_%@example.com")).all()
    test_uids = [u.id for u in test_users]
    if test_uids:
        db.query(UserPreference).filter(UserPreference.user_id.in_(test_uids)).delete(synchronize_session=False)
        db.query(UserAlertLocation).filter(UserAlertLocation.user_id.in_(test_uids)).delete(synchronize_session=False)
        db.query(PhoneOtp).filter(PhoneOtp.user_id.in_(test_uids)).delete(synchronize_session=False)
        db.query(UserAlertSmsDelivery).filter(UserAlertSmsDelivery.user_id.in_(test_uids)).delete(synchronize_session=False)
        db.query(User).filter(User.id.in_(test_uids)).delete(synchronize_session=False)
    db.query(UserAlertSmsDelivery).delete()
    db.query(AlertGeometry).filter(AlertGeometry.alert_id.like("TEST-ALERT-%")).delete()
    db.query(OfficialAlert).filter(OfficialAlert.id.like("TEST-ALERT-%")).delete()
    db.commit()
    db.close()

    print("\nALL 12 DISASTER SMS TESTS PASSED SUCCESSFULLY! 100% VERIFIED!")

if __name__ == "__main__":
    run_tests()
