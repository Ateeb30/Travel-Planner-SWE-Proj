# auth/login.py (Peewee ORM)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import HTTPException, status
from database.database import User, db 
from datetime import datetime, timezone, timedelta
import jwt
import hashlib
import secrets

# --- Security Configuration (Same as signup.py) ---
SECRET_KEY = "YOUR_SUPER_SECRET_KEY_CHANGE_IN_PRODUCTION" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Creates JWT token with expiration time (same as signup)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash with multiple format support"""
    # Try modern hashing first (bcrypt, etc.)
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(
            schemes=["bcrypt", "sha256_crypt"], 
            deprecated="auto"
        )
        return pwd_context.verify(plain_password, hashed_password)
    except:
        # Fallback verification for our custom SHA256 format
        if hashed_password.startswith("sha256$"):
            try:
                _, stored_hash, salt = hashed_password.split("$")
                computed_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
                return secrets.compare_digest(computed_hash, stored_hash)
            except:
                return False
        # Try simple colon-separated format
        elif ":" in hashed_password:
            try:
                stored_hash, salt = hashed_password.split(":")
                computed_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
                return secrets.compare_digest(computed_hash, stored_hash)
            except:
                return False
    return False

# --- Main Logic Function ---
def login(email: str, password: str):
    """Handles user login using Peewee ORM"""
    
    if db.is_closed():
        db.connect()
    try:
        # 1. Search database for user with that email
        user = User.select().where(User.email == email).first()

        # 2. Check if user exists
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        print(f"Found user: {user.user_name}")
        print(f"Stored password hash: {user.password[:50]}...")  # Debug info

        # 3. Verify password matches the stored hash
        if not verify_password(password, user.password): 
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # 4. If correct, generate JWT token
        access_token = create_access_token(
            data={"sub": user.user_name, "user_id": user.user_id}
        )

        # 5. Return success response
        return {
            "message": "Login successful!",
            "user_id": user.user_id,
            "username": user.user_name,
            "token": access_token
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )
    finally:
        if not db.is_closed():
            db.close()

# --- Test Function ---
if __name__ == "__main__":
    # Use the exact same credentials from your successful signup
    test_email = "test1@example.com"  # From your signup
    test_password = "1234567"         # From your signup
    
    print(f"Testing login with:")
    print(f"Email: {test_email}")
    print(f"Password: {test_password}")
    print("-" * 40)

    try:
        result = login(test_email, test_password)
        print("✅ Login successful!")
        print(f"User ID: {result['user_id']}")
        print(f"Username: {result['username']}")
        print(f"Token: {result['token'][:50]}...")
    except HTTPException as e:
        print(f"❌ Login failed: {e.detail}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")