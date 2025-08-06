from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

from .database import Base
from .guild import GuildRank

class BotPersonalityType(PyEnum):
    AGGRESSIVE_TRADER = "aggressive_trader"      # High risk, high reward, volatile
    CONSERVATIVE_BUILDER = "conservative_builder" # Steady growth, facility focused
    NETWORKING_ELITE = "networking_elite"        # Premium deals, exclusive access
    DATA_ANALYST = "data_analyst"               # Market timing, calculated moves
    CHARISMATIC_LEADER = "charismatic_leader"   # High public engagement
    OPPORTUNISTIC_SHARK = "opportunistic_shark" # Exploits others' failures

class BotBehaviorState(PyEnum):
    GROWING = "growing"           # Investing and expanding
    CONSOLIDATING = "consolidating" # Stabilizing after growth
    AGGRESSIVE = "aggressive"     # Going all-in on opportunities  
    DEFENSIVE = "defensive"       # Playing it safe
    STRUGGLING = "struggling"     # Low on resources
    DOMINANT = "dominant"         # Market leader behavior

class BotGuild(Base):
    """
    AI-controlled competitor guilds that exist within a player's game session.
    Each has unique personality, behavior patterns, and market presence.
    """
    __tablename__ = "bot_guilds"
    
    id = Column(Integer, primary_key=True, index=True)
    game_session_id = Column(Integer, ForeignKey("game_sessions.id"), nullable=False, index=True)
    
    # Basic info
    name = Column(String(100), nullable=False)
    ceo_name = Column(String(100), nullable=False)
    ceo_title = Column(String(100), default="CEO")
    ceo_avatar_emoji = Column(String(10), default="👨‍💼")
    
    # Guild stats (mirrors player guild)
    gold = Column(Integer, default=5000)
    guild_rank = Column(Enum(GuildRank), default=GuildRank.D)
    share_price = Column(Float, default=100.0)
    exp_bank = Column(Integer, default=0)
    
    # Bot personality and behavior
    personality_type = Column(Enum(BotPersonalityType), nullable=False)
    current_behavior = Column(Enum(BotBehaviorState), default=BotBehaviorState.GROWING)
    aggression_level = Column(Float, default=0.5)  # 0.0 to 1.0
    risk_tolerance = Column(Float, default=0.5)    # 0.0 to 1.0  
    market_focus = Column(Float, default=0.5)      # 0.0 = facilities, 1.0 = dungeons
    
    # Performance tracking
    total_dungeons_completed = Column(Integer, default=0)
    total_revenue_earned = Column(Integer, default=0)
    consecutive_successful_days = Column(Integer, default=0)
    recent_performance_score = Column(Float, default=50.0)  # 0-100 scale
    
    # Dynamic state
    current_strategy = Column(String(50))  # e.g., "expanding_facilities", "dungeon_focus"
    last_major_decision = Column(String(200))  # For generating posts
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    
    # Market presence  
    post_frequency_days = Column(Integer, default=3)  # How often they post
    last_post_day = Column(Integer, default=0)
    public_reputation = Column(Float, default=50.0)   # 0-100 scale
    
    # AI decision making
    decision_weights = Column(JSON, default={
        "dungeon_bidding": 0.4,
        "facility_upgrade": 0.3, 
        "adventurer_training": 0.2,
        "market_manipulation": 0.1
    })
    
    # Session isolation
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships  
    game_session = relationship("GameSession", back_populates="bot_guilds")
    dungeon_contracts = relationship("DungeonContract", back_populates="bot_guild")
    market_activities = relationship("BotMarketActivity", back_populates="bot_guild")
    
    def __repr__(self):
        return f"<BotGuild(id={self.id}, name='{self.name}', session={self.game_session_id})>"
    
    @property
    def display_name(self):
        """Full display name for UI"""
        return f"{self.ceo_name} - CEO of {self.name}"
    
    @property
    def personality_description(self):
        """Human-readable personality description"""
        descriptions = {
            BotPersonalityType.AGGRESSIVE_TRADER: "High-risk market player, makes bold moves",
            BotPersonalityType.CONSERVATIVE_BUILDER: "Steady growth focused, builds strong foundations", 
            BotPersonalityType.NETWORKING_ELITE: "Well-connected, gets premium opportunities",
            BotPersonalityType.DATA_ANALYST: "Makes calculated, data-driven decisions",
            BotPersonalityType.CHARISMATIC_LEADER: "High public engagement, inspires confidence",
            BotPersonalityType.OPPORTUNISTIC_SHARK: "Exploits market weaknesses ruthlessly"
        }
        return descriptions.get(self.personality_type, "Unknown personality")
    
    def should_post_today(self, current_day: int) -> bool:
        """Determine if bot should make a LinkedIn-style post today"""
        return current_day - self.last_post_day >= self.post_frequency_days
    
    def calculate_dungeon_bid(self, dungeon_value: int, competition_level: int) -> int:
        """Calculate how much this bot would bid on a dungeon"""
        base_bid = dungeon_value * 0.6  # Conservative base
        
        # Personality adjustments
        if self.personality_type == BotPersonalityType.AGGRESSIVE_TRADER:
            base_bid *= (1.2 + self.risk_tolerance * 0.3)
        elif self.personality_type == BotPersonalityType.CONSERVATIVE_BUILDER:
            base_bid *= (0.8 + self.risk_tolerance * 0.2)
        elif self.personality_type == BotPersonalityType.NETWORKING_ELITE:
            base_bid *= 1.1  # Gets better deals through connections
            
        # Behavior state adjustments
        if self.current_behavior == BotBehaviorState.AGGRESSIVE:
            base_bid *= 1.3
        elif self.current_behavior == BotBehaviorState.DEFENSIVE:
            base_bid *= 0.7
            
        # Competition adjustment
        base_bid *= (1.0 + competition_level * 0.1)
        
        # Cap at available gold
        return min(int(base_bid), int(self.gold * 0.8))
    
    def update_performance_score(self, recent_success: bool):
        """Update performance based on recent activities"""
        if recent_success:
            self.recent_performance_score = min(100, self.recent_performance_score + 5)
            self.consecutive_successful_days += 1
        else:
            self.recent_performance_score = max(0, self.recent_performance_score - 3)
            self.consecutive_successful_days = 0
            
        # Update behavior based on performance
        if self.recent_performance_score > 80:
            self.current_behavior = BotBehaviorState.DOMINANT
        elif self.recent_performance_score > 60:
            self.current_behavior = BotBehaviorState.GROWING  
        elif self.recent_performance_score > 40:
            self.current_behavior = BotBehaviorState.CONSOLIDATING
        elif self.recent_performance_score > 20:
            self.current_behavior = BotBehaviorState.DEFENSIVE
        else:
            self.current_behavior = BotBehaviorState.STRUGGLING