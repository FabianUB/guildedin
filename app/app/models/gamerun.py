from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base

class GameRunStatus(PyEnum):
    ACTIVE = "active"           # Currently playing
    WON = "won"                # Reached target money and sold guild
    LOST_BANKRUPT = "lost_bankrupt"    # Ran out of money
    ABANDONED = "abandoned"     # Player quit mid-run

class DifficultyLevel(PyEnum):
    INTERN = "intern"           # Easy mode - lower costs, higher rewards
    ASSOCIATE = "associate"     # Normal mode
    SENIOR = "senior"          # Hard mode - higher costs, same rewards
    EXECUTIVE = "executive"     # Very hard mode - much higher costs

class GameRun(Base):
    """Individual playthrough of the guild management game"""
    __tablename__ = "game_runs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Run Ownership
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=False)
    founder_id = Column(Integer, ForeignKey("founders.id"), nullable=False)
    
    # Run Configuration
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.ASSOCIATE)
    target_money = Column(Integer, default=100000)  # Money needed to win
    starting_money = Column(Integer, default=10000)  # Starting capital
    
    # Current Game State
    current_day = Column(Integer, default=1)
    current_money = Column(Integer)  # Will be set to starting_money on creation
    status = Column(Enum(GameRunStatus), default=GameRunStatus.ACTIVE)
    
    # Daily Costs (configurable based on difficulty)
    base_daily_costs = Column(JSON, default=dict)  # {"facility_maintenance": 100, "guild_overhead": 50}
    adventurer_daily_salary = Column(Integer, default=50)  # Per adventurer per day
    
    # Performance Tracking
    total_dungeons_completed = Column(Integer, default=0)
    total_income_generated = Column(Integer, default=0)
    total_expenses_paid = Column(Integer, default=0)
    peak_money = Column(Integer, default=0)  # Highest money reached
    lowest_money = Column(Integer, default=0)  # Closest to bankruptcy
    
    # Win/Loss Details
    final_money = Column(Integer)  # Money when run ended
    days_survived = Column(Integer)  # How many days the run lasted
    end_reason = Column(String)  # "Bankruptcy on day 15", "Sold guild for 120k", "Abandoned"
    
    # Guild Selling (only for successful runs)
    guild_sold_for = Column(Integer)  # Final sale price (null if bankrupt/abandoned)
    guild_sale_date = Column(DateTime(timezone=True))
    
    # Founder Progression
    founder_bonuses_snapshot = Column(JSON, default=dict)  # Founder stats at run start
    career_money_earned = Column(Integer, default=0)  # Money added to founder's career_money
    
    # Run Statistics
    performance_metrics = Column(JSON, default=dict)  # Detailed stats
    major_events = Column(JSON, default=list)  # ["Day 5: Hired first Senior adventurer", ...]
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    last_played = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="game_runs")
    guild = relationship("Guild", back_populates="current_run")
    founder = relationship("Founder", back_populates="game_runs")
    daily_plans = relationship("DailyPlan", back_populates="game_run")
    daily_expenses = relationship("DailyExpense", back_populates="game_run")
    turn_summaries = relationship("TurnSummary", back_populates="game_run")