from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base

class CorporateClass(PyEnum):
    HR_MANAGER = "hr_manager"                    # Discount on hiring and salaries
    PR_MANAGER = "pr_manager"                    # Easier to gain share price and reputation
    ASSET_MANAGER = "asset_manager"              # More interest on saved gold and exp
    WELLNESS_MANAGER = "wellness_manager"        # Adventurers have more HP and heal more

class Player(Base):
    """Basic player authentication and profile"""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    corporate_class = Column(Enum(CorporateClass), nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    game_session = relationship("GameSession", back_populates="player", uselist=False)
    guild = relationship("Guild", back_populates="owner", uselist=False)