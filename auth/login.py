# auth/login.py (Peewee ORM)

from fastapi import HTTPException, status
from database import User, db 
from passlib.context import CryptContext 

# Import necessary helpers from the adjacent signup file
from auth.signup import create_access_token, hash_password 
# We need verify_password here, which is a common helper
from auth.signup import pwd_context # Import pwd_context for verification

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if plain password matches hash"""
    return pwd_context.verify(plain_password, hashed_password)

# --- Main Logic Function ---

def login(email: str, password: str):
    """Handles user login using Peewee ORM"""
    
    db.connect()
    try:
        # 1. Searches database for user with that email (Peewee SELECT query)
        user = User.select().where(User.email == email).first()

        # 2. Check if user exists
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # 3. Verifies password matches the stored hash
        # We use user.password, which stores the hash
        if not verify_password(password, user.password): 
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # 4. If correct, generates JWT token
        access_token = create_access_token(
            data={"sub": user.user_name, "user_id": user.user_id}
        )

        # 5. Returns: success message, user_id, username, token
        return {
            "message": "Login successful!",
            "user_id": user.user_id,
            "username": user.user_name,
            "token": access_token
        }
    finally:
        db.close()
