from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base

class ExpenseCategory(PyEnum):
    ADVENTURER_SALARIES = "adventurer_salaries"     # Daily pay for employees
    FACILITY_MAINTENANCE = "facility_maintenance"   # Upkeep costs for buildings
    GUILD_OVERHEAD = "guild_overhead"               # Basic operational costs
    TRAINING_COSTS = "training_costs"               # Cost to improve adventurer stats
    RECRUITMENT_FEES = "recruitment_fees"           # Cost to hire new adventurers
    EQUIPMENT_PURCHASE = "equipment_purchase"       # Buying gear for adventurers
    DUNGEON_PREPARATION = "dungeon_preparation"     # Supplies, planning costs
    EMERGENCY_EXPENSES = "emergency_expenses"       # Unexpected costs from events
    MARKETING = "marketing"                         # Guild reputation building
    INSURANCE = "insurance"                         # Protection against disasters

class ExpenseType(PyEnum):
    FIXED_DAILY = "fixed_daily"         # Same amount every day
    VARIABLE_DAILY = "variable_daily"   # Changes based on guild size/facilities
    ACTION_BASED = "action_based"       # Only when specific actions are taken
    EVENT_TRIGGERED = "event_triggered" # Random events or special circumstances
    OPTIONAL = "optional"               # Player choice expenses

class DailyExpense(Base):
    """Detailed breakdown of all costs incurred on a specific day"""
    __tablename__ = "daily_expenses"

    id = Column(Integer, primary_key=True, index=True)
    
    # Context
    game_run_id = Column(Integer, ForeignKey("game_runs.id"), nullable=False)
    daily_plan_id = Column(Integer, ForeignKey("daily_plans.id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    
    # Total Summary
    total_expenses = Column(Integer, default=0)
    total_income = Column(Integer, default=0)
    net_change = Column(Integer, default=0)  # income - expenses
    
    # Expense Breakdown
    adventurer_salaries = Column(Integer, default=0)
    facility_maintenance = Column(Integer, default=0)
    guild_overhead = Column(Integer, default=0)
    action_costs = Column(Integer, default=0)  # Costs from daily actions
    emergency_costs = Column(Integer, default=0)  # Unexpected expenses
    optional_spending = Column(Integer, default=0)  # Player choice expenses
    
    # Income Breakdown
    dungeon_rewards = Column(Integer, default=0)
    contract_payments = Column(Integer, default=0)  # Future: client contracts
    reputation_bonuses = Column(Integer, default=0)
    equipment_sales = Column(Integer, default=0)  # Selling old gear
    misc_income = Column(Integer, default=0)
    
    # Detailed Expense Log
    expense_details = Column(JSON, default=list)  # [{"category": "salary", "amount": 200, "description": "Paid 4 adventurers"}]
    income_details = Column(JSON, default=list)   # [{"source": "dungeon", "amount": 1500, "description": "Quarterly Review dungeon"}]
    
    # Cost Modifiers Applied
    difficulty_modifier = Column(Integer, default=100)  # Percentage modifier from difficulty
    market_modifier = Column(Integer, default=100)     # Economic conditions modifier
    seasonal_modifier = Column(Integer, default=100)   # Holiday/seasonal effects
    guild_efficiency = Column(Integer, default=100)    # Facility upgrades reducing costs
    
    # Payment Status
    all_expenses_paid = Column(Boolean, default=True)
    unpaid_expenses = Column(Integer, default=0)  # Debt carried to next day
    
    # Consequences
    morale_impact = Column(Integer, default=0)  # How expenses affected team morale
    reputation_impact = Column(Integer, default=0)  # Effect on guild reputation
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    game_run = relationship("GameRun", back_populates="daily_expenses")
    daily_plan = relationship("DailyPlan", back_populates="daily_expense")

class ExpenseTemplate(Base):
    """Templates for calculating daily expenses based on guild state"""
    __tablename__ = "expense_templates"

    id = Column(Integer, primary_key=True, index=True)
    
    # Template Info
    name = Column(String, nullable=False)  # "Basic Guild Overhead", "Executive Facility Maintenance"
    category = Column(Enum(ExpenseCategory), nullable=False)
    expense_type = Column(Enum(ExpenseType), nullable=False)
    
    # Cost Calculation
    base_cost = Column(Integer, default=0)  # Fixed amount
    per_adventurer_cost = Column(Integer, default=0)  # Multiplied by adventurer count
    per_facility_cost = Column(Integer, default=0)    # Multiplied by facility count
    
    # Conditions
    minimum_guild_level = Column(Integer, default=1)
    required_facilities = Column(JSON, default=list)  # ["training_room", "conference_room"]
    triggers = Column(JSON, default=list)  # When this expense applies
    
    # Modifiers
    difficulty_scaling = Column(JSON, default=dict)  # {"intern": 0.7, "executive": 1.5}
    
    # Description
    description = Column(String)
    corporate_flavor = Column(String)  # "Monthly team building budget allocation"
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())