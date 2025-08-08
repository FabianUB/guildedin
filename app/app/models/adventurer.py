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
    level = Column(Integer, default=1)  # Character level (1-100)
    
    # Core RPG Stats (Current Values)
    max_hp = Column(Integer, default=100)
    current_hp = Column(Integer, default=100)
    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    synergy = Column(Integer, default=10)  # Team coordination
    optics = Column(Integer, default=10)   # Perception/awareness
    
    # Fire Emblem-Style Growth Rates (Percentages, can exceed 100%)
    hp_growth = Column(Integer, default=80)      # % chance to gain HP per level
    str_growth = Column(Integer, default=60)     # % chance to gain STR per level
    dex_growth = Column(Integer, default=50)     # % chance to gain DEX per level
    con_growth = Column(Integer, default=40)     # % chance to gain CON per level
    int_growth = Column(Integer, default=30)     # % chance to gain INT per level
    syn_growth = Column(Integer, default=45)     # % chance to gain SYN per level
    opt_growth = Column(Integer, default=55)     # % chance to gain OPT per level
    
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
    
    def experience_to_next_level(self):
        """Calculate EXP needed to reach next level using RuneScape-style formula"""
        if self.level >= 100:
            return "MAX"
        
        current_level_xp = self.get_xp_for_level(self.level)
        next_level_xp = self.get_xp_for_level(self.level + 1)
        
        # For now, assume adventurer has just reached current level (0 progress)
        # In full implementation, we'd track current_experience
        xp_needed = next_level_xp - current_level_xp
        
        return f"{xp_needed:,}"
    
    @staticmethod
    def get_xp_for_level(level):
        """Get total XP required to reach a specific level (RuneScape formula)"""
        if level <= 1:
            return 0
        
        # RuneScape formula: sum of ((level-1)^2 * 100 / 4) for each level
        total_xp = 0
        for i in range(2, level + 1):
            total_xp += int((i - 1) ** 2 * 100 / 4)
        
        return total_xp
    
    def heal(self, amount):
        """Heal the adventurer by specified amount"""
        self.current_hp = min(self.current_hp + amount, self.max_hp)
        return self.current_hp
    
    def take_damage(self, amount):
        """Apply damage to the adventurer"""
        self.current_hp = max(self.current_hp - amount, 0)
        return self.current_hp
    
    def level_up(self):
        """
        Fire Emblem-style level up with growth rate rolls.
        Growth rates > 100% guarantee multiple points.
        Example: 150% = guaranteed +1, 50% chance for +2 total
        Returns dict of stat gains for display.
        """
        if self.level >= 100:
            return {}
        
        gains = {}
        
        # Roll each stat against its growth rate
        # HP Growth (always show as max_hp increase)
        hp_gain = self._roll_stat_growth(self.hp_growth)
        if hp_gain > 0:
            self.max_hp += hp_gain * 5  # HP gains are multiplied for bigger numbers
            self.current_hp = self.max_hp  # Heal to full on level up
            gains['HP'] = hp_gain * 5
        
        # Strength
        str_gain = self._roll_stat_growth(self.str_growth)
        if str_gain > 0:
            self.strength += str_gain
            gains['STR'] = str_gain
        
        # Dexterity  
        dex_gain = self._roll_stat_growth(self.dex_growth)
        if dex_gain > 0:
            self.dexterity += dex_gain
            gains['DEX'] = dex_gain
        
        # Constitution
        con_gain = self._roll_stat_growth(self.con_growth)
        if con_gain > 0:
            self.constitution += con_gain
            gains['CON'] = con_gain
        
        # Intelligence
        int_gain = self._roll_stat_growth(self.int_growth)
        if int_gain > 0:
            self.intelligence += int_gain
            gains['INT'] = int_gain
        
        # Synergy
        syn_gain = self._roll_stat_growth(self.syn_growth)
        if syn_gain > 0:
            self.synergy += syn_gain
            gains['SYN'] = syn_gain
        
        # Optics
        opt_gain = self._roll_stat_growth(self.opt_growth)
        if opt_gain > 0:
            self.optics += opt_gain
            gains['OPT'] = opt_gain
        
        # Level up
        self.level += 1
        
        return gains
    
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
        Returns dict of growth rates.
        """
        # Base growth rates by class (focused on their specialties)
        base_growths = {
            "fighter": {"hp": 90, "str": 75, "dex": 45, "con": 70, "int": 25, "syn": 50, "opt": 40},
            "rogue": {"hp": 60, "str": 50, "dex": 85, "con": 45, "int": 55, "syn": 65, "opt": 80},
            "mage": {"hp": 45, "str": 20, "dex": 40, "con": 35, "int": 90, "syn": 55, "opt": 75},
            "cleric": {"hp": 70, "str": 35, "dex": 50, "con": 55, "int": 80, "syn": 85, "opt": 65},
            "archer": {"hp": 55, "str": 55, "dex": 80, "con": 40, "int": 45, "syn": 45, "opt": 85},
            "paladin": {"hp": 85, "str": 65, "dex": 35, "con": 75, "int": 45, "syn": 70, "opt": 50},
            "barbarian": {"hp": 95, "str": 85, "dex": 55, "con": 80, "int": 15, "syn": 30, "opt": 35},
            "bard": {"hp": 50, "str": 30, "dex": 60, "con": 40, "int": 65, "syn": 90, "opt": 70},
            "druid": {"hp": 65, "str": 40, "dex": 55, "con": 60, "int": 75, "syn": 65, "opt": 80},
            "monk": {"hp": 75, "str": 60, "dex": 75, "con": 65, "int": 50, "syn": 70, "opt": 85}
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
            "str_growth": int(base["str"] * multiplier),
            "dex_growth": int(base["dex"] * multiplier),
            "con_growth": int(base["con"] * multiplier),
            "int_growth": int(base["int"] * multiplier),
            "syn_growth": int(base["syn"] * multiplier),
            "opt_growth": int(base["opt"] * multiplier)
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