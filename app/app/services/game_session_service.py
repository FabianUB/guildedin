import random
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from ..models.game_session import GameSession, GameDifficulty
from ..models.guild import Guild, GuildRank
from ..models.bot_guild import BotGuild, BotPersonalityType, BotBehaviorState
from ..models.bot_market_activity import BotMarketActivity, ActivityType

class GameSessionService:
    """Service for managing player game sessions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_new_session(
        self, 
        player_id: int, 
        guild_name: str,
        difficulty: GameDifficulty = GameDifficulty.NORMAL
    ) -> GameSession:
        """Create a new isolated game session for a player with custom guild name"""
        
        # Validate guild name is available within this session (when we create it)
        # For now, just clean the name
        clean_guild_name = guild_name.strip()
        if not clean_guild_name:
            clean_guild_name = "My Guild"
        
        # Create the game session
        session = GameSession(
            player_id=player_id,
            difficulty_level=difficulty,
            daily_action_limit=5,
            starting_gold=5000,
            market_volatility=1.0
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        # Create player's guild with custom name
        player_guild = self._create_player_guild(session.id, player_id, clean_guild_name)
        
        # Generate bot competitors
        bot_guilds = self._generate_bot_guilds(session.id)
        
        # Generate initial dungeons
        initial_dungeons = self._generate_initial_dungeons(session.id)
        
        return session
    
    def _create_player_guild(self, session_id: int, player_id: int, guild_name: str) -> Guild:
        """Create the player's starting guild with custom name"""
        
        # Create URL-friendly slug
        guild_slug = guild_name.lower().replace(" ", "-").replace("_", "-")
        
        guild = Guild(
            game_session_id=session_id,
            owner_id=player_id,
            name=guild_name,
            slug=guild_slug,
            tagline="Building the future of adventuring",
            description="A dynamic guild focused on innovation and strategic growth in the dungeon economy.",
            industry="Adventure Management",
            headquarters="Global Network",
            company_size="1-10 adventurers",
            gold=5000,
            guild_rank=GuildRank.D,
            share_price=100.0,
            exp_bank=0,
            is_recruiting=True
        )
        
        self.db.add(guild)
        self.db.commit()
        self.db.refresh(guild)
        
        return guild
    
    def _generate_bot_guilds(self, session_id: int) -> List[BotGuild]:
        """Generate AI competitor guilds for this session"""
        
        # Bot guild templates with realistic names and personalities
        bot_templates = [
            {
                "name": "AdventureCorp",
                "ceo_name": "Marcus Chen",
                "personality": BotPersonalityType.AGGRESSIVE_TRADER,
                "avatar": "📈",
                "gold": 6500,
                "share_price": 120.0
            },
            {
                "name": "DataDriven Dynamics", 
                "ceo_name": "Dr. Sarah Kim",
                "personality": BotPersonalityType.DATA_ANALYST,
                "avatar": "🧠",
                "gold": 4800,
                "share_price": 95.0
            },
            {
                "name": "Elite Endeavors",
                "ceo_name": "Victoria Sterling", 
                "personality": BotPersonalityType.NETWORKING_ELITE,
                "avatar": "🎭",
                "gold": 8200,
                "share_price": 145.0
            },
            {
                "name": "Steadfast Solutions",
                "ceo_name": "Robert Foundation",
                "personality": BotPersonalityType.CONSERVATIVE_BUILDER,
                "avatar": "🏗️", 
                "gold": 5200,
                "share_price": 105.0
            },
            {
                "name": "Synergy Specialists",
                "ceo_name": "Alexandra Bright",
                "personality": BotPersonalityType.CHARISMATIC_LEADER,
                "avatar": "⭐",
                "gold": 5800,
                "share_price": 115.0
            },
            {
                "name": "Opportunity Holdings",
                "ceo_name": "Viktor Sharpe",
                "personality": BotPersonalityType.OPPORTUNISTIC_SHARK,
                "avatar": "🦈",
                "gold": 4200,
                "share_price": 88.0
            }
        ]
        
        bot_guilds = []
        for template in bot_templates:
            bot_guild = BotGuild(
                game_session_id=session_id,
                name=template["name"],
                ceo_name=template["ceo_name"],
                ceo_avatar_emoji=template["avatar"],
                personality_type=template["personality"],
                current_behavior=BotBehaviorState.GROWING,
                gold=template["gold"],
                share_price=template["share_price"],
                guild_rank=GuildRank.D,
                aggression_level=random.uniform(0.3, 0.8),
                risk_tolerance=random.uniform(0.2, 0.9),
                market_focus=random.uniform(0.3, 0.7),
                recent_performance_score=random.uniform(40.0, 60.0),
                post_frequency_days=random.randint(2, 5),
                public_reputation=random.uniform(40.0, 70.0)
            )
            
            self.db.add(bot_guild)
            bot_guilds.append(bot_guild)
        
        self.db.commit()
        
        # Generate initial activities for bot guilds
        for bot_guild in bot_guilds:
            self._generate_initial_bot_activity(bot_guild)
        
        return bot_guilds
    
    def _generate_initial_bot_activity(self, bot_guild: BotGuild):
        """Generate some initial market activity for a bot guild"""
        
        # Create a founding activity
        activity = BotMarketActivity(
            bot_guild_id=bot_guild.id,
            game_session_id=bot_guild.game_session_id,
            activity_type=ActivityType.LINKEDIN_POST,
            game_day=1,
            title=f"Excited to announce the launch of {bot_guild.name}!",
            content=f"Thrilled to announce the official launch of {bot_guild.name}! "
                   f"As {bot_guild.ceo_name}, I'm committed to building the most innovative "
                   f"guild in the adventure economy. Looking forward to connecting with "
                   f"top-tier talent and exploring premium opportunities. #NewBeginnings #Innovation #GuildLife",
            activity_data={
                "type": "company_launch",
                "initial_investment": bot_guild.gold,
                "founding_vision": bot_guild.personality_description
            },
            was_successful=True,
            success_score=55.0,
            is_public=True
        )
        
        self.db.add(activity)
        
        # Generate engagement
        activity.calculate_engagement()
        
        self.db.commit()
    
    def _generate_initial_dungeons(self, session_id: int) -> List:
        """Generate some starting dungeons for discovery"""
        # This would create initial dungeons for the session
        # Implementation depends on dungeon generation system
        return []
    
    def get_player_current_session(self, player_id: int) -> Optional[GameSession]:
        """Get the player's current active game session"""
        return self.db.query(GameSession).filter(
            GameSession.player_id == player_id,
            GameSession.is_active == True
        ).first()