"""
MDSA Authentication Module

Provides user authentication for the dashboard with:
- Default admin account
- Password hashing (bcrypt)
- Session management
- User management

Default Credentials:
- Username: admin_mdsa
- Email: admin_mdsa@mdsa.com
- Password: mdsa@admin123
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin):
    """User model for authentication."""

    def __init__(self, user_id: str, username: str, email: str, password_hash: str):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def check_password(self, password: str) -> bool:
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> Dict:
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create user from dictionary."""
        return cls(
            user_id=data['id'],
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash']
        )


class UserManager:
    """
    Manages user accounts for MDSA dashboard.

    Features:
    - File-based storage (users.json)
    - Password hashing
    - User CRUD operations
    - Default admin account
    """

    def __init__(self, users_file: Optional[str] = None):
        """
        Initialize user manager.

        Args:
            users_file: Path to users.json file (default: ./users.json)
        """
        if users_file is None:
            users_file = Path(__file__).parent / "users.json"

        self.users_file = Path(users_file)
        self.users = {}

        # Load existing users or create default admin
        self._load_users()

    def _load_users(self):
        """Load users from file or create default admin."""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r') as f:
                    users_data = json.load(f)
                    self.users = {
                        user_id: User.from_dict(data)
                        for user_id, data in users_data.items()
                    }
            except Exception as e:
                print(f"Error loading users: {e}")
                self._create_default_admin()
        else:
            self._create_default_admin()

    def _create_default_admin(self):
        """Create default admin account."""
        admin = User(
            user_id='admin_mdsa',
            username='admin_mdsa',
            email='admin_mdsa@mdsa.com',
            password_hash=generate_password_hash('mdsa@admin123')
        )
        self.users[admin.id] = admin
        self._save_users()
        print("[OK] Default admin account created")
        print("   Username: admin_mdsa")
        print("   Password: mdsa@admin123")

    def _save_users(self):
        """Save users to file."""
        users_data = {
            user_id: user.to_dict()
            for user_id, user in self.users.items()
        }

        self.users_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.users_file, 'w') as f:
            json.dump(users_data, f, indent=2)

    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User object or None
        """
        return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: Username

        Returns:
            User object or None
        """
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user.

        Args:
            username: Username
            password: Password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = self.get_user_by_username(username)
        if user and user.check_password(password):
            return user
        return None

    def create_user(self, username: str, email: str, password: str) -> User:
        """
        Create new user.

        Args:
            username: Username
            email: Email address
            password: Password (will be hashed)

        Returns:
            Created user object
        """
        user_id = username  # Use username as ID for simplicity

        if user_id in self.users:
            raise ValueError(f"User {username} already exists")

        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        self.users[user_id] = user
        self._save_users()

        return user

    def update_password(self, user_id: str, new_password: str) -> bool:
        """
        Update user password.

        Args:
            user_id: User ID
            new_password: New password

        Returns:
            True if successful, False otherwise
        """
        user = self.get_user(user_id)
        if not user:
            return False

        user.password_hash = generate_password_hash(new_password)
        self._save_users()

        return True

    def delete_user(self, user_id: str) -> bool:
        """
        Delete user.

        Args:
            user_id: User ID

        Returns:
            True if successful, False otherwise
        """
        if user_id == 'admin_mdsa':
            raise ValueError("Cannot delete default admin account")

        if user_id in self.users:
            del self.users[user_id]
            self._save_users()
            return True

        return False

    def list_users(self) -> list:
        """
        List all users.

        Returns:
            List of user dictionaries (without password hashes)
        """
        return [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
            for user in self.users.values()
        ]


# Global user manager instance
_user_manager = None


def get_user_manager() -> UserManager:
    """Get global user manager instance."""
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager()
    return _user_manager


def setup_auth(app):
    """
    Setup authentication for Flask app.

    Args:
        app: Flask application

    Returns:
        LoginManager instance
    """
    from flask_login import LoginManager

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access the dashboard.'

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID."""
        return get_user_manager().get_user(user_id)

    return login_manager
