#!/usr/bin/env python3
"""
Generate initial pool of recruitable adventurers with skills and traits
"""

import random
from app.models.database import SessionLocal
from app.models.adventurer import Adventurer, Skill, Trait, AdventurerClass, AdventurerSeniority, AdventurerRole
from app.models.game_session import GameSession

# Fantasy name pools for generating adventurers
FIRST_NAMES = [
    # Male names
    "Aiden", "Bjorn", "Cedric", "Darius", "Erik", "Finn", "Gareth", "Hank", "Ivan", "Jasper",
    "Kael", "Liam", "Magnus", "Nolan", "Owen", "Pierce", "Quinn", "Raven", "Soren", "Thane",
    "Ulric", "Victor", "Willem", "Xander", "York", "Zane",
    
    # Female names
    "Aria", "Brenna", "Cora", "Diana", "Elara", "Freya", "Gwen", "Hazel", "Iris", "Jora",
    "Kira", "Luna", "Mira", "Nora", "Olivia", "Piper", "Quinn", "Ruby", "Sage", "Tara",
    "Una", "Vera", "Wren", "Xara", "Yara", "Zoe"
]

LAST_NAMES = [
    "Ironforge", "Stormwind", "Brightblade", "Shadowmere", "Goldleaf", "Flameheart", "Frostborn",
    "Earthshaker", "Windwalker", "Starfall", "Moonbane", "Sunspear", "Darkbane", "Lightbringer",
    "Swiftstrike", "Stronghammer", "Shieldheart", "Bloodfang", "Whitehawk", "Blackthorn",
    "Silverleaf", "Copperbeard", "Ironwill", "Steelclaw", "Firemane", "Icevein", "Stonefist",
    "Lightfoot", "Deepdelver", "Highmountain", "Lowbrook", "Fairwind", "Grimheart", "Brightshot"
]

def generate_adventurer_name():
    """Generate a fantasy name for an adventurer"""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"

def generate_base_stats(adventurer_class, seniority):
    """Generate base stats using the new 5-stat system: Drive, Efficiency, Resilience, Insight, Luck"""
    
    # Base stat templates by class (new 5-stat system, 4 classes only)
    base_stat_templates = {
        "warrior": {"hp": 110, "drive": 15, "efficiency": 8, "resilience": 14, "insight": 6, "luck": 8},
        "archer": {"hp": 80, "drive": 10, "efficiency": 15, "resilience": 8, "insight": 9, "luck": 12},
        "mage": {"hp": 70, "drive": 6, "efficiency": 9, "resilience": 7, "insight": 16, "luck": 11},
        "paladin": {"hp": 105, "drive": 12, "efficiency": 7, "resilience": 13, "insight": 11, "luck": 9},
    }
    
    # Seniority multipliers
    seniority_multipliers = {
        "junior": 0.8,   # 80% of base stats
        "mid": 1.0,      # 100% of base stats
        "senior": 1.3    # 130% of base stats
    }
    
    base_template = base_stat_templates.get(adventurer_class, base_stat_templates["warrior"])
    multiplier = seniority_multipliers.get(seniority, 1.0)
    
    # Apply random variation (±15%) and seniority multiplier
    stats = {}
    for stat, base_value in base_template.items():
        variation = random.uniform(0.85, 1.15)  # ±15% variation
        final_value = int(base_value * multiplier * variation)
        
        # Ensure minimum values
        if stat == "hp":
            stats["max_hp"] = max(final_value, 50)
            stats["current_hp"] = stats["max_hp"]
        else:
            stats[stat] = max(final_value, 5)
    
    return stats

