from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base

class FounderBackground(PyEnum):
    WARRIOR = "warrior"           # +combat bonuses, facility efficiency
    MAGE = "mage"                # +magic bonuses, training efficiency
    ROGUE = "rogue"              # +stealth bonuses, recruitment efficiency  
    CLERIC = "cleric"            # +healing bonuses, reputation bonuses
    RANGER = "ranger"            # +ranged bonuses, gold bonuses

class Founder(Base):
    """Player's persistent character that carries between runs"""
    __tablename__ = "founders"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, unique=True)
    
    # Character Identity
    name = Column(String, nullable=False)
    title = Column(String, nullable=False)  # "Serial Entrepreneur", "Guild Architect"
    background = Column(Enum(FounderBackground), nullable=False)
    
    # Meta-Progression Stats (permanent upgrades)
    leadership_level = Column(Integer, default=1)     # Affects adventurer loyalty
    negotiation_level = Column(Integer, default=1)    # Better hiring costs
    vision_level = Column(Integer, default=1)         # Starting guild bonuses
    charisma_level = Column(Integer, default=1)       # Reputation gains
    expertise_level = Column(Integer, default=1)      # Training efficiency
    
    # Persistent Resources
    career_money = Column(Integer, default=0)         # Money earned from selling guilds
    lifetime_guilds_sold = Column(Integer, default=0) # Total runs completed
    
    # Achievement Unlocks
    unlocked_backgrounds = Column(JSON, default=list) # Available starting bonuses
    unlocked_titles = Column(JSON, default=list)      # Available titles
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="founder")
    game_runs = relationship("GameRun", back_populates="founder")