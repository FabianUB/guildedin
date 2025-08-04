from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .user import Base

class Guild(Base):
    """Player's managed company/guild with facilities and resources"""
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)  # URL-friendly name
    
    # Company/Guild Info (LinkedIn Company Page parody)
    tagline = Column(String)  # "Connecting top-tier adventurers since 2024"
    description = Column(Text)  # About the company/guild
    industry = Column(String)  # "Dungeon Consulting", "Quest Management"
    headquarters = Column(String)  # Location
    company_size = Column(String)  # "11-50 adventurers", "501-1000 employees"
    
    # Guild Stats & Metrics
    guild_level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    reputation_score = Column(Integer, default=0)
    total_dungeons_completed = Column(Integer, default=0)
    
    # Resources
    gold = Column(Integer, default=5000)  # Guild treasury
    influence_points = Column(Integer, default=0)  # Special currency for upgrades
    
    # Visual Customization
    logo_url = Column(String)
    banner_url = Column(String) 
    banner_color = Column(String, default="#6366F1")  # Fantasy indigo
    
    # Guild Culture & Values (LinkedIn company culture)
    core_values = Column(JSON, default=list)  # ["Innovation", "Teamwork", "Results-Driven"]
    perks_benefits = Column(JSON, default=list)  # ["Health Potions", "Flexible Quest Hours"]
    
    # Guild Ownership (one-to-one with Player)
    owner_id = Column(Integer, ForeignKey("players.id"), nullable=False, unique=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Verified company checkmark
    is_recruiting = Column(Boolean, default=True)  # Looking for adventurers
    
    # Timestamps
    founded_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("Player", back_populates="guild")
    adventurers = relationship("Adventurer", back_populates="guild")
    facilities = relationship("GuildFacility", back_populates="guild")
    activities = relationship("Activity", back_populates="guild")
    current_run = relationship("GameRun", back_populates="guild", uselist=False)