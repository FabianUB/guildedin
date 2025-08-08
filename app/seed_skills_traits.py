#!/usr/bin/env python3
"""
Seed Skills and Traits for GuildedIn
Populates the database with initial skills and traits for adventurers
"""

from app.models.database import get_db, SessionLocal
from app.models.adventurer import Skill, Trait

def seed_skills():
    """Create initial skills for adventurers"""
    skills_data = [
        # Fighter Skills
        {
            "name": "Shield Wall",
            "description": "Creates a defensive barrier that blocks incoming attacks and protects nearby allies.",
            "skill_type": "defensive",
            "cooldown": 3,
            "restricted_to_classes": "fighter,paladin",
            "usable_positions": "1,2",  # Front and mid-front only
            "target_type": "ally",
            "target_positions": "1,2,3,4"  # Can protect all allies
        },
        {
            "name": "Mighty Strike", 
            "description": "A powerful melee attack that deals extra damage and has a chance to stun the target.",
            "skill_type": "offensive",
            "cooldown": 2,
            "restricted_to_classes": "fighter,barbarian",
            "usable_positions": "1,2",  # Need to be in melee range
            "target_type": "enemy",
            "target_positions": "1,2"  # Can only hit front enemies
        },
        {
            "name": "Taunt",
            "description": "Forces enemies to focus their attacks on this adventurer, protecting the team.",
            "skill_type": "defensive", 
            "cooldown": 1,
            "restricted_to_classes": "fighter,paladin,barbarian",
            "usable_positions": "1,2",  # Need to be visible to enemies
            "target_type": "enemy",
            "target_positions": "1,2,3,4"  # Can taunt any enemy
        },
        {
            "name": "Battle Fury",
            "description": "Increases attack speed and damage for a short duration when health drops below 50%.",
            "skill_type": "offensive",
            "cooldown": 4, 
            "restricted_to_classes": "fighter,barbarian",
            "usable_positions": "1,2,3,4",  # Self-buff, any position
            "target_type": "self",
            "target_positions": None
        },
        
        # Rogue Skills
        {
            "name": "Stealth Strike",
            "description": "Attack from the shadows with increased critical hit chance and damage.",
            "skill_type": "offensive",
            "cooldown": 3,
            "restricted_to_classes": "rogue",
            "usable_positions": "2,3,4",  # From behind, not front line
            "target_type": "enemy",
            "target_positions": "1,2"  # Sneak attack front enemies
        },
        {
            "name": "Smoke Bomb",
            "description": "Create a smoke cloud that reduces enemy accuracy and provides cover for the team.",
            "skill_type": "utility",
            "cooldown": 4,
            "restricted_to_classes": "rogue"
        },
        {
            "name": "Lockpicking",
            "description": "Open locked treasure chests and doors during dungeon exploration.",
            "skill_type": "utility",
            "cooldown": 0,
            "restricted_to_classes": "rogue"
        },
        
        # Mage Skills
        {
            "name": "Fireball",
            "description": "Launch a devastating fireball that deals area damage to multiple enemies.",
            "skill_type": "offensive",
            "cooldown": 2,
            "restricted_to_classes": "mage",
            "usable_positions": "3,4",  # Back line casting
            "target_type": "enemy", 
            "target_positions": "1,2,3,4"  # Long range, can hit any enemy
        },
        {
            "name": "Ice Shield",
            "description": "Create a magical barrier that absorbs damage and slows attacking enemies.",
            "skill_type": "defensive",
            "cooldown": 3,
            "restricted_to_classes": "mage"
        },
        {
            "name": "Arcane Missile",
            "description": "Fire multiple homing projectiles that never miss their target.",
            "skill_type": "offensive",
            "cooldown": 1,
            "restricted_to_classes": "mage"
        },
        
        # Cleric Skills
        {
            "name": "Heal",
            "description": "Restore health to a single ally, removing minor debuffs.",
            "skill_type": "healing",
            "cooldown": 1,
            "restricted_to_classes": "cleric,druid",
            "usable_positions": "2,3,4",  # Support from mid/back
            "target_type": "ally",
            "target_positions": "1,2,3,4"  # Can heal anyone
        },
        {
            "name": "Mass Heal",
            "description": "Restore health to all party members simultaneously.",
            "skill_type": "healing",
            "cooldown": 4,
            "restricted_to_classes": "cleric",
            "usable_positions": "3,4",  # Powerful magic from back line
            "target_type": "ally",
            "target_positions": "1,2,3,4"  # Affects whole party
        },
        {
            "name": "Divine Protection",
            "description": "Grant temporary immunity to debuffs and increased resistance to damage.",
            "skill_type": "defensive",
            "cooldown": 5,
            "restricted_to_classes": "cleric,paladin"
        },
        
        # Archer Skills
        {
            "name": "Precision Shot",
            "description": "A carefully aimed shot that ignores armor and has increased critical chance.",
            "skill_type": "offensive",
            "cooldown": 2,
            "restricted_to_classes": "archer"
        },
        {
            "name": "Rain of Arrows",
            "description": "Fire multiple arrows that strike all enemies in the area.",
            "skill_type": "offensive",
            "cooldown": 4,
            "restricted_to_classes": "archer"
        },
        {
            "name": "Eagle Eye",
            "description": "Increase accuracy and critical hit rate for several turns.",
            "skill_type": "utility",
            "cooldown": 3,
            "restricted_to_classes": "archer"
        },
        
        # Universal Skills (no class restrictions)
        {
            "name": "First Aid",
            "description": "Basic healing that any adventurer can perform to restore minor health.",
            "skill_type": "healing",
            "cooldown": 2,
            "restricted_to_classes": None,
            "usable_positions": "1,2,3,4",  # Anyone can use
            "target_type": "ally", 
            "target_positions": "1,2,3,4"  # Can heal any ally
        },
        {
            "name": "Dodge Roll",
            "description": "Quick evasive maneuver that increases dodge chance for one turn.",
            "skill_type": "defensive",
            "cooldown": 3,
            "restricted_to_classes": None
        },
        {
            "name": "Focus",
            "description": "Concentrate to increase accuracy and reduce skill cooldowns.",
            "skill_type": "utility",
            "cooldown": 4,
            "restricted_to_classes": None
        }
    ]
    
    db = SessionLocal()
    try:
        for skill_data in skills_data:
            # Set default positioning for skills that don't have it specified
            if "usable_positions" not in skill_data:
                skill_data["usable_positions"] = "1,2,3,4"  # Default: can use from any position
            if "target_type" not in skill_data:
                skill_data["target_type"] = "enemy"  # Default: targets enemies
            if "target_positions" not in skill_data:
                skill_data["target_positions"] = None  # Default: can target any position of target_type
                
            # Check if skill already exists
            existing_skill = db.query(Skill).filter(Skill.name == skill_data["name"]).first()
            if not existing_skill:
                skill = Skill(**skill_data)
                db.add(skill)
        
        db.commit()
        print(f"✅ Seeded {len(skills_data)} skills")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding skills: {e}")
    finally:
        db.close()

