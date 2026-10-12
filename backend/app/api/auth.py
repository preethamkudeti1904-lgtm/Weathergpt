from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User, UserPreference
from app.models.location import SavedLocation
from app.schemas.user import UserCreate, UserLogin, UserOut, Token, UserPreferenceUpdate, UserPreferenceOut, UserTypeUpdate
from app.auth.security import verify_password, get_password_hash, create_access_token, password_service
from app.auth.deps import get_current_user

from pydantic import BaseModel
from typing import Optional
from app.services.sms.service import sms_service
from app.auth.deps import get_current_user, get_current_user_optional

from app.core.phone import normalize_and_validate_phone, mask_phone_number

router = APIRouter(prefix="/auth", tags=["Authentication"])

class SendPhoneOtpRequest(BaseModel):
    phone_number: Optional[str] = None
    phone_country_code: Optional[str] = "+91"

class VerifyPhoneOtpRequest(BaseModel):
    phone_number: str
    otp: str

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Validate password confirmation if provided
    if user_in.confirm_password is not None and user_in.password != user_in.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    # Validate and normalize phone number
    try:
        clean_phone, norm_country_code = normalize_and_validate_phone(
            user_in.phone_number, user_in.phone_country_code or "+91"
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    # Check if user with same email exists
    existing_email = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    # Check if user with same phone number exists
    existing_phone = db.query(User).filter(User.phone_number == clean_phone).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="An account with this phone number already exists.")

    try:
        hashed_pw = password_service.hash_password(user_in.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[Registration Error] Password hashing failed: {e}")
        raise HTTPException(status_code=500, detail="Unable to create your account right now. Please try again.")

    new_user = User(
        name=user_in.name,
        email=user_in.email.lower(),
        phone_number=clean_phone,
        phone_country_code=norm_country_code,
        phone_verified=False,
        password_hash=hashed_pw,
        user_type=user_in.user_type or "General User",
        country=user_in.country or "India",
        state=user_in.state or "Andhra Pradesh",
        preferred_language=user_in.preferred_language or "en",
        default_location=user_in.default_location or "Guntur, Andhra Pradesh"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Initialize default preferences
    pref = db.query(UserPreference).filter(UserPreference.user_id == new_user.id).first()
    if not pref:
        pref = UserPreference(
            user_id=new_user.id,
            theme="system",
            language=new_user.preferred_language,
            temperature_unit="celsius",
            wind_unit="kmh",
            severe_alerts=True,
            forecast_notifications=True,
            sms_alerts_enabled=False
        )
        db.add(pref)

    # Add default saved location (e.g. Guntur)
    loc = db.query(SavedLocation).filter(SavedLocation.user_id == new_user.id).first()
    if not loc:
        loc = SavedLocation(
            user_id=new_user.id,
            location_name="Guntur",
            state="Andhra Pradesh",
            country="India",
            latitude=16.3067,
            longitude=80.4365,
            is_default=True
        )
        db.add(loc)
    db.commit()

    # Automatically trigger initial phone OTP dispatch
    otp_res = await sms_service.create_and_send_phone_otp(db, clean_phone, new_user.id)
    if not otp_res.get("success"):
        err_code = otp_res.get("status_code", 400)
        raise HTTPException(status_code=err_code, detail=otp_res.get("error", "Failed to send verification OTP"))

    token = create_access_token(new_user.id)
    return Token(
        access_token=token,
        token_type="bearer",
        user=UserOut.model_validate(new_user),
        dev_otp=otp_res.get("dev_otp"),
        is_development=otp_res.get("is_development", False),
        sms_provider=otp_res.get("provider"),
        message=otp_res.get("message")
    )

@router.post("/send-phone-otp")
async def send_phone_otp(
    payload: SendPhoneOtpRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    target_phone = payload.phone_number
    if not target_phone and current_user:
        target_phone = current_user.phone_number
    if not target_phone:
        raise HTTPException(status_code=400, detail="Phone number is required to send verification OTP.")

    try:
        clean_phone, norm_country_code = normalize_and_validate_phone(
            target_phone, payload.phone_country_code or "+91"
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    user_id = current_user.id if current_user else None

    # If authenticated and phone number differs, check for duplicate phone number
    if current_user and current_user.phone_number != clean_phone:
        dup = db.query(User).filter(User.phone_number == clean_phone, User.id != current_user.id).first()
        if dup:
            raise HTTPException(status_code=400, detail="An account with this phone number already exists.")
        current_user.phone_number = clean_phone
        current_user.phone_country_code = norm_country_code
        current_user.phone_verified = False
        db.commit()

    res = await sms_service.create_and_send_phone_otp(db, clean_phone, user_id)
    if not res.get("success"):
        status_code = res.get("status_code", 400)
        raise HTTPException(status_code=status_code, detail=res.get("error", "Failed to send OTP"))
    return res

@router.post("/verify-phone-otp")
def verify_phone_otp(
    payload: VerifyPhoneOtpRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    try:
        clean_phone, _ = normalize_and_validate_phone(payload.phone_number)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    user_id = current_user.id if current_user else None
    success, msg, status_code, verified_user = sms_service.verify_phone_otp(db, clean_phone, payload.otp, user_id)
    if not success:
        raise HTTPException(status_code=status_code, detail=msg)

    # Issue access token for the verified user
    user_data = None
    token = None
    if verified_user:
        user_data = UserOut.model_validate(verified_user)
        token = create_access_token(verified_user.id)
    elif current_user:
        db.refresh(current_user)
        user_data = UserOut.model_validate(current_user)
        token = create_access_token(current_user.id)

    return {
        "success": True,
        "message": msg,
        "phone_verified": True,
        "access_token": token,
        "token_type": "bearer",
        "user": user_data
    }

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email.lower()).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.phone_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Phone number is not verified. Please verify your phone number to continue."
        )

    token = create_access_token(user.id)
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)

@router.put("/user-type", response_model=UserOut)
def update_user_type(payload: UserTypeUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.user_type = payload.user_type
    db.commit()
    db.refresh(current_user)
    return UserOut.model_validate(current_user)

@router.put("/preferences", response_model=UserPreferenceOut)
def update_preferences(prefs_in: UserPreferenceUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.add(pref)

    for field, value in prefs_in.model_dump(exclude_unset=True).items():
        setattr(pref, field, value)

    # Sync language
    if prefs_in.language:
        current_user.preferred_language = prefs_in.language

    db.commit()
    db.refresh(pref)
    return UserPreferenceOut.model_validate(pref)
