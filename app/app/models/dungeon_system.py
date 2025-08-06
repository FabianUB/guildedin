from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base

class DungeonRank(PyEnum):
    E = "E"  # Entry level dungeons
    D = "D"  # Basic dungeons
    C = "C"  # Intermediate dungeons
    B = "B"  # Advanced dungeons
    A = "A"  # Elite dungeons
    S = "S"  # Legendary dungeons

class DungeonStatus(PyEnum):
    DISCOVERED = "discovered"    # Just appeared, bidding open
    BIDDING = "bidding"         # Active bidding phase
    ACTIVE = "active"           # Contracts awarded, dungeon accessible
    COLLAPSED = "collapsed"     # Time expired, dungeon closed
    COMPLETED = "completed"     # Boss defeated, dungeon cleared

class ContractStatus(PyEnum):
    PENDING = "pending"         # Bid submitted, awaiting results
    AWARDED = "awarded"         # Contract won, access granted
    REJECTED = "rejected"       # Bid lost to competitors
    CANCELLED = "cancelled"     # Bid withdrawn

class Dungeon(Base):
    """Session-isolated dungeon instances appearing in player's world"""
    __tablename__ = "dungeons"

    id = Column(Integer, primary_key=True, index=True)
    game_session_id = Column(Integer, ForeignKey("game_sessions.id"), nullable=False, index=True)  # SESSION ISOLATION
    
    # Basic Info
    name = Column(String, nullable=False)           # "Ancient Tokyo Ruins"
    description = Column(Text)                      # Flavor text
    difficulty_rank = Column(Enum(DungeonRank), nullable=False)
    
    # Location (Earth-based)
    location_name = Column(String, nullable=False)  # "Tokyo, Japan"
    latitude = Column(Float)                        # For map visualization
    longitude = Column(Float)
    region = Column(String)                         # "Asia-Pacific"
    
    # Dungeon Structure
    total_rooms = Column(Integer, nullable=False)   # Linear progression
    boss_room_number = Column(Integer, nullable=False) # Usually = total_rooms
    estimated_completion_time = Column(Integer)     # Hours needed to clear
    
    # Contract & Access
    max_guild_contracts = Column(Integer, default=1) # How many guilds can access
    current_contracts = Column(Integer, default=0)   # Current contracted guilds
    
    # Economic
    base_loot_value = Column(Integer, nullable=False) # Base gold/loot per room
    completion_bonus = Column(Integer, nullable=False) # Bonus for boss kill
    failure_penalty = Column(Integer, nullable=False)  # Penalty for collapse
    
    # Timing
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())
    bidding_closes_at = Column(DateTime(timezone=True), nullable=False)
    dungeon_closes_at = Column(DateTime(timezone=True), nullable=False) # Collapse deadline
    
    # Status
    status = Column(Enum(DungeonStatus), default=DungeonStatus.DISCOVERED)
    is_completed = Column(Boolean, default=False)
    completed_by_guild_id = Column(Integer, nullable=True) # Which guild killed boss
    
    # Metadata
    generation_seed = Column(String)                # For procedural content
    special_events = Column(JSON, default=list)    # Special conditions/events
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    game_session = relationship("GameSession", back_populates="dungeons")
    rooms = relationship("DungeonRoom", back_populates="dungeon", order_by="DungeonRoom.room_number")
    contracts = relationship("DungeonContract", back_populates="dungeon")
    runs = relationship("DungeonRun", back_populates="dungeon")

class DungeonRoom(Base):
    """Template for each room in a dungeon"""
    __tablename__ = "dungeon_rooms"

    id = Column(Integer, primary_key=True, index=True)
    
    # Room Position
    dungeon_id = Column(Integer, ForeignKey("dungeons.id"), nullable=False)
    room_number = Column(Integer, nullable=False)    # 1, 2, 3... (linear progression)
    
    # Room Details
    name = Column(String)                           # "Crystal Cavern", "Goblin Warren"
    description = Column(Text)                      # Room flavor text
    is_boss_room = Column(Boolean, default=False)
    
    # Combat
    enemy_configuration = Column(JSON, nullable=False) # Enemy types and numbers
    enemy_level_range = Column(JSON)                # [min_level, max_level]
    combat_difficulty = Column(Integer)             # 1-100 scale
    
    # Loot & Mining
    base_loot = Column(JSON, default=dict)          # {"gold": 500, "exp": 200}
    mining_resources = Column(JSON, default=dict)   # {"iron_ore": 50, "gems": 10}
    mining_duration_hours = Column(Integer, default=4) # How long to fully mine
    
    # Special Properties
    room_effects = Column(JSON, default=list)       # Environmental effects
    required_abilities = Column(JSON, default=list) # Special requirements
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    dungeon = relationship("Dungeon", back_populates="rooms")
    room_states = relationship("RoomProgress", back_populates="room")

class DungeonContract(Base):
    """Guild access rights to dungeons through bidding"""
    __tablename__ = "dungeon_contracts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Contract Details
    dungeon_id = Column(Integer, ForeignKey("dungeons.id"), nullable=False)
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=True)      # For player guilds
    bot_guild_id = Column(Integer, ForeignKey("bot_guilds.id"), nullable=True)  # For bot guilds
    
    # Bidding
    bid_amount = Column(Integer, nullable=False)     # Gold bid for access
    bid_submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Contract Status
    status = Column(Enum(ContractStatus), default=ContractStatus.PENDING)
    awarded_at = Column(DateTime(timezone=True), nullable=True)
    contract_value = Column(Integer, nullable=True)  # Final amount paid
    
    # Access Terms
    daily_time_limit = Column(Integer, default=8)   # Hours per day (real time)
    access_expires_at = Column(DateTime(timezone=True)) # When access ends
    
    # Performance Tracking
    completion_bonus_eligible = Column(Boolean, default=True)
    penalty_applied = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dungeon = relationship("Dungeon", back_populates="contracts")
    guild = relationship("Guild")  # For player guilds
    bot_guild = relationship("BotGuild", back_populates="dungeon_contracts")  # For bot guilds
    runs = relationship("DungeonRun", back_populates="contract")