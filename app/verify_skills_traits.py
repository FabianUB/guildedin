#!/usr/bin/env python3
"""
Quick verification script to show the seeded Skills and Traits
"""

from app.models.database import SessionLocal
from app.models.adventurer import Skill, Trait

def verify_skills_traits():
    db = SessionLocal()
    try:
        # Count totals
        skill_count = db.query(Skill).count()
        trait_count = db.query(Trait).count()
        
        print(f"📊 Database Contents:")
        print(f"   Skills: {skill_count}")
        print(f"   Traits: {trait_count}")
        print()
        
        # Show skill examples by type
        print("⚔️ Sample Skills by Type:")
        skill_types = db.query(Skill.skill_type).distinct().all()
        for (skill_type,) in skill_types:
            skills = db.query(Skill).filter(Skill.skill_type == skill_type).limit(3).all()
            print(f"   {skill_type.upper()}:")
            for skill in skills:
                positions = skill.usable_positions if skill.usable_positions != "1,2,3,4" else "Any"
                print(f"     • {skill.name} (positions: {positions}, targets: {skill.target_type})")
        print()
        
        # Show trait examples by effect type
        print("✨ Sample Traits by Effect:")
        effect_types = db.query(Trait.effect_type).distinct().all()
        for (effect_type,) in effect_types:
            traits = db.query(Trait).filter(Trait.effect_type == effect_type).limit(3).all()
            print(f"   {effect_type.upper()}:")
            for trait in traits:
                rarity = f"({trait.rarity})" if trait.rarity else ""
                print(f"     • {trait.name} {rarity}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_skills_traits()