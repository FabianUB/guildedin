from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base

class CEOPersonalityType(PyEnum):
    AGGRESSIVE_TRADER = "aggressive_trader"        # High-risk dungeons for maximum stock impact
    CONSERVATIVE_BUILDER = "conservative_builder"  # Steady growth and facility upgrades
    SOCIAL_CLIMBER = "social_climber"             # Flashy moves for reputation and network effects
    ANALYTICAL_OPTIMIZER = "analytical_optimizer"  # Data-driven decisions, efficient allocation
    CHARISMATIC_LEADER = "charismatic_leader"     # Strong adventurer loyalty, great recruitment
    INNOVATION_PIONEER = "innovation_pioneer"      # Early adopter of new strategies and tech

class RiskTolerance(PyEnum):
    VERY_LOW = "very_low"      # 10-20% risk dungeons only
    LOW = "low"                # 20-40% risk dungeons
    MODERATE = "moderate"      # 40-60% risk dungeons
    HIGH = "high"              # 60-80% risk dungeons
    VERY_HIGH = "very_high"    # 80%+ risk dungeons

class CommunicationStyle(PyEnum):
    PROFESSIONAL = "professional"  # Formal business language
    CASUAL = "casual"              # Friendly, approachable tone
    BOASTFUL = "boastful"          # Bragging about achievements
    ANALYTICAL = "analytical"      # Data-heavy, technical posts
    INSPIRATIONAL = "inspirational" # Motivational, team-focused
    SARCASTIC = "sarcastic"        # Witty, sometimes cutting remarks

class BotCEOPersonality(Base):
    """AI personality profiles for bot guild CEOs"""
    __tablename__ = "bot_ceo_personalities"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Identity
    name = Column(String, nullable=False)
    title = Column(String, default="CEO")  # "CEO", "Founder", "Guild Master"
    bio = Column(Text)  # LinkedIn-style bio
    
    # Personality Type
    personality_type = Column(Enum(CEOPersonalityType), nullable=False)
    risk_tolerance = Column(Enum(RiskTolerance), nullable=False)
    communication_style = Column(Enum(CommunicationStyle), nullable=False)
    
    # Behavioral Traits (0-100 scale)
    ambition = Column(Integer, default=50)        # Drive for growth and success
    patience = Column(Integer, default=50)        # Willingness to wait for results
    ego = Column(Integer, default=50)             # Self-importance and pride
    loyalty = Column(Integer, default=50)         # Commitment to adventurers
    innovation = Column(Integer, default=50)      # Openness to new strategies
    competitiveness = Column(Integer, default=50) # Drive to beat other guilds
    
    # Strategic Preferences (0-100 scale)
    facility_investment_priority = Column(Integer, default=50)  # Focus on guild buildings
    recruitment_priority = Column(Integer, default=50)         # Focus on hiring talent
    training_priority = Column(Integer, default=50)            # Focus on developing adventurers
    dungeon_frequency = Column(Integer, default=50)            # How often to run dungeons
    
    # Market Behavior
    stock_volatility_comfort = Column(Integer, default=50)     # Tolerance for price swings
    competitive_response_speed = Column(Integer, default=50)   # React quickly to competitors
    market_timing_skill = Column(Integer, default=50)         # Ability to time market moves
    
    # Communication Patterns
    post_frequency = Column(Integer, default=3)               # Posts per week
    posts_about_success = Column(Integer, default=70)         # % posts celebrating wins
    posts_about_strategy = Column(Integer, default=20)        # % posts about plans
    posts_about_market = Column(Integer, default=10)          # % posts about market trends
    
    # Template phrases for post generation
    signature_phrases = Column(JSON, default=list)            # ["Synergy achieved!", "Next level!"]
    victory_templates = Column(JSON, default=list)            # Templates for success posts
    failure_templates = Column(JSON, default=list)            # Templates for setback posts
    strategy_templates = Column(JSON, default=list)           # Templates for planning posts
    
    # Visual Identity
    avatar_emoji = Column(String, default="👨‍💼")             # Profile picture emoji
    banner_color = Column(String, default="#3b82f6")          # Profile banner color
    
    # Performance History
    guilds_managed = Column(Integer, default=0)               # Total guilds run by this CEO
    average_guild_performance = Column(Integer, default=50)   # Historical success rate
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    current_guild = relationship("Guild", back_populates="bot_ceo", uselist=False)

# Add this relationship to Guild model (will need to be added separately)
# bot_ceo_id = Column(Integer, ForeignKey("bot_ceo_personalities.id"), nullable=True)
# bot_ceo = relationship("BotCEOPersonality", back_populates="current_guild")