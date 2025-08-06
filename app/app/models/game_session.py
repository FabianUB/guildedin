from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

from .database import Base

class GameDifficulty(PyEnum):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    NIGHTMARE = "nightmare"

class GameSession(Base):
    """
    Represents an isolated game instance for a single player.
    Each player gets their own world with unique bot guilds, dungeons, and market conditions.
    """
    __tablename__ = "game_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    
    # Game progression
    current_day = Column(Integer, default=1)
    current_quarter = Column(Integer, default=1) 
    current_year = Column(Integer, default=2024)
    
    # Game state
    difficulty_level = Column(Enum(GameDifficulty), default=GameDifficulty.NORMAL)
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Session metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_played_at = Column(DateTime, default=datetime.utcnow)
    total_playtime_minutes = Column(Integer, default=0)
    
    # Game configuration
    daily_action_limit = Column(Integer, default=5)
    starting_gold = Column(Integer, default=5000)
    market_volatility = Column(Float, default=1.0)  # Multiplier for bot guild activity
    
    # Win/lose conditions
    target_guild_rank = Column(String, default="A")  # Goal to reach
    target_days = Column(Integer, default=365)  # Time limit
    bankruptcy_threshold = Column(Integer, default=0)  # Fail if gold drops below this
    
    # Session notes/metadata
    session_notes = Column(Text)  # For any custom session data
    
    # Relationships
    player = relationship("Player", back_populates="game_sessions")
    player_guild = relationship("Guild", back_populates="game_session", uselist=False)
    bot_guilds = relationship("BotGuild", back_populates="game_session", cascade="all, delete-orphan")
    dungeons = relationship("Dungeon", back_populates="game_session", cascade="all, delete-orphan")
    market_events = relationship("MarketEvent", back_populates="game_session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<GameSession(id={self.id}, player_id={self.player_id}, day={self.current_day})>"
    
    @property
    def game_date_display(self):
        """Format game date for UI display"""
        return f"Day {self.current_day} • Q{self.current_quarter} {self.current_year}"
    
    @property
    def days_remaining(self):
        """Calculate days remaining until target deadline"""
        return max(0, self.target_days - self.current_day)
    
    @property
    def progress_percentage(self):
        """Calculate overall game progress as percentage"""
        return min(100, (self.current_day / self.target_days) * 100)
    
    def advance_day(self):
        """Advance the game calendar by one day"""
        self.current_day += 1
        
        # Check if quarter/year should advance
        days_per_quarter = 90
        if self.current_day % days_per_quarter == 0:
            self.current_quarter += 1
            if self.current_quarter > 4:
                self.current_quarter = 1
                self.current_year += 1
        
        self.last_played_at = datetime.utcnow()
    
    def check_win_condition(self):
        """Check if player has won the game"""
        if not self.player_guild:
            return False
            
        # Won if reached target guild rank
        rank_values = {"E": 1, "D": 2, "C": 3, "B": 4, "A": 5, "S": 6}
        current_rank_value = rank_values.get(self.player_guild.guild_rank.value, 0)
        target_rank_value = rank_values.get(self.target_guild_rank, 5)
        
        return current_rank_value >= target_rank_value
    
    def check_lose_condition(self):
        """Check if player has lost the game"""
        if not self.player_guild:
            return False
            
        # Lost if ran out of time
        if self.current_day >= self.target_days:
            return True
            
        # Lost if went bankrupt
        if self.player_guild.gold <= self.bankruptcy_threshold:
            return True
            
        return False