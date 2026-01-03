"""
JWT Authentication for MDSA Dashboard
Provides secure token-based authentication for admin features.
"""

import os
import sys
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
from fastapi import HTTPException, Request, status
from fastapi.responses import RedirectResponse


# =================================================================
# ENVIRONMENT VALIDATION (Security Critical)
# =================================================================

REQUIRED_ENV_VARS = {
    'MDSA_ADMIN_PASSWORD': 'Admin password',
    'MDSA_JWT_SECRET': 'JWT signing secret',
}

def validate_environment():
    """
    Ensure all required environment variables are set with non-default values.
    Exits the application if validation fails.
    """
    missing = []
    defaults = []

    # Check for missing vars
    for var, description in REQUIRED_ENV_VARS.items():
        value = os.getenv(var)
        if not value:
            missing.append(f"{var} ({description})")

    # Check for default/insecure values
    admin_password = os.getenv('MDSA_ADMIN_PASSWORD', '')
    if admin_password == 'mdsa_admin_2025':
        defaults.append('MDSA_ADMIN_PASSWORD is using default value "mdsa_admin_2025"')

    jwt_secret = os.getenv('MDSA_JWT_SECRET', '')
    if 'change-in-production' in jwt_secret:
        defaults.append('MDSA_JWT_SECRET is using default value')

    encryption_key = os.getenv('MDSA_ENCRYPTION_KEY', '')
    if 'change-in-production' in encryption_key:
        defaults.append('MDSA_ENCRYPTION_KEY is using default value')

    # Report errors
    if missing or defaults:
        print("\n" + "="*70)
        print("[SECURITY] MDSA SECURITY CONFIGURATION ERROR")
        print("="*70)

        if missing:
            print("\n[ERROR] Missing required environment variables:")
            for var in missing:
                print(f"   - {var}")

        if defaults:
            print("\n[WARNING] Using default/insecure values:")
            for msg in defaults:
                print(f"   - {msg}")

        print("\n[ACTION REQUIRED]")
        print("   1. Copy .env.example to .env in the project root")
        print("   2. Set secure values for all required variables")
        print("   3. Generate secrets with: openssl rand -hex 32")
        print("   4. Set a strong admin password (min 12 characters)")
        print("   5. Restart the MDSA dashboard")
        print("\n[EXAMPLE]")
        print("   export MDSA_ADMIN_PASSWORD='YourSecurePassword123!'")
        print("   export MDSA_JWT_SECRET=$(openssl rand -hex 32)")
        print("   export MDSA_ENCRYPTION_KEY=$(openssl rand -hex 32)")
        print("="*70 + "\n")

        sys.exit(1)

# Call validation on module import
validate_environment()

# =================================================================
# JWT CONFIGURATION
# =================================================================

# Secret key for JWT (validated above - must be set)
SECRET_KEY = os.getenv('MDSA_JWT_SECRET')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

# Admin credentials (validated above - must be set)
DEFAULT_ADMIN_USERNAME = os.getenv('MDSA_ADMIN_USERNAME', 'admin')
DEFAULT_ADMIN_PASSWORD = os.getenv('MDSA_ADMIN_PASSWORD')


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt (secure, with automatic salt).

    Args:
        password: Plain text password

    Returns:
        Bcrypt hash as string
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hash to verify against

    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token to verify

    Returns:
        Decoded token data if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None


def authenticate_user(username: str, password: str) -> Optional[Dict[str, str]]:
    """
    Authenticate a user with username and password.

    Args:
        username: Username
        password: Password

    Returns:
        User data if authenticated, None otherwise
    """
    # Check against admin credentials from environment
    if username == DEFAULT_ADMIN_USERNAME:
        # Simple comparison - for single admin user
        # In production, you would store bcrypt hashes in a database
        if password == DEFAULT_ADMIN_PASSWORD:
            return {
                "username": username,
                "role": "admin",
                "name": "MDSA Administrator"
            }

    # TODO: Add database-based user authentication for production
    # Store users with bcrypt hashed passwords in database:
    # user = db.get_user(username)
    # if user and verify_password(password, user.password_hash):
    #     return user

    return None


def get_current_user_from_cookie(request: Request) -> Optional[Dict[str, Any]]:
    """
    Get the current user from the JWT cookie.

    Args:
        request: FastAPI request object

    Returns:
        User data if authenticated, None otherwise
    """
    token = request.cookies.get("access_token")

    if not token:
        return None

    # Remove "Bearer " prefix if present
    if token.startswith("Bearer "):
        token = token[7:]

    payload = verify_token(token)

    if payload is None:
        return None

    return payload


def require_auth(redirect_to_login: bool = True):
    """
    Decorator to require authentication for a route.

    Args:
        redirect_to_login: If True, redirect to login page. If False, raise 401.

    Usage:
        @app.get("/admin/rag")
        @require_auth()
        async def rag_admin(request: Request):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user = get_current_user_from_cookie(request)

            if user is None:
                if redirect_to_login:
                    return RedirectResponse(
                        url=f"/login?next={request.url.path}",
                        status_code=status.HTTP_302_FOUND
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not authenticated"
                    )

            # Add user to request state
            request.state.user = user

            return await func(request, *args, **kwargs)

        return wrapper
    return decorator


def require_admin():
    """
    Decorator to require admin role for a route.

    Usage:
        @app.delete("/admin/tools/{tool_id}")
        @require_admin()
        async def delete_tool(request: Request, tool_id: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user = get_current_user_from_cookie(request)

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )

            if user.get("role") != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )

            # Add user to request state
            request.state.user = user

            return await func(request, *args, **kwargs)

        return wrapper
    return decorator


# Session management
class SessionManager:
    """Manage user sessions."""

    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, username: str, token: str) -> None:
        """Create a new session."""
        self.active_sessions[username] = {
            "token": token,
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        }

    def update_activity(self, username: str) -> None:
        """Update last activity time."""
        if username in self.active_sessions:
            self.active_sessions[username]["last_active"] = datetime.utcnow()

    def invalidate_session(self, username: str) -> None:
        """Invalidate a session."""
        if username in self.active_sessions:
            del self.active_sessions[username]

    def is_session_valid(self, username: str, token: str) -> bool:
        """Check if a session is valid."""
        if username not in self.active_sessions:
            return False

        session = self.active_sessions[username]

        # Check if token matches
        if session["token"] != token:
            return False

        # Check if session is expired (24 hours)
        if (datetime.utcnow() - session["created_at"]).total_seconds() > 86400:
            self.invalidate_session(username)
            return False

        return True


# Global session manager instance
session_manager = SessionManager()
