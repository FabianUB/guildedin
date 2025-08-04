from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .user import Base

class CorporateClass(PyEnum):
    HR_MANAGER = "hr_manager"                    # Summoner
    CONFLICT_STRATEGIST = "conflict_strategist"  # Fighter  
    ETHICS_OFFICER = "ethics_officer"            # Paladin
    PR_MANAGER = "pr_manager"                    # Bard
    SUSTAINABILITY_OFFICER = "sustainability_officer"  # Druid
    ASSET_MANAGER = "asset_manager"              # Rogue/Thief
    WELLNESS_COORDINATOR = "wellness_coordinator"  # Healer
    STAKEHOLDER_MANAGER = "stakeholder_manager"  # Warlock
    INNOVATION_DIRECTOR = "innovation_director"  # Artificer
    PERFORMANCE_COACH = "performance_coach"      # Monk

class AdventurerRarity(PyEnum):
    INTERN = "intern"           # Common - low stats
    ASSOCIATE = "associate"     # Uncommon - decent stats  
    SENIOR = "senior"          # Rare - good stats
    PRINCIPAL = "principal"    # Epic - great stats
    EXECUTIVE = "executive"    # Legendary - amazing stats

class Adventurer(Base):
    """Bot characters that players recruit and manage"""
    __tablename__ = "adventurers"

    id = Column(Integer, primary_key=True, index=True)
    
    # LinkedIn-style Profile Info
    display_name = Column(String, nullable=False)
    corporate_class = Column(Enum(CorporateClass), nullable=False)
    rarity = Column(Enum(AdventurerRarity), default=AdventurerRarity.ASSOCIATE)
    
    # Professional LinkedIn Info (Parody)
    current_position = Column(String)  # "Senior Stakeholder Manager at MegaCorp"
    professional_summary = Column(Text)  # LinkedIn About section parody
    location = Column(String)
    industry_experience = Column(Integer, default=1)  # Years of "experience"
    
    # RPG Stats (Corporate Competencies)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    
    # Corporate RPG Stats (LinkedIn Skills Parody)
    personal_brand = Column(Integer, default=10)      # Charisma - networking power
    bandwidth = Column(Integer, default=10)           # Constitution - workload capacity
    synergy = Column(Integer, default=10)             # Strength - team performance
    growth_mindset = Column(Integer, default=10)      # Intelligence - learning agility
    agility = Column(Integer, default=10)             # Dexterity - adapting to change
    optics = Column(Integer, default=10)              # Wisdom - perception management
    
    # Derived Combat Stats (calculated from base stats)
    max_health = Column(Integer, default=100)
    current_health = Column(Integer, default=100)
    max_energy = Column(Integer, default=50)
    current_energy = Column(Integer, default=50)
    
    # Professional Skills & Certifications
    core_competencies = Column(JSON, default=dict)  # {"agile_methodology": 85, "client_relations": 70}
    certifications = Column(JSON, default=list)     # ["PMP Certified", "Six Sigma Black Belt"]
    career_achievements = Column(JSON, default=list) # ["Employee of the Month", "Process Optimizer"]
    
    # Visual Customization
    headshot_url = Column(String)  # Pixel art portrait
    banner_color = Column(String, default="#8B5CF6")  # Profile banner color
    
    # Bot Behavior & Personality
    personality_traits = Column(JSON, default=list)  # ["Ambitious", "Detail-oriented", "Team Player"]
    linkedin_style_posts = Column(JSON, default=list)  # Sample posts this bot would make
    
    # Recruitment & Status
    is_available = Column(Boolean, default=True)     # Available for recruitment
    hire_cost = Column(Integer, default=500)         # Cost to recruit
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=True)  # Null if not recruited
    
    # Training & Development
    training_points = Column(Integer, default=0)     # Points available for stat increases
    last_trained = Column(DateTime(timezone=True))   # Cooldown for training
    
    # Performance Metrics
    dungeons_completed = Column(Integer, default=0)
    total_damage_dealt = Column(Integer, default=0)
    total_healing_done = Column(Integer, default=0)
    team_synergy_bonus = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True))    # For "LinkedIn activity"
    
    # Relationships
    guild = relationship("Guild", back_populates="adventurers")
    equipped_items = relationship("AdventurerEquipment", back_populates="adventurer")
    dungeon_participations = relationship("DungeonParticipant", back_populates="adventurer")