def assign_skills_to_adventurer(db, adventurer, adventurer_class):
    """Assign appropriate skills based on class and randomness"""
    # Get all available skills
    all_skills = db.query(Skill).all()
    
    # Filter skills for this class
    class_skills = []
    universal_skills = []
    
    for skill in all_skills:
        if skill.restricted_to_classes is None:
            universal_skills.append(skill)
        elif adventurer_class in skill.restricted_to_classes.split(','):
            class_skills.append(skill)
    
    # Determine number of skills based on seniority
    skill_count = {
        "junior": random.randint(2, 3),
        "mid": random.randint(3, 4), 
        "senior": random.randint(4, 6)
    }[adventurer.seniority]
    
    assigned_skills = []
    
    # Always get at least 1 class-specific skill if available
    if class_skills:
        assigned_skills.append(random.choice(class_skills))
        skill_count -= 1
    
    # Always get First Aid (universal healing)
    first_aid = next((s for s in universal_skills if s.name == "First Aid"), None)
    if first_aid and first_aid not in assigned_skills:
        assigned_skills.append(first_aid)
        skill_count -= 1
    
    # Fill remaining slots with mix of class and universal skills
    available_skills = class_skills + universal_skills
    available_skills = [s for s in available_skills if s not in assigned_skills]
    
    while skill_count > 0 and available_skills:
        skill = random.choice(available_skills)
        assigned_skills.append(skill)
        available_skills.remove(skill)
        skill_count -= 1
    
    # Assign skills to adventurer
    for skill in assigned_skills:
        adventurer.add_skill(skill)

def assign_traits_to_adventurer(db, adventurer):
    """Assign traits based on seniority and randomness"""
    all_traits = db.query(Trait).all()
    
    # Filter traits by rarity for appropriate distribution
    common_traits = [t for t in all_traits if t.rarity == "common"]
    uncommon_traits = [t for t in all_traits if t.rarity == "uncommon"]
    rare_traits = [t for t in all_traits if t.rarity == "rare"]
    legendary_traits = [t for t in all_traits if t.rarity == "legendary"]
    
    # Determine number of traits based on seniority
    trait_count = {
        "junior": random.randint(1, 2),
        "mid": random.randint(2, 3),
        "senior": random.randint(3, 4)
    }[adventurer.seniority]
    
    assigned_traits = []
    
    for _ in range(trait_count):
        # Weighted random selection based on rarity
        rarity_roll = random.randint(1, 100)
        
        if rarity_roll <= 5 and legendary_traits:  # 5% legendary
            trait_pool = legendary_traits
        elif rarity_roll <= 20 and rare_traits:    # 15% rare  
            trait_pool = rare_traits
        elif rarity_roll <= 45 and uncommon_traits: # 25% uncommon
            trait_pool = uncommon_traits
        else:  # 55% common
            trait_pool = common_traits
        
        # Remove already assigned traits from pool
        available_traits = [t for t in trait_pool if t not in assigned_traits]
        
        if available_traits:
            trait = random.choice(available_traits)
            assigned_traits.append(trait)
    
    # Assign traits to adventurer
    for trait in assigned_traits:
        adventurer.add_trait(trait)

