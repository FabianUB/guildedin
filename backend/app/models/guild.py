from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .user import Base

class Guild(Base):
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
    member_count = Column(Integer, default=0)
    total_quests_completed = Column(Integer, default=0)
    guild_level = Column(Integer, default=1)
    reputation_score = Column(Integer, default=0)
    
    # Visual Customization
    logo_url = Column(String)
    banner_url = Column(String) 
    banner_color = Column(String, default="#6366F1")  # Fantasy indigo
    
    # Guild Culture & Values (LinkedIn company culture)
    core_values = Column(JSON, default=list)  # ["Innovation", "Teamwork", "Results-Driven"]
    perks_benefits = Column(JSON, default=list)  # ["Health Potions", "Flexible Quest Hours"]
    
    # Guild Leadership
    founder_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Verified company checkmark
    is_hiring = Column(Boolean, default=False)  # "We're hiring!" badge
    
    # Timestamps
    founded_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    founder = relationship("User", back_populates="founded_guilds")
    members = relationship("GuildMember", back_populates="guild")
    quests = relationship("Quest", back_populates="guild")