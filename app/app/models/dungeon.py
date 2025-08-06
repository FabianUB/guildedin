from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base

class DungeonDifficulty(PyEnum):
    ENTRY_LEVEL = "entry_level"     # Easy dungeons for new teams
    MID_LEVEL = "mid_level"         # Standard difficulty
    SENIOR_LEVEL = "senior_level"   # Hard dungeons requiring good teams
    EXECUTIVE = "executive"         # Very hard dungeons
    C_SUITE = "c_suite"            # Endgame content

class DungeonType(PyEnum):
    CLIENT_MEETING = "client_meeting"           # Social encounters, high Personal Brand req
    QUARTERLY_REVIEW = "quarterly_review"      # Performance evaluation, balanced stats
    CRISIS_MANAGEMENT = "crisis_management"    # High pressure, Optics + Agility focus
    TEAM_BUILDING = "team_building"           # Synergy and Bandwidth focus  
    INNOVATION_SPRINT = "innovation_sprint"    # Growth Mindset heavy
    STAKEHOLDER_NEGOTIATION = "stakeholder_negotiation"  # Complex multi-phase encounter

class Dungeon(Base):
    """Quest content that teams can tackle"""
    __tablename__ = "dungeons"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    name = Column(String, nullable=False)  # "Q4 Performance Review Dungeon"
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)  # "Navigate the treacherous waters of quarterly metrics..."
    
    # Dungeon Classification
    difficulty = Column(Enum(DungeonDifficulty), nullable=False)
    dungeon_type = Column(Enum(DungeonType), nullable=False)
    recommended_level = Column(Integer, default=1)
    max_team_size = Column(Integer, default=4)
    min_team_size = Column(Integer, default=1)
    
    # Requirements & Unlocks
    required_guild_level = Column(Integer, default=1)
    unlock_conditions = Column(JSON, default=dict)  # {"completed_dungeons": ["dungeon_1"], "gold_spent": 1000}
    
    # Rewards
    base_experience_reward = Column(Integer, default=100)
    base_gold_reward = Column(Integer, default=50)
    possible_loot = Column(JSON, default=list)  # List of equipment IDs that can drop
    first_clear_bonus = Column(JSON, default=dict)  # {"experience": 500, "gold": 200}
    
    # Dungeon Mechanics
    stat_requirements = Column(JSON, default=dict)  # {"personal_brand": 25, "optics": 30}
    phases = Column(JSON, default=list)  # [{"name": "Opening Remarks", "mechanics": [...]}]
    special_mechanics = Column(JSON, default=list)  # Unique dungeon features
    
    # Visual & Flavor
    background_image = Column(String)  # Pixel art background
    ambient_music = Column(String)     # Background music file
    corporate_setting = Column(String)  # "Conference Room", "Open Office", "Executive Boardroom"
    
    # Metadata
    estimated_duration = Column(Integer, default=5)  # Minutes
    is_active = Column(Boolean, default=True)
    is_daily_special = Column(Boolean, default=False)  # Rotating daily dungeon
    
    # Stats
    total_attempts = Column(Integer, default=0)
    total_completions = Column(Integer, default=0)
    average_completion_time = Column(Integer, default=0)  # Seconds
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    runs = relationship("DungeonRun", back_populates="dungeon")

class DungeonRun(Base):
    """Record of a team's attempt at a dungeon"""
    __tablename__ = "dungeon_runs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    dungeon_id = Column(Integer, ForeignKey("dungeons.id"), nullable=False)
    
    # Team Composition (stored as JSON for flexibility)
    team_composition = Column(JSON, nullable=False)  # [{"adventurer_id": 1, "position": "leader"}, ...]
    team_level_average = Column(Integer)  # Calculated average level
    
    # Run Results
    is_completed = Column(Boolean, default=False)
    completion_time = Column(Integer)  # Seconds taken
    final_score = Column(Integer, default=0)  # Performance rating
    
    # Rewards Earned
    experience_gained = Column(Integer, default=0)
    gold_earned = Column(Integer, default=0)
    loot_received = Column(JSON, default=list)  # [{"equipment_id": 1, "quantity": 1}]
    
    # Performance Metrics
    damage_dealt = Column(Integer, default=0)
    healing_done = Column(Integer, default=0)
    synergy_bonus = Column(Integer, default=0)
    critical_successes = Column(Integer, default=0)
    
    # Run Log & Analysis
    combat_log = Column(JSON, default=list)  # Detailed log of what happened
    performance_breakdown = Column(JSON, default=dict)  # Per-adventurer stats
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    player = relationship("Player", back_populates="dungeon_runs")
    dungeon = relationship("Dungeon", back_populates="runs")
    participants = relationship("DungeonParticipant", back_populates="dungeon_run")

class DungeonParticipant(Base):
    """Join table tracking which adventurers participated in each run"""
    __tablename__ = "dungeon_participants"

    id = Column(Integer, primary_key=True, index=True)
    dungeon_run_id = Column(Integer, ForeignKey("dungeon_runs.id"), nullable=False)
    adventurer_id = Column(Integer, ForeignKey("adventurers.id"), nullable=False)
    
    # Participation Details
    position = Column(String)  # "leader", "support", "specialist"
    experience_gained = Column(Integer, default=0)
    damage_dealt = Column(Integer, default=0)
    healing_done = Column(Integer, default=0)
    performance_rating = Column(Integer, default=0)  # 1-10 rating
    
    # Relationships
    dungeon_run = relationship("DungeonRun", back_populates="participants")
    adventurer = relationship("Adventurer", back_populates="dungeon_participations")