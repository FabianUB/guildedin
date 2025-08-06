from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, JSON, Boolean
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
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Professional RPG Profile
    display_name = Column(String, nullable=False)
    corporate_class = Column(Enum(CorporateClass), nullable=False)
    seniority_level = Column(Integer, default=1)  # Level 1-100
    career_experience = Column(Integer, default=0)  # XP points

    # LinkedIn-style Professional Info
    current_position = Column(String)  # "Senior Stakeholder Manager at AdventureCorp"
    professional_summary = Column(Text)  # LinkedIn About section
    location = Column(String)

    # Corporate RPG Stats (LinkedIn Skills Parody)
    personal_brand = Column(Integer, default=10)      # Charisma - networking power
    bandwidth = Column(Integer, default=10)           # Constitution - workload capacity
    synergy = Column(Integer, default=10)             # Strength - team performance
    growth_mindset = Column(Integer, default=10)      # Intelligence - learning agility
    agility = Column(Integer, default=10)             # Dexterity - adapting to change
    optics = Column(Integer, default=10)              # Wisdom - perception management

    # Professional Skills & Endorsements
    core_competencies = Column(JSON, default=dict)  # {"agile_methodology": 95, "client_relations": 78}
    professional_toolkit = Column(JSON, default=list)  # Equipment = Tools/Certifications
    career_achievements = Column(JSON, default=list)   # ["Q4 Top Performer", "Guild Founder"]

    # Profile customization
    headshot_url = Column(String)    # Professional headshot
    banner_color = Column(String, default="#8B5CF6")  # Fantasy purple default

    # Account status
    is_active = Column(Boolean, default=True)
    is_premium_member = Column(Boolean, default=False)  # LinkedIn Premium parody

    # Timestamps
    joined_network = Column(DateTime(timezone=True), server_default=func.now())
    profile_updated = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True))
    
    # Relationships
    game_sessions = relationship("GameSession", back_populates="player", cascade="all, delete-orphan")
    guild = relationship("Guild", back_populates="owner", uselist=False)