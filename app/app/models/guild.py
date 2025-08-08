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
    
    # Guild Build System (replaces adventurer EXP)
    guild_exp = Column(Integer, default=0)  # EXP earned from all activities (training, dungeons, etc.)
    guild_exp_spent = Column(Integer, default=0)  # EXP spent on guild builds
    
    # Guild Build Bonuses (purchased with guild_exp)
    training_efficiency_bonus = Column(Integer, default=0)  # % bonus to training gains
    dungeon_reward_bonus = Column(Integer, default=0)      # % bonus to dungeon rewards
    recruitment_cost_reduction = Column(Integer, default=0) # % reduction in hiring costs
    facility_maintenance_reduction = Column(Integer, default=0)  # % reduction in facility costs
    action_count_bonus = Column(Integer, default=0)        # Extra weekly actions
    
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
    
    def calculate_guild_exp_interest(self):
        """Calculate weekly interest on unspent guild EXP"""
        available_exp = self.get_available_guild_exp()
        return int(available_exp * 0.05)  # 5% interest on unspent EXP
    
    def apply_weekly_interest(self):
        """Apply weekly interest to both gold and unspent guild EXP"""
        gold_interest = self.calculate_gold_interest()
        exp_interest = self.calculate_guild_exp_interest()
        
        self.gold += gold_interest
        self.guild_exp += exp_interest  # Add interest to total EXP pool
        
        return {
            "gold_interest": gold_interest,
            "exp_interest": exp_interest,
            "new_gold_total": self.gold,
            "new_guild_exp_total": self.guild_exp
        }
    
    def earn_guild_exp(self, amount):
        """Earn guild EXP from activities (training, dungeons, etc.)"""
        self.guild_exp += amount
        return self.guild_exp
    
    def get_available_guild_exp(self):
        """Get unspent guild EXP available for builds"""
        return self.guild_exp - self.guild_exp_spent
    
    def can_purchase_build(self, cost):
        """Check if guild has enough EXP for a build"""
        return self.get_available_guild_exp() >= cost
    
    def purchase_guild_build(self, build_type, cost):
        """Purchase a guild build upgrade"""
        if not self.can_purchase_build(cost):
            return {"error": "Not enough Guild EXP"}
        
        # Apply the build bonus
        if build_type == "training_efficiency":
            self.training_efficiency_bonus += 10  # +10% training efficiency
        elif build_type == "dungeon_rewards":
            self.dungeon_reward_bonus += 15      # +15% dungeon rewards
        elif build_type == "recruitment_cost":
            self.recruitment_cost_reduction += 5  # -5% hiring costs
        elif build_type == "facility_maintenance":
            self.facility_maintenance_reduction += 8  # -8% facility costs
        elif build_type == "extra_actions":
            self.action_count_bonus += 1         # +1 weekly action
        else:
            return {"error": f"Unknown build type: {build_type}"}
        
        # Spend the EXP
        self.guild_exp_spent += cost
        
        return {
            "success": True,
            "build_purchased": build_type,
            "cost": cost,
            "remaining_exp": self.get_available_guild_exp()
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
            "E": 1,  # Startup guilds get 1 slot (simplify for new players)
            "D": 2,  # Growth phase gets 2 slots
            "C": 4,  # Established gets 4 slots
            "B": 6,  # Successful gets 6 slots
            "A": 8,  # Elite gets 8 slots
            "S": 10  # Market leaders get 10 slots
        }
        return max_adventurers.get(rank, 1)
    
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
    
    def get_max_facilities(self):
        """Get maximum facilities allowed based on guild rank"""
        rank = self.get_guild_rank()
        max_facilities = {
            "E": 2,  # Startup guilds get 2 facility slots
            "D": 3,  # Growth phase gets 3 facility slots
            "C": 4,  # Established gets 4 facility slots
            "B": 5,  # Successful gets 5 facility slots
            "A": 6,  # Elite gets 6 facility slots
            "S": 8   # Market leaders get 8 facility slots
        }
        return max_facilities.get(rank, 2)
    
    def get_current_facility_count(self):
        """Get current number of built facilities (mockup)"""
        # For mockup purposes, return 0 - this will be connected to actual facilities later
        return 0
    
    def get_max_dungeons(self):
        """Get maximum dungeon contracts allowed based on guild rank"""
        rank = self.get_guild_rank()
        max_dungeons = {
            "E": 1,  # Startup guilds get 1 dungeon contract
            "D": 2,  # Growth phase gets 2 dungeon contracts
            "C": 3,  # Established gets 3 dungeon contracts
            "B": 4,  # Successful gets 4 dungeon contracts
            "A": 5,  # Elite gets 5 dungeon contracts
            "S": 6   # Market leaders get 6 dungeon contracts
        }
        return max_dungeons.get(rank, 1)
    
    def get_current_dungeon_count(self):
        """Get current number of active dungeon contracts (mockup)"""
        # For mockup purposes, return 0 - this will be connected to actual dungeon contracts later
        return 0
    
    @property
    def facilities(self):
        """Mockup facilities list - empty for now"""
        # This will be replaced with actual facility relationships later
        return []
    
    @property
    def dungeon_contracts(self):
        """Mockup dungeon contracts list - empty for now"""
        # This will be replaced with actual dungeon contract relationships later
        return []