def seed_traits():
    """Create initial traits for adventurers"""
    traits_data = [
        # Combat Traits
        {
            "name": "Veteran Leadership",
            "description": "Provides +10% experience gain to all party members during dungeon expeditions.",
            "trait_type": "combat",
            "bonus_value": 10,
            "bonus_type": "percentage",
            "effect_type": "positive",
            "rarity": "uncommon"
        },
        {
            "name": "Iron Will",
            "description": "Immune to fear and charm effects. Reduces duration of all negative status effects by 50%.",
            "trait_type": "combat",
            "bonus_value": 50,
            "bonus_type": "percentage",
            "rarity": "rare"
        },
        {
            "name": "Heavy Armor Mastery",
            "description": "Reduces physical damage taken by 20% and negates movement penalties from heavy armor.",
            "trait_type": "combat",
            "bonus_value": 20,
            "bonus_type": "percentage",
            "rarity": "common"
        },
        {
            "name": "Berserker Rage",
            "description": "Deal 25% more damage when health is below 30%, but take 15% more damage.",
            "trait_type": "combat",
            "bonus_value": 25,
            "bonus_type": "percentage",
            "rarity": "uncommon"
        },
        {
            "name": "Lucky",
            "description": "15% chance to avoid any negative effect, including damage, debuffs, and traps.",
            "trait_type": "combat",
            "bonus_value": 15,
            "bonus_type": "percentage",
            "rarity": "rare"
        },
        {
            "name": "Quick Reflexes",
            "description": "Always act first in combat rounds and +10% dodge chance.",
            "trait_type": "combat",
            "bonus_value": 10,
            "bonus_type": "percentage",
            "rarity": "uncommon"
        },
        
        # Economic Traits
        {
            "name": "Treasure Hunter",
            "description": "Find 20% more gold and has a chance to discover rare items in dungeons.",
            "trait_type": "economic",
            "bonus_value": 20,
            "bonus_type": "percentage",
            "rarity": "common"
        },
        {
            "name": "Merchant Background",
            "description": "Equipment and supplies cost 15% less when purchased for this adventurer.",
            "trait_type": "economic",
            "bonus_value": 15,
            "bonus_type": "percentage",
            "rarity": "common"
        },
        {
            "name": "Goldsniff",
            "description": "Can detect hidden treasure rooms and secret passages containing valuable loot.",
            "trait_type": "economic",
            "bonus_value": 0,
            "bonus_type": "special",
            "rarity": "rare"
        },
        
        # Training Traits
        {
            "name": "Fast Learner",
            "description": "Gains experience 25% faster from all activities including combat and training.",
            "trait_type": "training",
            "bonus_value": 25,
            "bonus_type": "percentage",
            "rarity": "uncommon"
        },
        {
            "name": "Mentor",
            "description": "Other adventurers in the same guild gain +15% experience when training together.",
            "trait_type": "training",
            "bonus_value": 15,
            "bonus_type": "percentage",
            "rarity": "rare"
        },
        
        # Social Traits
        {
            "name": "Charismatic",
            "description": "Improves team morale and reduces chance of adventurers leaving the guild.",
            "trait_type": "social",
            "bonus_value": 25,
            "bonus_type": "percentage",
            "rarity": "common"
        },
        {
            "name": "Inspiring Presence",
            "description": "All party members gain +5% to all stats when this adventurer is present.",
            "trait_type": "social",
            "bonus_value": 5,
            "bonus_type": "percentage",
            "rarity": "legendary"
        },
        {
            "name": "Loyal",
            "description": "Will never leave the guild voluntarily and provides stability bonus to other adventurers.",
            "trait_type": "social",
            "bonus_value": 0,
            "bonus_type": "special",
            "rarity": "uncommon"
        },
        {
            "name": "Rival",
            "description": "Performs better when another specific adventurer is not in the same party.",
            "trait_type": "social",
            "bonus_value": 20,
            "bonus_type": "percentage",
            "rarity": "common"
        },
        
        # Legendary Traits
        {
            "name": "Phoenix Heart",
            "description": "Once per dungeon, automatically revive with 50% health when defeated.",
            "trait_type": "combat",
            "bonus_value": 50,
            "bonus_type": "percentage",
            "rarity": "legendary"
        },
        {
            "name": "Master of Arms",
            "description": "Can use any skill regardless of class restrictions, but with 20% reduced effectiveness.",
            "trait_type": "combat",
            "bonus_value": 20,
            "bonus_type": "percentage",
            "rarity": "legendary"
        },
        {
            "name": "Guild Legend",
            "description": "Increases guild share price by 10% just by being part of the roster.",
            "trait_type": "economic",
            "bonus_value": 10,
            "bonus_type": "percentage",
            "effect_type": "positive",
            "rarity": "legendary"
        },
        
        # Negative Traits
        {
            "name": "Slow Healer",
            "description": "Recovers from injuries 40% slower and receives 25% less healing from all sources.",
            "trait_type": "combat",
            "bonus_value": -40,
            "bonus_type": "healing_rate",
            "penalty_value": 25,
            "penalty_type": "healing_received",
            "effect_type": "negative",
            "rarity": "common"
        },
        {
            "name": "Fragile",
            "description": "Takes 20% more damage from all sources due to poor constitution.",
            "trait_type": "combat",
            "bonus_value": -20,
            "bonus_type": "damage_resistance",
            "effect_type": "negative", 
            "rarity": "common"
        },
        {
            "name": "Coward",
            "description": "Flees from combat when health drops below 60%, abandoning the party.",
            "trait_type": "combat",
            "bonus_value": 0,
            "bonus_type": "special",
            "effect_type": "negative",
            "rarity": "uncommon"
        },
        {
            "name": "Expensive Tastes",
            "description": "Demands 50% higher salary and premium equipment, draining guild resources.",
            "trait_type": "economic", 
            "bonus_value": -50,
            "bonus_type": "salary_cost",
            "effect_type": "negative",
            "rarity": "common"
        },
        {
            "name": "Antisocial",
            "description": "Reduces team morale and prevents other adventurers from gaining synergy bonuses.",
            "trait_type": "social",
            "bonus_value": -30,
            "bonus_type": "morale",
            "effect_type": "negative",
            "rarity": "uncommon"
        },
        
        # Mixed Traits (Positive + Negative)
        {
            "name": "Berserker's Curse",
            "description": "Deals 40% more damage but takes 25% more damage and cannot be healed during combat.",
            "trait_type": "combat",
            "bonus_value": 40,
            "bonus_type": "damage_dealt",
            "penalty_value": 25, 
            "penalty_type": "damage_taken",
            "effect_type": "mixed",
            "rarity": "rare"
        },
        {
            "name": "Perfectionist",
            "description": "Training provides 30% better results but costs 50% more gold due to demanding standards.",
            "trait_type": "training",
            "bonus_value": 30,
            "bonus_type": "training_effectiveness",
            "penalty_value": 50,
            "penalty_type": "training_cost", 
            "effect_type": "mixed",
            "rarity": "uncommon"
        },
        {
            "name": "Lucky Fool",
            "description": "15% chance to avoid negative effects, but 20% chance to fail when using skills.",
            "trait_type": "combat", 
            "bonus_value": 15,
            "bonus_type": "avoid_negative",
            "penalty_value": 20,
            "penalty_type": "skill_failure",
            "effect_type": "mixed",
            "rarity": "rare"
        },
        {
            "name": "Natural Born Leader",
            "description": "Provides +20% experience to party but becomes unavailable if not made party leader.",
            "trait_type": "social",
            "bonus_value": 20,
            "bonus_type": "party_experience",
            "penalty_value": 0,
            "penalty_type": "leadership_requirement",
            "effect_type": "mixed",
            "rarity": "rare"
        },
        {
            "name": "Treasure Obsessed", 
            "description": "Finds 35% more gold in dungeons but refuses to share loot with party members.",
            "trait_type": "economic",
            "bonus_value": 35,
            "bonus_type": "gold_found",
            "penalty_value": 100,
            "penalty_type": "loot_sharing",
            "effect_type": "mixed", 
            "rarity": "uncommon"
        }
    ]
    
    db = SessionLocal()
    try:
        for trait_data in traits_data:
            # Set default effect_type for traits that don't have it specified
            if "effect_type" not in trait_data:
                trait_data["effect_type"] = "positive"
            
            # Check if trait already exists
            existing_trait = db.query(Trait).filter(Trait.name == trait_data["name"]).first()
            if not existing_trait:
                trait = Trait(**trait_data)
                db.add(trait)
        
        db.commit()
        print(f"✅ Seeded {len(traits_data)} traits")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding traits: {e}")
    finally:
        db.close()

def main():
    """Seed skills and traits"""
    print("🌱 Seeding Skills and Traits...")
    
    seed_skills()
    seed_traits()
    
    print("✅ Skills and Traits seeding complete!")

if __name__ == "__main__":
    main()