def generate_adventurer(db, game_session_id=None):
    """Generate a single adventurer with appropriate stats, skills, and traits"""
    
    # Generate basic info
    name = generate_adventurer_name()
    adventurer_class = random.choice(["warrior", "archer", "mage", "paladin"])
    seniority = random.choice(list(AdventurerSeniority)).value
    role = Adventurer.get_role_for_class(adventurer_class)
    
    # Generate growth rates based on class and seniority
    growth_rates = Adventurer.generate_growth_rates(adventurer_class, seniority)
    
    # Generate base stats based on class and seniority
    base_stats = generate_base_stats(adventurer_class, seniority)
    
    # Calculate hire cost based on seniority and total stats
    seniority_cost = {"junior": 300, "mid": 500, "senior": 800}[seniority]
    
    # Calculate stat bonus (higher stats = higher cost) - new 5-stat system
    stat_total = sum([
        base_stats["drive"], base_stats["efficiency"], base_stats["resilience"],
        base_stats["insight"], base_stats["luck"]
    ])
    expected_total = 50  # Expected average total for new 5-stat system
    stat_bonus = max(0, stat_total - expected_total) * 8
    
    hire_cost = seniority_cost + stat_bonus
    
    # Calculate weekly salary (typically 8-15% of hire cost)
    base_salary = {"junior": 25, "mid": 45, "senior": 75}[seniority]
    salary_stat_bonus = max(0, stat_total - expected_total) * 1
    weekly_salary = base_salary + salary_stat_bonus
    
    # Create adventurer
    adventurer = Adventurer(
        name=name,
        game_session_id=game_session_id,
        guild_id=None,  # Available for hire
        adventurer_class=adventurer_class,
        seniority=seniority,
        role=role,
        is_available=True,
        hire_cost=hire_cost,
        weekly_salary=weekly_salary,
        
        # Base stats (new 5-stat system)
        max_hp=base_stats["max_hp"],
        current_hp=base_stats["current_hp"],
        drive=base_stats["drive"],
        efficiency=base_stats["efficiency"],
        resilience=base_stats["resilience"],
        insight=base_stats["insight"],
        luck=base_stats["luck"],
        
        # Condition stats (Uma Musume style)
        morale=random.randint(60, 90),
        stamina=random.randint(80, 100),
        
        # Growth rates
        **growth_rates
    )
    
    db.add(adventurer)
    db.flush()  # Get the ID for relationships
    
    # Assign skills and traits
    assign_skills_to_adventurer(db, adventurer, adventurer_class)
    assign_traits_to_adventurer(db, adventurer)
    
    return adventurer

def seed_adventurers_for_session(db, game_session_id, count=20):
    """Generate a pool of adventurers for a specific game session"""
    adventurers = []
    
    print(f"🧙‍♂️ Generating {count} adventurers for game session {game_session_id}...")
    
    for i in range(count):
        adventurer = generate_adventurer(db, game_session_id)
        adventurers.append(adventurer)
        
        if (i + 1) % 5 == 0:
            print(f"   Generated {i + 1}/{count} adventurers...")
    
    db.commit()
    print(f"✅ Generated {len(adventurers)} adventurers")
    
    # Show some examples
    print("\n📋 Sample Generated Adventurers:")
    for i, adv in enumerate(adventurers[:5]):
        skills = [s.name for s in adv.skills]
        traits = [f"{t.name} ({t.rarity})" for t in adv.traits]
        stats = f"DRV:{adv.drive} EFF:{adv.efficiency} RES:{adv.resilience} INS:{adv.insight} LCK:{adv.luck}"
        condition = f"Morale:{adv.morale} Stamina:{adv.stamina} ({adv.condition_status})"
        
        print(f"   {i+1}. {adv.name} - {adv.class_display_name} {adv.seniority_display_name}")
        print(f"      💰 Hire: {adv.hire_cost}g | 💳 Salary: {adv.weekly_salary}g/week | ❤️ HP: {adv.max_hp}")
        print(f"      📊 {stats}")
        print(f"      🎭 {condition}")
        print(f"      🗡️ Skills: {', '.join(skills)}")
        print(f"      ✨ Traits: {', '.join(traits)}")
        print()
    
    return adventurers

def main():
    """Generate adventurers for all existing game sessions"""
    db = SessionLocal()
    try:
        # Get all game sessions
        sessions = db.query(GameSession).all()
        
        if not sessions:
            print("❌ No game sessions found. Create a player and game session first.")
            return
        
        total_generated = 0
        
        for session in sessions:
            # Check if session already has adventurers
            existing_count = db.query(Adventurer).filter(
                Adventurer.game_session_id == session.id,
                Adventurer.is_available == True
            ).count()
            
            if existing_count > 0:
                print(f"⏭️  Session {session.id} already has {existing_count} adventurers, skipping...")
                continue
            
            # Generate adventurers for this session
            adventurers = seed_adventurers_for_session(db, session.id, 20)
            total_generated += len(adventurers)
        
        print(f"\n🎉 Adventurer generation complete!")
        print(f"📊 Total adventurers generated: {total_generated}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error generating adventurers: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()