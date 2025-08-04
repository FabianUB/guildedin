from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .user import Base

class Player(Base):
    """Real users who authenticate and manage their guild"""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Player Profile
    display_name = Column(String, nullable=False)
    
    # Game Progress
    player_level = Column(Integer, default=1)
    total_experience = Column(Integer, default=0)
    gold = Column(Integer, default=1000)  # Starting currency
    
    # Account Status  
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)  # Premium membership
    is_verified = Column(Boolean, default=False)  # Verified account
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    guild = relationship("Guild", back_populates="owner", uselist=False)
    dungeon_runs = relationship("DungeonRun", back_populates="player")
    activities = relationship("Activity", back_populates="player")
    game_runs = relationship("GameRun", back_populates="player")