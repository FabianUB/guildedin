from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base

class AdventurerClass(PyEnum):
    FIGHTER = "fighter"         # Melee combat specialist
    ROGUE = "rogue"            # Stealth and infiltration
    MAGE = "mage"              # Arcane magic user
    CLERIC = "cleric"          # Divine magic and healing
    ARCHER = "archer"          # Ranged combat specialist
    PALADIN = "paladin"        # Holy warrior and tank
    BARBARIAN = "barbarian"    # Berserker damage dealer
    BARD = "bard"              # Support and party buffs
    DRUID = "druid"            # Nature magic and shapeshifting
    MONK = "monk"              # Martial arts and mobility

class AdventurerRarity(PyEnum):
    NOVICE = "novice"           # Common - low stats
    JOURNEYMAN = "journeyman"   # Uncommon - decent stats  
    EXPERT = "expert"          # Rare - good stats
    MASTER = "master"          # Epic - great stats
    LEGENDARY = "legendary"    # Legendary - amazing stats

class Adventurer(Base):
    """Bot characters that players recruit and manage"""
    __tablename__ = "adventurers"

    id = Column(Integer, primary_key=True, index=True)
    
    # LinkedIn-style Profile Info
    display_name = Column(String, nullable=False)
    adventurer_class = Column(Enum(AdventurerClass), nullable=False)
    rarity = Column(Enum(AdventurerRarity), default=AdventurerRarity.JOURNEYMAN)
    
    # Professional LinkedIn Info (Parody)
    current_position = Column(String)  # "Senior Stakeholder Manager at MegaCorp"
    professional_summary = Column(Text)  # LinkedIn About section parody
    location = Column(String)
    industry_experience = Column(Integer, default=1)  # Years of "experience"
    
    # RPG Stats (Corporate Competencies)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    
    # Fantasy RPG Stats (with some unique twists)
    strength = Column(Integer, default=10)       # Physical power and melee damage
    dexterity = Column(Integer, default=10)      # Agility and ranged accuracy
    constitution = Column(Integer, default=10)   # Health and endurance
    intelligence = Column(Integer, default=10)   # Magical power and spell damage
    synergy = Column(Integer, default=10)        # Team coordination and combo attacks
    optics = Column(Integer, default=10)         # Perception and situational awareness
    
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
    
    # EXP Distribution Tracking
    total_exp_received = Column(Integer, default=0)  # Total EXP distributed to this adventurer
    last_exp_distribution = Column(DateTime(timezone=True))  # When last received EXP
    
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