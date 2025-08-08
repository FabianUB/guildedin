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

def init_database():
    """Create all tables from scratch"""
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

if __name__ == "__main__":
    init_database()