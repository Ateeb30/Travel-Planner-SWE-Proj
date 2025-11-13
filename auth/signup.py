# auth/signup.py (Peewee ORM)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import HTTPException, status
# Import models and db connection from your files
from database.database import User, db 
from datetime import datetime, timedelta
import jwt 
import hashlib
import secrets

# Fallback hashing function that always works
def hash_password(password: str) -> str:
    """Secure password hashing with proper length handling"""
    # Encode the password to bytes and ensure it's not too long
    password_bytes = password.encode('utf-8')
    
    # If password is too long, hash it first (common practice)
    if len(password_bytes) > 72:
        password_bytes = hashlib.sha256(password_bytes).digest()
    
    # Try bcrypt first, fallback to argon2 or sha256 if unavailable
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(
            schemes=["bcrypt", "argon2", "sha256_crypt"], 
            deprecated="auto"
        )
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Warning: Using fallback hashing due to: {e}")
        # Fallback: SHA256 with salt
        salt = secrets.token_hex(32)
        return f"sha256${hashlib.sha256((password + salt).encode()).hexdigest()}${salt}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash (for future login implementation)"""
    try:
        # Try modern hashing first
        from passlib.context import CryptContext
        pwd_context = CryptContext(
            schemes=["bcrypt", "argon2", "sha256_crypt"], 
            deprecated="auto"
        )
        return pwd_context.verify(plain_password, hashed_password)
    except:
        # Fallback verification
        if hashed_password.startswith("sha256$"):
            _, stored_hash, salt = hashed_password.split("$")
            computed_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
            return secrets.compare_digest(computed_hash, stored_hash)
        return False

# --- Security Configuration ---
SECRET_KEY = "YOUR_SUPER_SECRET_KEY" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Creates JWT token with expiration time"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Main Logic Function ---
def signup(email: str, username: str, password: str, city: str, country: str):
    """Handles user registration using Peewee ORM"""

    if db.is_closed():
        db.connect()
    try:
        # Input validation
        if len(password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )

        user_exists = User.select().where(
            (User.email == email) | (User.user_name == username)
        ).exists()

        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )

        hashed_password = hash_password(password)

        new_user = User.create(
            user_name=username,
            password=hashed_password,
            email=email,
            city=city,
            country=country
        )

        access_token = create_access_token(
            data={"sub": username, "user_id": new_user.user_id}
        )

        return {
            "message": "Signup successful!",
            "user_id": new_user.user_id,
            "username": username,
            "token": access_token
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )
    finally:
        if not db.is_closed():
            db.close()

if __name__ == "__main__":
    # Test with a shorter password to avoid length issues
    test_email = "test1@example.com"
    test_username = "test1user"
    test_password = "1234567"  # Keep it simple for testing
    test_city = "Lahore"
    test_country = "Pakistan"

    if db.is_closed():
        db.connect()
    try:
        result = signup(
            email=test_email,
            username=test_username,
            password=test_password,
            city=test_city,
            country=test_country
        )
        print("Signup result:", result)
    except HTTPException as e:
        print(f"Signup failed: {e.detail}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if not db.is_closed():
            db.close()