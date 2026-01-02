from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"

if not SECRET_KEY:
    raise ValueError("BETTER_AUTH_SECRET environment variable is not set")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    role: Optional[str] = "user"

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Verifies the JWT token issued by Better Auth and returns the user.
    Usage:
        @app.get("/items")
        def read_items(user: User = Depends(get_current_user)):
            ...
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify the signature using the shared secret
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None:
            raise credentials_exception
            
        # You can construct the user object from the token claims directly
        # or fetch the full user from the database if needed.
        # For stateless auth, using claims is preferred.
        user = User(
            id=user_id,
            email=email,
            name=payload.get("name"),
            role=payload.get("role", "user")
        )
        return user
        
    except JWTError:
        raise credentials_exception
