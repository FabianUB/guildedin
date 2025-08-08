from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class GameSession(Base):
    """
    Isolated game instance for each player.
    Each player gets their own world with unique game state.
    """
    __tablename__ = "game_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, unique=True)  # One session per player
    
    # Game progression (Week-based calendar system)
    current_week = Column(Integer, default=1)      # Week 1, 2, 3, ... 
    current_quarter = Column(Integer, default=1)   # Quarter 1, 2, 3, 4
    current_year = Column(Integer, default=1)      # Year 1, 2, 3, ...
    
    # Game state
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Session metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_played_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Game configuration
    weekly_action_limit = Column(Integer, default=5)  # Upgradeable
    actions_remaining = Column(Integer, default=5)  # Current available actions
    starting_gold = Column(Integer, default=5000)
    
    # Relationships
    player = relationship("Player", back_populates="game_session")
    guild = relationship("Guild", back_populates="game_session", uselist=False)
    adventurers = relationship("Adventurer", back_populates="game_session")
    
    def __repr__(self):
        return f"<GameSession(id={self.id}, player_id={self.player_id}, week={self.current_week})>"
    
    @property
    def game_date_display(self):
        """Format game date for UI display"""
        return f"Week {self.current_week} • Q{self.current_quarter} Year {self.current_year}"
    
    @property
    def total_weeks_played(self):
        """Calculate total weeks since game start"""
        return (self.current_year - 1) * 56 + (self.current_quarter - 1) * 14 + self.current_week
    
    def advance_week(self, db_session=None):
        """Advance the game calendar by one week and apply interest"""
        self.current_week += 1
        
        # Check if quarter should advance (every 14 weeks)
        if self.current_week > 14:
            self.current_week = 1
            self.current_quarter += 1
            
            # Check if year should advance (every 4 quarters)
            if self.current_quarter > 4:
                self.current_quarter = 1
                self.current_year += 1
        
        # Reset weekly actions
        self.actions_remaining = self.weekly_action_limit
        
        # Apply weekly interest to guild resources
        if self.guild:
            interest_results = self.guild.apply_weekly_interest()
            if db_session:
                db_session.commit()  # Save interest changes
        
        # Update last played timestamp
        from datetime import datetime
        self.last_played_at = datetime.utcnow()
        
        return interest_results if self.guild else None
    
    @property
    def weeks_in_current_quarter(self):
        """Get current week within the quarter (1-14)"""
        return self.current_week
    
    @property
    def weeks_remaining_in_quarter(self):
        """Get weeks remaining in current quarter"""
        return 14 - self.current_week
    
    @property
    def should_show_activity_feed(self):
        """Determine if activity feed should be displayed"""
        # Show during Week 1 (tutorial) or Week 14 (quarterly briefing)
        return self.current_week in [1, 14]
    
    @property
    def is_tutorial_week(self):
        """Check if this is the tutorial week (Week 1, Q1, Year 1)"""
        return (self.current_week == 1 and 
                self.current_quarter == 1 and 
                self.current_year == 1)
    
    @property
    def is_quarterly_briefing_week(self):
        """Check if this is a quarterly briefing week (Week 14 of any quarter)"""
        return self.current_week == 14