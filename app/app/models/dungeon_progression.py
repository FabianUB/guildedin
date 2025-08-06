from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base

class RunStatus(PyEnum):
    PREPARING = "preparing"     # Guild has access but hasn't entered
    ACTIVE = "active"          # Currently in dungeon
    SUSPENDED = "suspended"    # Paused, can resume
    COMPLETED = "completed"    # Boss defeated
    FAILED = "failed"          # Collapsed or party defeated
    ABANDONED = "abandoned"    # Guild gave up

class RoomState(PyEnum):
    UNEXPLORED = "unexplored"  # Haven't reached this room yet
    COMBAT = "combat"          # Currently fighting enemies
    CLEARED = "cleared"        # Enemies defeated, room available
    MINING = "mining"          # Miners extracting resources
    EXHAUSTED = "exhausted"    # All resources extracted

class DungeonRun(Base):
    """Individual guild expedition through a dungeon"""
    __tablename__ = "dungeon_runs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Run Identity
    dungeon_id = Column(Integer, ForeignKey("dungeons.id"), nullable=False)
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=False)
    contract_id = Column(Integer, ForeignKey("dungeon_contracts.id"), nullable=False)
    
    # Progression
    current_room = Column(Integer, default=0)       # 0 = at entrance, 1+ = in rooms
    furthest_room_reached = Column(Integer, default=0)
    status = Column(Enum(RunStatus), default=RunStatus.PREPARING)
    
    # Time Management (Real Time)
    total_time_used = Column(Integer, default=0)    # Minutes used in dungeon
    time_limit_per_day = Column(Integer, default=480) # 8 hours = 480 minutes
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Daily Time Tracking
    today_time_used = Column(Integer, default=0)    # Minutes used today
    last_reset_date = Column(DateTime(timezone=True)) # When daily timer reset
    
    # Party Composition
    party_adventurers = Column(JSON, default=list)  # [adventurer_ids] in dungeon
    party_size = Column(Integer, default=0)
    
    # Performance Metrics
    total_loot_gained = Column(JSON, default=dict)  # {"gold": 1500, "exp": 800}
    rooms_cleared = Column(Integer, default=0)
    enemies_defeated = Column(Integer, default=0)
    mining_operations = Column(Integer, default=0)
    
    # Run Outcome
    completion_bonus_earned = Column(Integer, default=0)
    failure_penalty_paid = Column(Integer, default=0)
    boss_defeated = Column(Boolean, default=False)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dungeon = relationship("Dungeon", back_populates="runs")
    guild = relationship("Guild")
    contract = relationship("DungeonContract", back_populates="runs")
    room_progress = relationship("RoomProgress", back_populates="run")
    battles = relationship("DungeonBattle", back_populates="run")
    mining_ops = relationship("MiningOperation", back_populates="run")

class RoomProgress(Base):
    """Per-guild state for each room in dungeon"""
    __tablename__ = "room_progress"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiers
    run_id = Column(Integer, ForeignKey("dungeon_runs.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("dungeon_rooms.id"), nullable=False)
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=False) # For easy queries
    
    # Room State
    state = Column(Enum(RoomState), default=RoomState.UNEXPLORED)
    
    # Combat Results
    combat_completed = Column(Boolean, default=False)
    combat_result = Column(String, nullable=True)    # "victory", "defeat", "retreat"
    enemies_remaining = Column(JSON, default=list)   # Enemies still alive
    
    # Loot & Resources
    loot_collected = Column(JSON, default=dict)      # Immediate combat loot
    resources_mined = Column(JSON, default=dict)     # Resources extracted by miners
    mining_completion_percent = Column(Float, default=0.0) # 0.0 to 100.0
    
    # Timing
    first_entered_at = Column(DateTime(timezone=True), nullable=True)
    combat_completed_at = Column(DateTime(timezone=True), nullable=True)
    mining_started_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    run = relationship("DungeonRun", back_populates="room_progress")
    room = relationship("DungeonRoom", back_populates="room_states")
    mining_operation = relationship("MiningOperation", back_populates="room_progress", uselist=False)

class MiningOperation(Base):
    """Background mining in cleared rooms"""
    __tablename__ = "mining_operations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Operation Identity
    run_id = Column(Integer, ForeignKey("dungeon_runs.id"), nullable=False)
    room_progress_id = Column(Integer, ForeignKey("room_progress.id"), nullable=False)
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=False)
    
    # Mining Details
    miners_assigned = Column(Integer, default=1)     # Number of temporary miners
    mining_efficiency = Column(Float, default=1.0)   # Multiplier based on guild upgrades
    
    # Progress Tracking
    total_duration_hours = Column(Integer, nullable=False) # How long to complete
    hours_completed = Column(Float, default=0.0)     # Progress so far
    completion_percentage = Column(Float, default=0.0)
    
    # Resource Yield
    target_resources = Column(JSON, nullable=False)  # What can be mined
    resources_extracted = Column(JSON, default=dict) # What has been mined
    estimated_value = Column(Integer, default=0)     # Total value when complete
    
    # Status
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Timing (Real Time)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_update = Column(DateTime(timezone=True), server_default=func.now())
    estimated_completion = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    run = relationship("DungeonRun", back_populates="mining_ops")
    room_progress = relationship("RoomProgress", back_populates="mining_operation")
    guild = relationship("Guild")

class DungeonBattle(Base):
    """Combat results for each room battle"""
    __tablename__ = "dungeon_battles"

    id = Column(Integer, primary_key=True, index=True)
    
    # Battle Context
    run_id = Column(Integer, ForeignKey("dungeon_runs.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("dungeon_rooms.id"), nullable=False)
    room_number = Column(Integer, nullable=False)
    
    # Participants
    participating_adventurers = Column(JSON, nullable=False) # Adventurer IDs and stats
    enemy_configuration = Column(JSON, nullable=False)      # Enemy types and numbers
    
    # Battle Results
    result = Column(String, nullable=False)              # "victory", "defeat", "retreat"
    battle_duration_minutes = Column(Integer, default=0)
    
    # Performance Metrics
    damage_dealt = Column(Integer, default=0)
    damage_taken = Column(Integer, default=0)
    adventurers_defeated = Column(JSON, default=list)   # IDs of defeated adventurers
    enemies_defeated = Column(JSON, default=list)       # Enemy types defeated
    
    # Rewards
    exp_gained = Column(Integer, default=0)
    loot_gained = Column(JSON, default=dict)            # {"gold": 300, "items": [...]}
    
    # Battle Log (for future auto-battler display)
    battle_log = Column(JSON, default=list)             # Turn-by-turn results
    
    # Timestamps
    battle_started_at = Column(DateTime(timezone=True), server_default=func.now())
    battle_ended_at = Column(DateTime(timezone=True))
    
    # Relationships
    run = relationship("DungeonRun", back_populates="battles")
    room = relationship("DungeonRoom")