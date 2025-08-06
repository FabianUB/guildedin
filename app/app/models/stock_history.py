from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base

class PriceChangeReason(PyEnum):
    DUNGEON_SUCCESS = "dungeon_success"      # Successful dungeon completion
    DUNGEON_FAILURE = "dungeon_failure"      # Failed dungeon attempt
    NEW_RECRUITMENT = "new_recruitment"      # Hired high-quality adventurer
    FACILITY_UPGRADE = "facility_upgrade"    # Upgraded guild facilities
    MARKET_SENTIMENT = "market_sentiment"    # General market trends
    CEO_ANNOUNCEMENT = "ceo_announcement"    # Strategic announcement impact
    COMPETITIVE_ACTION = "competitive_action" # Response to competitor moves
    RANK_PROMOTION = "rank_promotion"        # Guild rank increased
    RANK_DEMOTION = "rank_demotion"          # Guild rank decreased
    EXTERNAL_EVENT = "external_event"        # Game-wide events affecting market

class StockPriceHistory(Base):
    """Historical tracking of guild stock price changes"""
    __tablename__ = "stock_price_history"

    id = Column(Integer, primary_key=True, index=True)
    
    # Guild Reference
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=False)
    
    # Price Data
    previous_price = Column(Float, nullable=False)
    new_price = Column(Float, nullable=False)
    price_change = Column(Float, nullable=False)      # Absolute change in gold
    price_change_percent = Column(Float, nullable=False) # Percentage change
    
    # Context
    reason = Column(Enum(PriceChangeReason), nullable=False)
    description = Column(Text, nullable=False)        # "Successful Ancient Ruins completion (+15%)"
    
    # Market Context
    market_volume = Column(Integer, default=0)        # Trading activity (shares)
    market_cap = Column(Float, nullable=False)        # shares_outstanding * new_price
    
    # Related Events
    dungeon_run_id = Column(Integer, nullable=True)   # If related to dungeon
    facility_id = Column(Integer, nullable=True)      # If related to facility upgrade
    adventurer_id = Column(Integer, nullable=True)    # If related to recruitment
    
    # Timestamps
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    guild = relationship("Guild", back_populates="stock_history")

class MarketEvent(Base):
    """Major market events affecting multiple guilds"""
    __tablename__ = "market_events"

    id = Column(Integer, primary_key=True, index=True)
    
    # Event Details
    event_type = Column(String, nullable=False)       # "DUNGEON_DIFFICULTY_INCREASE", "NEW_REGION_OPENED"
    title = Column(String, nullable=False)            # "Dragon's Lair Difficulty Surge"
    description = Column(Text, nullable=False)        # Full event description
    
    # Market Impact
    market_impact = Column(String, nullable=False)    # "NEGATIVE", "POSITIVE", "MIXED"
    affected_guild_types = Column(String)             # "HIGH_RISK", "ALL", "CONSERVATIVE"
    estimated_impact_percent = Column(Float)          # Expected market movement
    
    # Event Status
    is_active = Column(Boolean, default=True)
    affects_new_guilds = Column(Boolean, default=True)
    
    # Timestamps
    event_date = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Generated Content
    news_headline = Column(String)                    # For network activity feed
    ceo_talking_points = Column(JSON, default=list)   # Template responses for bot CEOs