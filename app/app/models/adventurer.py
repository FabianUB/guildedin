from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
import random
from .database import Base

# Association tables for many-to-many relationships
adventurer_skills = Table(
    'adventurer_skills', Base.metadata,
    Column('adventurer_id', Integer, ForeignKey('adventurers.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)

adventurer_traits = Table(
    'adventurer_traits', Base.metadata,
    Column('adventurer_id', Integer, ForeignKey('adventurers.id'), primary_key=True),
    Column('trait_id', Integer, ForeignKey('traits.id'), primary_key=True)
)

class Skill(Base):
    """Combat skills that adventurers can use during dungeons"""
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=False)
    skill_type = Column(String, nullable=False)  # 'offensive', 'defensive', 'utility', 'healing'
    cooldown = Column(Integer, default=0)  # Turns between uses (0 = no cooldown)
    
    # Class restrictions (None = available to all)
    restricted_to_classes = Column(String, nullable=True)  # Comma-separated class names, or None
    
    # Darkest Dungeon-style position system
    usable_positions = Column(String, nullable=False, default="1,2,3,4")  # Comma-separated positions (1=front, 2=mid-front, 3=mid-back, 4=back)
    target_type = Column(String, nullable=False, default="enemy")  # 'enemy', 'ally', 'any', 'self'
    target_positions = Column(String, nullable=True)  # Which positions this skill can target (None = any position of target_type)
    
    # Relationships
    adventurers = relationship("Adventurer", secondary=adventurer_skills, back_populates="skills")
    
    def __repr__(self):
        return f"<Skill(id={self.id}, name='{self.name}', type='{self.skill_type}', positions='{self.usable_positions}', targets='{self.target_type}')>"
    
    def can_use_from_position(self, position):
        """Check if skill can be used from specific position (1-4)"""
        return str(position) in self.usable_positions.split(',')
    
    def can_target_position(self, position, target_type=None):
        """Check if skill can target specific position (1-4)"""
        if target_type and self.target_type not in ['any', target_type]:
            return False
        if not self.target_positions:
            return True  # Can target any position of correct type
        return str(position) in self.target_positions.split(',')
    
    def get_valid_targets(self):
        """Get description of what this skill can target"""
        target_desc = {
            'enemy': 'Enemies',
            'ally': 'Allies', 
            'any': 'Anyone',
            'self': 'Self only'
        }
        return target_desc.get(self.target_type, 'Unknown')

class Trait(Base):
    """Passive traits that provide bonuses and penalties in combat and outside combat"""
    __tablename__ = "traits"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=False)
    trait_type = Column(String, nullable=False)  # 'combat', 'economic', 'social', 'training'
    
    # Effect values (can be positive or negative)
    bonus_value = Column(Integer, default=0)  # Percentage or flat bonus (negative values = penalties)
    bonus_type = Column(String, nullable=True)  # 'percentage', 'flat', 'special'
    
    # Additional effect for complex traits with both positive and negative aspects
    penalty_value = Column(Integer, default=0)  # Additional penalty value for balanced traits
    penalty_type = Column(String, nullable=True)  # What the penalty affects
    
    # Trait classification
    effect_type = Column(String, default="positive")  # 'positive', 'negative', 'mixed'
    rarity = Column(String, default="common")  # 'common', 'uncommon', 'rare', 'legendary'
    
    # Relationships  
    adventurers = relationship("Adventurer", secondary=adventurer_traits, back_populates="traits")
    
    def __repr__(self):
        return f"<Trait(id={self.id}, name='{self.name}', type='{self.trait_type}', effect='{self.effect_type}', rarity='{self.rarity}')>"
    
    @property
    def is_negative(self):
        """Check if trait has overall negative effect"""
        return self.effect_type in ['negative', 'mixed']
    
    @property
    def is_positive(self):
        """Check if trait has overall positive effect"""
        return self.effect_type in ['positive', 'mixed']
    
    def get_effect_description(self):
        """Get human-readable description of trait effects"""
        if self.effect_type == "positive":
            return f"+{self.bonus_value}% {self.bonus_type}" if self.bonus_type else "Special positive effect"
        elif self.effect_type == "negative":
            return f"{self.bonus_value}% {self.bonus_type}" if self.bonus_type else "Special negative effect"
        else:  # mixed
            bonus_desc = f"+{self.bonus_value}% {self.bonus_type}" if self.bonus_type else "Special bonus"
            penalty_desc = f"-{self.penalty_value}% {self.penalty_type}" if self.penalty_type else "Special penalty"
            return f"{bonus_desc}, {penalty_desc}"

class AdventurerClass(PyEnum):
    """Fantasy RPG classes for adventurers"""
    FIGHTER = "fighter"
    ROGUE = "rogue" 
    MAGE = "mage"
    CLERIC = "cleric"
    ARCHER = "archer"
    PALADIN = "paladin"
    BARBARIAN = "barbarian"
    BARD = "bard"
    DRUID = "druid"
    MONK = "monk"

class AdventurerSeniority(PyEnum):
    """Seniority levels affecting growth rates"""
    JUNIOR = "junior"      # 80% of base growth rates, cheaper to hire
    MID = "mid"           # 100% of base growth rates
    SENIOR = "senior"     # 140% of base growth rates, expensive to hire

class AdventurerRole(PyEnum):
    """Combat roles for team composition"""
    DPS = "dps"           # Damage dealers
    TANK = "tank"         # Damage absorbers  
    SUPPORT = "support"   # Team enablers

class Adventurer(Base):
    """Bot characters with fantasy RPG classes that players can recruit"""
    __tablename__ = "adventurers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identity & Ownership
    name = Column(String, nullable=False)  # Generated fantasy names
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=True)  # NULL for available adventurers
    game_session_id = Column(Integer, ForeignKey("game_sessions.id"), nullable=False)  # Session isolation
    
    # RPG Class & Progression
    adventurer_class = Column(String, nullable=False)  # AdventurerClass enum value
    seniority = Column(String, nullable=False, default="junior")  # AdventurerSeniority enum value
    role = Column(String, nullable=False)  # AdventurerRole enum value
    
    # Core 5 Stats (Uma Musume Style)
    max_hp = Column(Integer, default=100)
    current_hp = Column(Integer, default=100)
    drive = Column(Integer, default=10)       # Physical strength and determination (STR)
    efficiency = Column(Integer, default=10)  # Speed and dexterity (DEX/SPEED)  
    resilience = Column(Integer, default=10)  # Endurance and constitution (CON/END)
    insight = Column(Integer, default=10)     # Intelligence and wisdom (INT/WIS)
    luck = Column(Integer, default=10)        # Fortune and critical success chance
    
    # Condition Stats (Uma Musume Style)
    morale = Column(Integer, default=75)      # Mood/happiness (0-100)
    stamina = Column(Integer, default=100)    # Energy for training/dungeons (0-100)
    
    # Fire Emblem-Style Growth Rates for Training (Percentages, can exceed 100%)
    hp_growth = Column(Integer, default=80)       # % chance to gain HP during training
    drive_growth = Column(Integer, default=60)    # % chance to gain Drive during strength training
    efficiency_growth = Column(Integer, default=50)  # % chance to gain Efficiency during speed training
    resilience_growth = Column(Integer, default=40)  # % chance to gain Resilience during endurance training
    insight_growth = Column(Integer, default=30)     # % chance to gain Insight during wisdom training
    luck_growth = Column(Integer, default=20)        # % chance to gain Luck during any training (low base chance)
    
    # Recruitment Info
    hire_cost = Column(Integer, default=500)  # Cost to recruit
    weekly_salary = Column(Integer, default=50)  # Weekly salary cost
    is_available = Column(Boolean, default=False)  # False = already hired
    
    # Timestamps
    recruited_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    guild = relationship("Guild", back_populates="adventurers")
    game_session = relationship("GameSession", back_populates="adventurers")
    skills = relationship("Skill", secondary=adventurer_skills, back_populates="adventurers")
    traits = relationship("Trait", secondary=adventurer_traits, back_populates="adventurers")
    
    def __repr__(self):
        return f"<Adventurer(id={self.id}, name='{self.name}', class='{self.adventurer_class}', seniority='{self.seniority}', level={self.level})>"
    
    @property
    def class_display_name(self):
        """Get formatted class name for display"""
        return self.adventurer_class.replace('_', ' ').title()
    
    @property
    def seniority_display_name(self):
        """Get formatted seniority for display"""
        return self.seniority.title()
    
    @property
    def role_display_name(self):
        """Get formatted role for display"""
        return self.role.upper()
    
    @property
    def class_emoji(self):
        """Get emoji icon for adventurer class"""
        class_emojis = {
            "fighter": "⚔️",
            "rogue": "🗡️", 
            "mage": "🔮",
            "cleric": "⚡",
            "archer": "🏹",
            "paladin": "🛡️",
            "barbarian": "🪓",
            "bard": "🎵",
            "druid": "🌿",
            "monk": "👊"
        }
        return class_emojis.get(self.adventurer_class, "⚔️")
    
    @property
    def seniority_emoji(self):
        """Get emoji for seniority level"""
        seniority_emojis = {
            "junior": "🌱",
            "mid": "⭐",
            "senior": "💎"
        }
        return seniority_emojis.get(self.seniority, "⭐")
    
    @property
    def role_emoji(self):
        """Get emoji for combat role"""
        role_emojis = {
            "dps": "💥",
            "tank": "🛡️",
            "support": "💚"
        }
        return role_emojis.get(self.role, "⚔️")
    
    @property
    def hp_percentage(self):
        """Get HP as percentage for health bars"""
        if self.max_hp <= 0:
            return 0
        return int((self.current_hp / self.max_hp) * 100)
    
    @property
    def is_injured(self):
        """Check if adventurer needs healing"""
        return self.current_hp < self.max_hp
    
    @property
    def is_critically_injured(self):
        """Check if adventurer is in critical condition"""
        return self.current_hp <= (self.max_hp * 0.25)
    
    @property
    def total_stats(self):
        """Calculate total stat points (replaces level concept)"""
        return self.drive + self.efficiency + self.resilience + self.insight + self.luck
    
    @property
    def condition_status(self):
        """Get condition status based on morale and stamina (Uma Musume style)"""
        avg_condition = (self.morale + self.stamina) / 2
        if avg_condition >= 90:
            return "Excellent"
        elif avg_condition >= 75:
            return "Good"
        elif avg_condition >= 50:
            return "Normal" 
        elif avg_condition >= 25:
            return "Poor"
        else:
            return "Bad"
    
    def can_train(self):
        """Check if adventurer is in condition to train effectively"""
        return self.stamina >= 10  # Only need 10 stamina since training costs 5
    
    def rest(self):
        """Restore morale and stamina (alternative to training)"""
        # Restore 20-40 stamina and 10-20 morale
        import random
        stamina_gain = random.randint(20, 40)
        morale_gain = random.randint(10, 20)
        
        self.stamina = min(100, self.stamina + stamina_gain)
        self.morale = min(100, self.morale + morale_gain)
        
        return {
            "stamina_gained": stamina_gain,
            "morale_gained": morale_gain,
            "new_stamina": self.stamina,
            "new_morale": self.morale
        }
    
    def heal(self, amount):
        """Heal the adventurer by specified amount"""
        self.current_hp = min(self.current_hp + amount, self.max_hp)
        return self.current_hp
    
    def take_damage(self, amount):
        """Apply damage to the adventurer"""
        self.current_hp = max(self.current_hp - amount, 0)
        return self.current_hp
    
    def train_stat(self, stat_name, guild_exp_bonus=0):
        """
        Train a specific stat using Fire Emblem-style growth rates.
        Returns dict with gains and exp earned for guild builds.
        """
        if not self.can_train():
            return {"error": "Adventurer too tired to train effectively"}
        
        gains = {}
        base_guild_exp = 50  # Base EXP earned for guild builds
        
        # Determine which stat to train and its growth rate
        growth_rates = {
            "drive": self.drive_growth,
            "efficiency": self.efficiency_growth, 
            "resilience": self.resilience_growth,
            "insight": self.insight_growth,
            "luck": self.luck_growth
        }
        
        if stat_name not in growth_rates:
            return {"error": f"Invalid stat: {stat_name}"}
        
        # Roll for stat gain
        stat_gain = self._roll_stat_growth(growth_rates[stat_name])
        if stat_gain > 0:
            # Apply stat gain
            current_value = getattr(self, stat_name)
            setattr(self, stat_name, current_value + stat_gain)
            gains[stat_name.upper()] = stat_gain
        
        # Small chance for HP gain during any training
        hp_gain = self._roll_stat_growth(self.hp_growth // 4)  # 1/4 chance of HP growth
        if hp_gain > 0:
            self.max_hp += hp_gain * 3
            self.current_hp = min(self.current_hp + hp_gain * 3, self.max_hp)
            gains['HP'] = hp_gain * 3
        
        # Training costs consistent stamina, with chance to gain morale from successful training
        import random
        stamina_cost = 5  # Consistent low cost
        
        # Morale can increase or decrease slightly based on training success
        if gains:  # If we gained stats, small chance for morale boost
            morale_change = random.choice([-2, -1, 0, 0, 1])  # Mostly neutral, slight chance for +1 or -1/-2
        else:  # Failed training session, slight morale drop
            morale_change = random.choice([-2, -1, -1, 0])  # Higher chance for small morale drop
        
        self.stamina = max(0, self.stamina - stamina_cost)
        self.morale = max(0, min(100, self.morale + morale_change))
        
        # Calculate guild EXP earned (affected by guild bonuses)
        guild_exp_earned = int(base_guild_exp * (1 + guild_exp_bonus / 100))
        
        return {
            "gains": gains,
            "guild_exp_earned": guild_exp_earned,
            "stamina_cost": stamina_cost,
            "morale_change": morale_change,
            "new_stamina": self.stamina,
            "new_morale": self.morale,
            "new_condition": self.condition_status
        }
    
    def _roll_stat_growth(self, growth_rate):
        """
        Roll for stat growth based on Fire Emblem mechanics.
        Examples:
        - 75% growth: 75% chance for +1, 25% chance for +0
        - 150% growth: guaranteed +1, 50% chance for +2 total
        - 200% growth: guaranteed +2
        """
        if growth_rate <= 0:
            return 0
        
        # Calculate guaranteed gains and remaining percentage
        guaranteed_gains = growth_rate // 100
        remaining_chance = growth_rate % 100
        
        total_gains = guaranteed_gains
        
        # Roll for the remaining percentage
        if remaining_chance > 0 and random.randint(1, 100) <= remaining_chance:
            total_gains += 1
        
        return total_gains
    
    def add_skill(self, skill):
        """Add a skill to the adventurer"""
        if skill not in self.skills:
            self.skills.append(skill)
    
    def remove_skill(self, skill):
        """Remove a skill from the adventurer"""
        if skill in self.skills:
            self.skills.remove(skill)
    
    def add_trait(self, trait):
        """Add a trait to the adventurer"""
        if trait not in self.traits:
            self.traits.append(trait)
    
    def remove_trait(self, trait):
        """Remove a trait from the adventurer"""
        if trait in self.traits:
            self.traits.remove(trait)
    
    def get_skills_by_type(self, skill_type):
        """Get all skills of a specific type"""
        return [skill for skill in self.skills if skill.skill_type == skill_type]
    
    def get_traits_by_type(self, trait_type):
        """Get all traits of a specific type"""
        return [trait for trait in self.traits if trait.trait_type == trait_type]
    
    def get_combat_bonus(self, bonus_type):
        """Calculate total bonus from traits for specific bonus type"""
        total_bonus = 0
        for trait in self.traits:
            if trait.trait_type == 'combat' and trait.bonus_type == bonus_type:
                total_bonus += trait.bonus_value
        return total_bonus
    
    @classmethod
    def generate_growth_rates(cls, adventurer_class, seniority):
        """
        Generate appropriate growth rates based on class and seniority.
        Returns dict of growth rates for the new 5-stat system.
        """
        # Base growth rates by class (focused on their specialties)
        # New 5-stat system: Drive, Efficiency, Resilience, Insight, Luck
        base_growths = {
            "fighter": {"hp": 90, "drive": 80, "efficiency": 45, "resilience": 75, "insight": 30, "luck": 40},
            "rogue": {"hp": 60, "drive": 55, "efficiency": 85, "resilience": 45, "insight": 60, "luck": 70},
            "mage": {"hp": 45, "drive": 25, "efficiency": 40, "resilience": 35, "insight": 90, "luck": 65},
            "cleric": {"hp": 70, "drive": 40, "efficiency": 50, "resilience": 60, "insight": 85, "luck": 55},
            "archer": {"hp": 55, "drive": 60, "efficiency": 80, "resilience": 45, "insight": 50, "luck": 75},
            "paladin": {"hp": 85, "drive": 70, "efficiency": 35, "resilience": 80, "insight": 50, "luck": 45},
            "barbarian": {"hp": 95, "drive": 85, "efficiency": 60, "resilience": 85, "insight": 20, "luck": 50},
            "bard": {"hp": 50, "drive": 35, "efficiency": 65, "resilience": 40, "insight": 70, "luck": 80},
            "druid": {"hp": 65, "drive": 45, "efficiency": 55, "resilience": 65, "insight": 80, "luck": 75},
            "monk": {"hp": 75, "drive": 65, "efficiency": 75, "resilience": 70, "insight": 55, "luck": 85}
        }
        
        # Seniority multipliers
        seniority_multipliers = {
            "junior": 0.8,   # 80% of base growth rates (cheaper to hire)
            "mid": 1.0,      # 100% of base growth rates  
            "senior": 1.4    # 140% of base growth rates (expensive but can exceed 100%)
        }
        
        base = base_growths.get(adventurer_class, base_growths["fighter"])
        multiplier = seniority_multipliers.get(seniority, 1.0)
        
        return {
            "hp_growth": int(base["hp"] * multiplier),
            "drive_growth": int(base["drive"] * multiplier),
            "efficiency_growth": int(base["efficiency"] * multiplier),
            "resilience_growth": int(base["resilience"] * multiplier),
            "insight_growth": int(base["insight"] * multiplier),
            "luck_growth": int(base["luck"] * multiplier)
        }
    
    @classmethod
    def get_role_for_class(cls, adventurer_class):
        """Determine the primary role for each class"""
        class_roles = {
            "fighter": "dps",       # Can also tank but primarily DPS
            "rogue": "dps",
            "mage": "dps", 
            "cleric": "support",
            "archer": "dps",
            "paladin": "tank",
            "barbarian": "tank",    # Can also DPS but primarily tank
            "bard": "support",
            "druid": "support",
            "monk": "dps"
        }
        return class_roles.get(adventurer_class, "dps")