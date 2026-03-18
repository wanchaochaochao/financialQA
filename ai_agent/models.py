"""
Database Models
===============

SQLAlchemy models for the application.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime

from .database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=False)
    nickname = Column(String, unique=True, index=True, nullable=False)
    avatar = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    vip_level = Column(Integer, default=0)  # 0: 普通用户, 1-5: VIP等级
    vip_expire = Column(DateTime, nullable=True)
    status = Column(Boolean, default=True)  # True: 激活, False: 禁用
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, nickname='{self.nickname}', vip_level={self.vip_level})>"
