# auth/signup.py (Peewee ORM)

from fastapi import HTTPException, status
# Import models and db connection from your files
from database import User, db 
from datetime import datetime, timedelta
import jwt 
from passlib.context import CryptContext 
import random

# --- Security Configuration (Required for hashing) ---
SECRET_KEY = "YOUR_SUPER_SECRET_KEY" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    "Hashing Password"
    return pwd_context.hash(password)

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
    
    db.connect()
    try:
        # 1. Check if email/username already exists in database
        # Peewee query for checking existence 
        user_exists = User.select().where(
            (User.email == email) | (User.user_name == username)
        ).exists()
        
        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )

        # 2. Hash the password
        hashed_password = hash_password(password)

        # 3. Create new User record in database (Peewee INSERT operation)
        new_user = User.create(
            user_name=username,
            password=hashed_password, # Storing the hash in the 'password' field
            email=email,
            city=city,
            country=country
        )
        new_user_id = new_user.user_id
        
        # 4. Generates JWT token for the user
        access_token = create_access_token(
            data={"sub": username, "user_id": new_user_id}
        )

        # 5. Returns: success message, user_id, username, token
        return {
            "message": "Signup successful!",
            "user_id": new_user_id,
            "username": username,
            "token": access_token
        }
    finally:
        db.close()