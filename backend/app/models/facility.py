from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .user import Base

class FacilityType(PyEnum):
    TRAINING_ROOM = "training_room"       # Boost adventurer stat growth
    EQUIPMENT_STORAGE = "equipment_storage"  # Increase inventory capacity
    WELLNESS_CENTER = "wellness_center"   # Faster health/energy recovery
    NETWORKING_LOUNGE = "networking_lounge"  # Recruit higher quality adventurers
    STRATEGY_CENTER = "strategy_center"   # Better dungeon planning/bonuses
    INNOVATION_LAB = "innovation_lab"     # Craft/upgrade equipment
    CONFERENCE_ROOM = "conference_room"   # Team building and synergy bonuses

class Facility(Base):
    """Upgradeable guild buildings that provide passive bonuses"""
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    name = Column(String, nullable=False)  # "Executive Training Suite"
    description = Column(Text)  # What this facility does
    facility_type = Column(Enum(FacilityType), nullable=False)
    
    # Upgrade System
    max_level = Column(Integer, default=5)
    base_cost = Column(Integer, default=1000)  # Cost for level 1
    upgrade_cost_multiplier = Column(Integer, default=2)  # Cost increase per level
    
    # Effects (scale with level)
    base_effects = Column(JSON, default=dict)  # {"training_speed": 1.2, "stat_bonus": 1}
    level_scaling = Column(JSON, default=dict)  # {"training_speed": 0.1, "stat_bonus": 0.5}
    
    # Requirements
    required_guild_level = Column(Integer, default=1)
    prerequisites = Column(JSON, default=list)  # ["Basic Office", "10 Adventurers"]
    
    # Visual & Flavor
    icon_url = Column(String)  # Pixel art building icon
    flavor_text = Column(Text)  # Corporate description
    linkedin_equivalent = Column(String)  # "Like having a premium office space"
    
    # Metadata
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    guild_facilities = relationship("GuildFacility", back_populates="facility")

class GuildFacility(Base):
    """Join table tracking which facilities each guild has and their levels"""
    __tablename__ = "guild_facilities"

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=False)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    
    # Facility Status
    current_level = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    # Economics
    total_invested = Column(Integer, default=0)  # Total gold spent on this facility
    maintenance_due = Column(DateTime(timezone=True))  # When next maintenance payment is due
    
    # Usage Stats
    times_used = Column(Integer, default=0)
    total_benefit_provided = Column(Integer, default=0)  # Cumulative benefit metric
    
    # Timestamps
    built_at = Column(DateTime(timezone=True), server_default=func.now())
    last_upgraded = Column(DateTime(timezone=True))
    
    # Relationships
    guild = relationship("Guild", back_populates="facilities")
    facility = relationship("Facility", back_populates="guild_facilities")