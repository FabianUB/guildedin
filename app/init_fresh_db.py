#!/usr/bin/env python3
"""
Initialize a fresh database for GuildedIn
This script creates all tables from scratch without relying on migrations
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from app.models.database import Base, engine
from app.models.user import Player
from app.models.game_session import GameSession
from app.models.guild import Guild
from app.models.adventurer import Adventurer

def create_dev_user():
    """Create a development user with complete setup"""
    from sqlalchemy.orm import sessionmaker
    from app.auth import hash_password
    
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        print("👤 Creating development user...")
        
        # Create dev player
        hashed_password = hash_password("dev")
        dev_player = Player(
            email="dev@guildedin.com",
            username="dev",
            display_name="Dev Player",
            hashed_password=hashed_password,
            corporate_class="HR_MANAGER",
            is_active=True
        )
        db.add(dev_player)
        db.flush()  # Get the player ID
        
        # Create game session
        print("🎮 Creating game session...")
        game_session = GameSession(
            player_id=dev_player.id,
            current_week=1,
            current_quarter=1,
            current_year=1,
            is_active=True
        )
        db.add(game_session)
        db.flush()  # Get the game session ID
        
        # Create guild
        print("🏰 Creating guild...")
        guild = Guild(
            name="Dev Guild",
            owner_id=dev_player.id,
            game_session_id=game_session.id,
            gold=5000,
            guild_exp=100  # Start with some EXP for testing guild builds
        )
        db.add(guild)
        
        db.commit()
        
        print("✅ Development setup complete!")
        print("📧 Email: dev@guildedin.com")
        print("🔑 Password: dev")
        print("🏰 Guild: Dev Guild")
        print("💰 Starting Gold: 5,000G")
        print("⭐ Starting Guild EXP: 100")
        
        return dev_player.id, game_session.id
        
    except Exception as e:
        print(f"❌ Error creating dev user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_database():
    """Create all tables from scratch and set up dev environment"""
    print("🗄️ Initializing fresh GuildedIn database...")
    
    # Remove existing database if it exists
    db_path = app_dir / "guildedin.db"
    if db_path.exists():
        print(f"🗑️ Removing existing database: {db_path}")
        db_path.unlink()
    
    print("🔨 Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database initialization complete!")
    print(f"📂 Database location: {db_path}")
    
    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"📋 Created {len(tables)} tables: {', '.join(tables)}")
    
    # Create development user with complete setup
    player_id, game_session_id = create_dev_user()
    
    return player_id, game_session_id

if __name__ == "__main__":
    init_database()