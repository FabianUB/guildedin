from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

from .database import Base

class ActivityType(PyEnum):
    DUNGEON_BID = "dungeon_bid"
    DUNGEON_COMPLETE = "dungeon_complete"
    FACILITY_UPGRADE = "facility_upgrade"
    ADVENTURER_RECRUIT = "adventurer_recruit"
    MARKET_MANIPULATION = "market_manipulation"
    LINKEDIN_POST = "linkedin_post"
    STRATEGIC_PARTNERSHIP = "strategic_partnership"

class BotMarketActivity(Base):
    """
    Tracks all bot guild activities for generating realistic LinkedIn-style posts
    and market behavior within a player's isolated game session.
    """
    __tablename__ = "bot_market_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_guild_id = Column(Integer, ForeignKey("bot_guilds.id"), nullable=False, index=True)
    game_session_id = Column(Integer, ForeignKey("game_sessions.id"), nullable=False, index=True)
    
    # Activity details
    activity_type = Column(Enum(ActivityType), nullable=False)
    game_day = Column(Integer, nullable=False)  # When this activity occurred
    
    # Activity data
    title = Column(String(200))  # LinkedIn post title
    content = Column(Text)       # Post content or activity description
    activity_data = Column(JSON) # Structured data about the activity
    
    # Results and impact
    gold_change = Column(Integer, default=0)      # Financial impact
    share_price_change = Column(Float, default=0.0) # Stock impact %
    reputation_change = Column(Float, default=0.0)  # Public perception impact
    
    # Engagement (for LinkedIn posts)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    # Activity success/failure
    was_successful = Column(Boolean, default=True)
    success_score = Column(Float, default=50.0)  # 0-100 scale
    
    # Visibility and timing
    is_public = Column(Boolean, default=True)    # Whether this generates a LinkedIn post
    post_generated = Column(Boolean, default=False)
    post_generated_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    bot_guild = relationship("BotGuild", back_populates="market_activities")
    game_session = relationship("GameSession", back_populates="market_events")
    
    def __repr__(self):
        return f"<BotMarketActivity(id={self.id}, type={self.activity_type}, guild={self.bot_guild_id})>"
    
    def generate_linkedin_post(self):
        """Generate a LinkedIn-style post based on this activity"""
        if self.post_generated or not self.is_public:
            return None
            
        post_templates = {
            ActivityType.DUNGEON_COMPLETE: [
                "🎉 Thrilled to announce our team successfully cleared the {dungeon_name}! Our strategic approach to {challenge} really paid off. Earned {gold}G in completion bonuses. #TeamWork #Results",
                "Just wrapped up an incredible expedition to {dungeon_name}. The challenges were intense but our {team_strength} training showed. ROI: {roi}%. #Leadership #Excellence",
                "Another milestone achieved! 🏆 {dungeon_name} cleared with zero casualties. Our investment in {facility} really made the difference. #Innovation #GrowthMindset"
            ],
            
            ActivityType.DUNGEON_BID: [
                "Excited to secure exclusive access to {dungeon_name}! Our bid of {bid_amount}G demonstrates our commitment to premium opportunities. #StrategicInvestment #MarketLeader",
                "Sometimes you have to bid aggressively to win. Just secured {dungeon_name} for {bid_amount}G. The potential returns justify the investment. #BoldMoves #Calculated Risk",
                "Won the competitive bidding for {dungeon_name}! Our market intelligence and timing were key factors. Looking forward to the expedition. #WinningStrategy #MarketTiming"
            ],
            
            ActivityType.FACILITY_UPGRADE: [
                "Proud to announce our {facility_name} upgrade is complete! This {cost}G investment will boost our team's efficiency by {efficiency}%. #ContinuousImprovement #TeamDevelopment",
                "Investing in our people is investing in our future. Our new {facility_name} facility will transform how we approach challenges. #PeopleFirst #Innovation",
                "Just completed a major infrastructure upgrade. Our {facility_name} is now state-of-the-art. This positions us perfectly for Q{quarter} growth. #Infrastructure #ForwardThinking"
            ],
            
            ActivityType.ADVENTURER_RECRUIT: [
                "Welcome to the team, {adventurer_name}! Their expertise in {skill} will be invaluable for our upcoming projects. #Hiring #TeamGrowth #TalentAcquisition",
                "Excited to announce we've hired a {class} specialist! Our recruiting team found an absolute gem. #NewHire #TeamExpansion #ExcellentTalent",
                "Adding world-class talent to our roster. {adventurer_name} brings {years} years of {specialty} experience. #TalentAcquisition #TeamBuilding"
            ]
        }
        
        templates = post_templates.get(self.activity_type, ["Great progress on our latest project! #Success"])
        
        # Select template based on bot personality and activity data
        import random
        template = random.choice(templates)
        
        # Fill in template variables from activity_data
        try:
            post_content = template.format(**self.activity_data)
        except KeyError:
            # Fallback if template variables don't match
            post_content = f"Exciting developments at {self.bot_guild.name}! Our latest {self.activity_type.value.replace('_', ' ')} initiative is showing great results. #Growth #Success"
        
        self.title = post_content.split('.')[0]  # First sentence as title
        self.content = post_content
        self.post_generated = True
        self.post_generated_at = datetime.utcnow()
        
        return post_content
    
    def calculate_engagement(self):
        """Calculate realistic engagement numbers based on bot guild reputation"""
        base_likes = max(1, int(self.bot_guild.public_reputation / 5))
        base_comments = max(0, int(base_likes / 4))
        base_shares = max(0, int(base_likes / 8))
        
        # Activity type modifiers
        multipliers = {
            ActivityType.DUNGEON_COMPLETE: 1.5,
            ActivityType.FACILITY_UPGRADE: 0.8,
            ActivityType.DUNGEON_BID: 1.2,
            ActivityType.ADVENTURER_RECRUIT: 0.9,
            ActivityType.LINKEDIN_POST: 1.0
        }
        
        multiplier = multipliers.get(self.activity_type, 1.0)
        
        # Success modifier
        success_modifier = 1.0 + (self.success_score - 50.0) / 100.0
        
        self.likes_count = int(base_likes * multiplier * success_modifier)
        self.comments_count = int(base_comments * multiplier * success_modifier)  
        self.shares_count = int(base_shares * multiplier * success_modifier)
        
        return {
            "likes": self.likes_count,
            "comments": self.comments_count,
            "shares": self.shares_count
        }