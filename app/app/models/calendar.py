from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base

class DayType(PyEnum):
    WEEKDAY = "weekday"         # Normal working day
    WEEKEND = "weekend"         # Special weekend bonuses/events
    HOLIDAY = "holiday"         # Special holiday effects
    CRISIS = "crisis"          # Random negative events
    OPPORTUNITY = "opportunity"  # Random positive events

class ActionType(PyEnum):
    DUNGEON_EXPEDITION = "dungeon_expedition"    # Full day action
    RECRUIT_ADVENTURER = "recruit_adventurer"    # Partial action
    TRAIN_ADVENTURER = "train_adventurer"       # Partial action  
    UPGRADE_FACILITY = "upgrade_facility"       # Partial action
    GUILD_MANAGEMENT = "guild_management"       # Partial action
    REST_DAY = "rest_day"                      # Adventurer recovery
    MARKET_RESEARCH = "market_research"        # Unlock new dungeons/equipment

class ActionResult(PyEnum):
    SUCCESS = "success"         # Action completed successfully
    PARTIAL_SUCCESS = "partial_success"  # Some benefits gained
    FAILURE = "failure"         # Action failed, some costs still paid
    CRITICAL_SUCCESS = "critical_success"  # Exceptional results
    CRITICAL_FAILURE = "critical_failure"  # Disaster with extra consequences

class DailyPlan(Base):
    """What the player planned and executed on a specific day"""
    __tablename__ = "daily_plans"

    id = Column(Integer, primary_key=True, index=True)
    
    # Context
    game_run_id = Column(Integer, ForeignKey("game_runs.id"), nullable=False)
    day_number = Column(Integer, nullable=False)  # Day 1, 2, 3, etc.
    
    # Day Classification
    day_type = Column(Enum(DayType), default=DayType.WEEKDAY)
    special_event = Column(String)  # "Market Crash", "Industry Conference", etc.
    weather_effect = Column(String)  # Corporate parody: "Sunny Outlook", "Stormy Markets"
    
    # Daily Budget
    starting_money = Column(Integer, nullable=False)
    money_allocated = Column(Integer, default=0)  # How much player planned to spend
    actual_money_spent = Column(Integer, default=0)  # What was actually spent
    ending_money = Column(Integer)  # Money at end of day
    
    # Main Action (only one per day)
    primary_action = Column(Enum(ActionType), nullable=False)
    action_details = Column(JSON, default=dict)  # {"dungeon_id": 1, "team": [1,2,3]} or {"adventurer_type": "hr_manager"}
    
    # Action Results
    action_result = Column(Enum(ActionResult))
    result_details = Column(JSON, default=dict)  # Detailed outcome data
    experience_gained = Column(Integer, default=0)
    money_earned = Column(Integer, default=0)
    money_lost = Column(Integer, default=0)
    
    # Secondary Actions (only on non-dungeon days)
    secondary_actions = Column(JSON, default=list)  # [{"action": "train", "target": "adventurer_1", "cost": 100}]
    secondary_results = Column(JSON, default=list)  # Results for each secondary action
    
    # Day Summary
    major_events = Column(JSON, default=list)  # ["New adventurer hired", "Facility upgraded"]
    achievements_unlocked = Column(JSON, default=list)  # Any achievements earned today
    guild_morale_change = Column(Integer, default=0)  # +/- morale for the day
    
    # Planning vs Reality
    plan_executed_successfully = Column(Boolean, default=True)
    deviations_from_plan = Column(JSON, default=list)  # What went differently than planned
    
    # Timestamps
    day_started = Column(DateTime(timezone=True))
    day_ended = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    game_run = relationship("GameRun", back_populates="daily_plans")
    daily_expense = relationship("DailyExpense", back_populates="daily_plan", uselist=False)

class Calendar(Base):
    """Calendar system with special events and seasonal effects"""
    __tablename__ = "calendar"

    id = Column(Integer, primary_key=True, index=True)
    
    # Calendar Info
    day_number = Column(Integer, nullable=False, unique=True)  # Global day counter
    day_name = Column(String)  # "Monday", "Tuesday", etc.
    week_number = Column(Integer)
    month_name = Column(String)  # "January", "Q1", "Fiscal Year Start"
    
    # Day Characteristics
    day_type = Column(Enum(DayType), default=DayType.WEEKDAY)
    is_special = Column(Boolean, default=False)
    
    # Special Events
    global_event = Column(String)  # "Industry Conference", "Market Crash", "Holiday Season"
    event_description = Column(Text)  # Detailed description of the event
    event_effects = Column(JSON, default=dict)  # {"recruitment_cost": 0.8, "dungeon_rewards": 1.2}
    
    # Market Conditions (affects costs/rewards)
    market_sentiment = Column(String, default="stable")  # "bull", "bear", "volatile", "stable"
    economic_modifier = Column(Integer, default=100)  # Percentage modifier for costs/rewards
    
    # Seasonal Bonuses
    seasonal_effects = Column(JSON, default=dict)  # Recurring effects for this time period
    
    # Unlocks & Availability
    dungeons_available = Column(JSON, default=list)  # Which dungeons can be accessed today
    special_recruitment = Column(JSON, default=list)  # Special adventurers available
    limited_time_offers = Column(JSON, default=list)  # Special deals or equipment
    
    # Corporate Calendar Parody
    corporate_theme = Column(String)  # "Performance Review Season", "Budget Planning", "Team Building Month"
    motivational_quote = Column(String)  # Daily corporate wisdom
    industry_news = Column(JSON, default=list)  # Fake news affecting the business world
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())