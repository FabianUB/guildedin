from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .user import Base

class EquipmentType(PyEnum):
    CERTIFICATION = "certification"      # Professional certifications
    SOFTWARE_LICENSE = "software_license"  # Tools and software
    NETWORKING_TOOL = "networking_tool"  # Personal brand boosters
    PRODUCTIVITY_SUITE = "productivity_suite"  # Workflow optimization
    LEADERSHIP_BADGE = "leadership_badge"  # Authority symbols
    WELLNESS_PERK = "wellness_perk"     # Health and bandwidth boosters

class EquipmentRarity(PyEnum):
    COMMON = "common"           # Basic corporate tools
    UNCOMMON = "uncommon"       # Decent professional gear
    RARE = "rare"              # Premium certifications
    EPIC = "epic"              # Executive-level equipment
    LEGENDARY = "legendary"     # C-Suite exclusive items

class Equipment(Base):
    """Corporate tools, certifications, and perks that boost adventurer stats"""
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    name = Column(String, nullable=False)  # "PMP Certification", "Slack Premium License"
    description = Column(Text)  # What this equipment does
    equipment_type = Column(Enum(EquipmentType), nullable=False)
    rarity = Column(Enum(EquipmentRarity), default=EquipmentRarity.COMMON)
    
    # Stat Bonuses (JSON for flexibility)
    stat_bonuses = Column(JSON, default=dict)  # {"personal_brand": 5, "optics": 3}
    special_effects = Column(JSON, default=list)  # ["Immunity to Monday Blues", "+20% Meeting Efficiency"]
    
    # Requirements
    required_level = Column(Integer, default=1)
    required_corporate_class = Column(String)  # Null = any class can use
    prerequisites = Column(JSON, default=list)  # ["Basic Certification", "5 Years Experience"]
    
    # Economic Info
    base_cost = Column(Integer, default=100)  # Purchase/upgrade cost
    market_value = Column(Integer, default=50)  # Sell value
    maintenance_cost = Column(Integer, default=0)  # Ongoing cost per day/week
    
    # Visual & Flavor
    icon_url = Column(String)  # Pixel art icon
    flavor_text = Column(Text)  # Funny corporate description
    linkedin_equivalent = Column(String)  # "This is like having 500+ connections"
    
    # Drop Info (for dungeon loot)
    drop_chance = Column(Integer, default=5)  # Percentage chance to drop
    dropped_from = Column(JSON, default=list)  # List of dungeon IDs where this can drop
    
    # Metadata
    is_active = Column(Boolean, default=True)
    is_premium_only = Column(Boolean, default=False)  # Premium members only
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    equipped_by = relationship("AdventurerEquipment", back_populates="equipment")

class AdventurerEquipment(Base):
    """Join table tracking which adventurers have which equipment equipped"""
    __tablename__ = "adventurer_equipment"

    id = Column(Integer, primary_key=True, index=True)
    adventurer_id = Column(Integer, ForeignKey("adventurers.id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    
    # Equipment Details
    is_equipped = Column(Boolean, default=True)  # Equipped vs in inventory
    upgrade_level = Column(Integer, default=0)   # +1, +2, etc.
    acquired_from = Column(String)  # "Dungeon Drop", "Shop Purchase", "Reward"
    
    # Timestamps
    acquired_at = Column(DateTime(timezone=True), server_default=func.now())
    equipped_at = Column(DateTime(timezone=True))
    
    # Relationships
    adventurer = relationship("Adventurer", back_populates="equipped_items")
    equipment = relationship("Equipment", back_populates="equipped_by")