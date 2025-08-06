from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class TurnSummary(Base):
    """Daily briefing summary for activity feed"""
    __tablename__ = "turn_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    game_run_id = Column(Integer, ForeignKey("game_runs.id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    
    # Summary Data
    actions_taken = Column(JSON, default=list)        # ["Recruited Sarah", "Trained Mike"]
    resources_changed = Column(JSON, default=dict)    # {"gold": +500, "reputation": +5}
    major_events = Column(JSON, default=list)         # ["Dungeon cleared", "Level up"]
    
    # Performance
    income = Column(Integer, default=0)
    expenses = Column(Integer, default=0)
    net_change = Column(Integer, default=0)
    
    # Activity Feed Display
    post_title = Column(String)  # "🏰 TechCorp Guild - Daily Briefing"
    post_content = Column(String)  # Formatted summary text
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    game_run = relationship("GameRun", back_populates="turn_summaries")