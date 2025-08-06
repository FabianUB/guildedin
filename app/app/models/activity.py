from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base

class ActivityType(PyEnum):
    DUNGEON_COMPLETION = "dungeon_completion"    # "Completed Q4 Review Dungeon!"
    ADVENTURER_RECRUITMENT = "adventurer_recruitment"  # "Welcomed Sarah (HR Manager) to the team!"
    LEVEL_UP = "level_up"                       # "Congratulations to Mike for reaching Level 15!"
    EQUIPMENT_ACQUIRED = "equipment_acquired"    # "The team earned Premium Slack License!"
    FACILITY_UPGRADE = "facility_upgrade"       # "Upgraded our Training Room to Level 3!"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"  # "Unlocked 'Team Player' achievement!"
    GUILD_MILESTONE = "guild_milestone"         # "Our guild reached 25 members!"
    DAILY_REFLECTION = "daily_reflection"       # Bot-generated motivational posts
    ENDORSEMENT = "endorsement"                 # "Endorsed Alex for Crisis Management skills"
    CONNECTION_MADE = "connection_made"         # "Connected with other guilds in the network"

class Activity(Base):
    """LinkedIn-style activity feed posts showing guild and adventurer achievements"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    activity_type = Column(Enum(ActivityType), nullable=False)
    title = Column(String, nullable=False)  # "🎉 Dungeon Completed!"
    content = Column(Text, nullable=False)  # Main post content
    
    # Source & Attribution
    player_id = Column(Integer, ForeignKey("players.id"), nullable=True)  # Can be null for system posts
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=True)
    adventurer_id = Column(Integer, ForeignKey("adventurers.id"), nullable=True)  # If about specific adventurer
    
    # LinkedIn-style Metadata
    author_name = Column(String)  # "AdventureCorp Guild" or "Sarah (HR Manager)"
    author_title = Column(String)  # "Senior Guild Manager" or "Level 15 HR Manager"
    author_avatar = Column(String)  # Profile picture URL
    
    # Post Content & Media
    summary = Column(String)  # Short description for feed previews
    media_urls = Column(JSON, default=list)  # Screenshots, achievement badges, etc.
    hashtags = Column(JSON, default=list)  # ["#TeamWork", "#Achievement", "#GuildLife"]
    
    # Engagement Metrics (LinkedIn parody)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    # Activity Context
    related_dungeon_run_id = Column(Integer, ForeignKey("dungeon_runs.id"), nullable=True)
    related_equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)
    related_facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=True)
    
    # Post Metadata
    is_system_generated = Column(Boolean, default=True)  # Most posts are auto-generated
    is_pinned = Column(Boolean, default=False)  # Pin important achievements
    is_public = Column(Boolean, default=True)   # Visible to other players
    
    # Corporate Speak Elements
    corporate_template = Column(String)  # Template used for generation
    motivational_quote = Column(String)  # Random corporate wisdom
    industry_buzzwords = Column(JSON, default=list)  # ["synergy", "leverage", "streamline"]
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="activities")
    guild = relationship("Guild", back_populates="activities")
    adventurer = relationship("Adventurer")
    dungeon_run = relationship("DungeonRun")
    comments = relationship("ActivityComment", back_populates="activity")

class ActivityComment(Base):
    """LinkedIn-style comments on activity posts"""
    __tablename__ = "activity_comments"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    
    # Comment Author (can be players or bots)
    author_type = Column(String, default="bot")  # "player" or "bot"
    author_id = Column(Integer)  # Player ID or Adventurer ID depending on type
    author_name = Column(String, nullable=False)
    author_avatar = Column(String)
    
    # Comment Content
    content = Column(Text, nullable=False)
    is_system_generated = Column(Boolean, default=True)
    
    # Engagement
    likes_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    activity = relationship("Activity", back_populates="comments")