from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Guild(Base):
    """Player's managed guild/company within their game session"""
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("players.id"), nullable=False, unique=True)
    game_session_id = Column(Integer, ForeignKey("game_sessions.id"), nullable=False, unique=True)  # Session isolation
    
    # Core Resources
    gold = Column(Integer, default=5000)  # Primary currency
    gold_interest_rate = Column(Integer, default=5)  # 5% weekly interest (upgradeable)
    
    exp = Column(Integer, default=0)  # Experience points (earns weekly interest)
    exp_interest_rate = Column(Integer, default=5)  # 5% weekly interest on EXP
    
    # Share Price & Market Performance
    share_price = Column(Float, default=1.0)  # Starting share price: 1G (lowest rank)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("Player", back_populates="guild")
    game_session = relationship("GameSession", back_populates="guild")
    adventurers = relationship("Adventurer", back_populates="guild")
    
    def calculate_gold_interest(self):
        """Calculate weekly interest on current gold"""
        return int(self.gold * (self.gold_interest_rate / 100.0))
    
    def calculate_exp_interest(self):
        """Calculate weekly interest on EXP"""
        return int(self.exp * (self.exp_interest_rate / 100.0))
    
    def apply_weekly_interest(self):
        """Apply weekly interest to both gold and EXP"""
        gold_interest = self.calculate_gold_interest()
        exp_interest = self.calculate_exp_interest()
        
        self.gold += gold_interest
        self.exp += exp_interest
        
        return {
            "gold_interest": gold_interest,
            "exp_interest": exp_interest,
            "new_gold_total": self.gold,
            "new_exp_total": self.exp
        }
    
    def get_guild_rank(self):
        """Calculate guild rank based on share price tiers from GDD"""
        if self.share_price >= 800:
            return "S"
        elif self.share_price >= 401:
            return "A"
        elif self.share_price >= 201:
            return "B"
        elif self.share_price >= 101:
            return "C"
        elif self.share_price >= 51:
            return "D"
        else:
            return "E"
    
    def get_rank_description(self):
        """Get human-readable description of guild rank"""
        rank = self.get_guild_rank()
        descriptions = {
            "S": "Market Leader",
            "A": "Elite",
            "B": "Successful",
            "C": "Established",
            "D": "Growth Phase",
            "E": "Startup Phase"
        }
        return descriptions.get(rank, "Unknown")
    
    def get_formatted_share_price(self):
        """Get formatted share price string for display"""
        return f"{self.share_price:.1f}G"
    
    def get_max_adventurers(self):
        """Get maximum adventurers allowed based on guild rank"""
        rank = self.get_guild_rank()
        max_adventurers = {
            "E": 3,  # Startup guilds get 3 slots
            "D": 4,  # Growth phase gets 4 slots
            "C": 5,  # Established gets 5 slots
            "B": 6,  # Successful gets 6 slots
            "A": 8,  # Elite gets 8 slots
            "S": 10  # Market leaders get 10 slots
        }
        return max_adventurers.get(rank, 3)
    
    def get_current_adventurer_count(self):
        """Get current number of recruited adventurers"""
        return len(self.adventurers) if self.adventurers else 0
    
    def can_recruit_more_adventurers(self):
        """Check if guild can recruit more adventurers"""
        return self.get_current_adventurer_count() < self.get_max_adventurers()
    
    def get_adventurers_by_role(self, role):
        """Get adventurers filtered by their role (dps, tank, support)"""
        if not self.adventurers:
            return []
        return [adv for adv in self.adventurers if adv.role == role]