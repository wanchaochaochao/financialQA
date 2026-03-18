"""
CRUD Operations
===============

Database CRUD operations for users.
"""

from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from .models import User
from .auth import get_password_hash, verify_password


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Get user by ID.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User object or None
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_nickname(db: Session, nickname: str) -> Optional[User]:
    """
    Get user by nickname.

    Args:
        db: Database session
        nickname: User nickname

    Returns:
        User object or None
    """
    return db.query(User).filter(User.nickname == nickname).first()


def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
    """
    Get user by phone.

    Args:
        db: Database session
        phone: Phone number

    Returns:
        User object or None
    """
    return db.query(User).filter(User.phone == phone).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get user by email.

    Args:
        db: Database session
        email: Email address

    Returns:
        User object or None
    """
    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session,
    nickname: str,
    password: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
) -> User:
    """
    Create a new user.

    Args:
        db: Database session
        nickname: User nickname
        password: Plain text password
        phone: Phone number (optional)
        email: Email address (optional)

    Returns:
        Created user object
    """
    password_hash = get_password_hash(password)
    db_user = User(
        nickname=nickname,
        password_hash=password_hash,
        phone=phone,
        email=email,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, nickname: str, password: str) -> Optional[User]:
    """
    Authenticate user by nickname and password.

    Args:
        db: Database session
        nickname: User nickname
        password: Plain text password

    Returns:
        User object if authenticated, None otherwise
    """
    user = get_user_by_nickname(db, nickname)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.status:
        return None  # User is disabled
    return user


def update_last_login(db: Session, user_id: int) -> None:
    """
    Update user's last login time.

    Args:
        db: Database session
        user_id: User ID
    """
    user = get_user_by_id(db, user_id)
    if user:
        user.last_login = datetime.utcnow()
        db.commit()


def is_vip_active(user: User) -> bool:
    """
    Check if user's VIP is active.

    Args:
        user: User object

    Returns:
        True if VIP is active, False otherwise
    """
    if user.vip_level == 0:
        return False
    if user.vip_expire is None:
        return False
    return user.vip_expire > datetime.utcnow()
