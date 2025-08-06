from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base

class GuildRank(PyEnum):
    E = "E"  # 0-50 gold/share - New/struggling guilds
    D = "D"  # 51-100 gold/share - Developing guilds  
    C = "C"  # 101-200 gold/share - Established guilds
    B = "B"  # 201-400 gold/share - Successful guilds
    A = "A"  # 401-800 gold/share - Elite guilds
    S = "S"  # 800+ gold/share - Legendary guilds

class Guild(Base):
    """Player's managed company/guild with facilities and resources"""
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True, index=True)
    game_session_id = Column(Integer, ForeignKey("game_sessions.id"), nullable=False, index=True)  # SESSION ISOLATION
    name = Column(String, nullable=False)  # Removed unique constraint - unique per session instead
    slug = Column(String, nullable=False)  # URL-friendly name
    
    # Company/Guild Info (LinkedIn Company Page parody)
    tagline = Column(String)  # "Connecting top-tier adventurers since 2024"
    description = Column(Text)  # About the company/guild
    industry = Column(String)  # "Dungeon Consulting", "Quest Management"
    headquarters = Column(String)  # Location
    company_size = Column(String)  # "11-50 adventurers", "501-1000 employees"
    
    # Guild Stats & Metrics
    guild_level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    total_dungeons_completed = Column(Integer, default=0)
    
    # Stock Market System
    share_price = Column(Float, default=100.0)  # Starting price: 100 gold/share
    guild_rank = Column(Enum(GuildRank), default=GuildRank.D)
    shares_outstanding = Column(Integer, default=1000)  # Total shares for market cap calculation
    daily_price_change = Column(Float, default=0.0)  # Today's price change %
    weekly_price_change = Column(Float, default=0.0)  # 7-day price change %
    all_time_high = Column(Float, default=100.0)  # Highest share price achieved
    all_time_low = Column(Float, default=100.0)  # Lowest share price achieved
    last_price_update = Column(DateTime(timezone=True))  # When price was last updated
    
    # Resources
    gold = Column(Integer, default=5000)  # Guild treasury
    influence_points = Column(Integer, default=0)  # Special currency for upgrades
    
    # EXP Banking System
    exp_bank = Column(Integer, default=0)  # Unallocated EXP points from dungeons
    exp_reserved = Column(Integer, default=0)  # EXP earning interest
    exp_interest_rate = Column(Integer, default=5)  # 5% daily interest on reserved EXP
    last_interest_calculation = Column(DateTime(timezone=True))  # Track interest timing
    
    # Visual Customization
    logo_url = Column(String)
    banner_url = Column(String) 
    banner_color = Column(String, default="#6366F1")  # Fantasy indigo
    
    # Guild Culture & Values (LinkedIn company culture)
    core_values = Column(JSON, default=list)  # ["Innovation", "Teamwork", "Results-Driven"]
    perks_benefits = Column(JSON, default=list)  # ["Health Potions", "Flexible Quest Hours"]
    
    # Guild Ownership (one-to-one with Player OR Bot CEO)
    owner_id = Column(Integer, ForeignKey("players.id"), nullable=True, unique=True)  # Null for bot guilds
    bot_ceo_id = Column(Integer, ForeignKey("bot_ceo_personalities.id"), nullable=True, unique=True)  # Null for player guilds
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Verified company checkmark
    is_recruiting = Column(Boolean, default=True)  # Looking for adventurers
    
    # Timestamps
    founded_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    game_session = relationship("GameSession", back_populates="player_guild")
    owner = relationship("Player", back_populates="guild")
    bot_ceo = relationship("BotCEOPersonality", back_populates="current_guild", uselist=False)
    adventurers = relationship("Adventurer", back_populates="guild")
    facilities = relationship("GuildFacility", back_populates="guild")
    activities = relationship("Activity", back_populates="guild")
    current_run = relationship("GameRun", back_populates="guild", uselist=False)
    stock_history = relationship("StockPriceHistory", back_populates="guild")