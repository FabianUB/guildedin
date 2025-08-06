import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.dungeon_progression import DungeonRun, MiningOperation, RunStatus, RoomState
from ..models.dungeon_system import Dungeon, DungeonStatus
from ..models.database import get_db

class DungeonTimeManager:
    """Handles real-time mechanics for dungeons"""
    
    def __init__(self):
        self.update_interval = 60  # Update every minute
        self.running = False
    
    async def start_background_tasks(self):
        """Start all background time-based tasks"""
        if self.running:
            return
        
        self.running = True
        
        # Start concurrent background tasks
        await asyncio.gather(
            self.update_mining_operations(),
            self.update_daily_time_limits(),
            self.check_dungeon_collapses(),
            self.process_dungeon_events()
        )
    
    async def update_mining_operations(self):
        """Update mining progress for all active operations"""
        while self.running:
            try:
                db = next(get_db())
                now = datetime.utcnow()
                
                # Get all active mining operations
                active_mining = db.query(MiningOperation).filter(
                    and_(
                        MiningOperation.is_active == True,
                        MiningOperation.is_completed == False
                    )
                ).all()
                
                for mining_op in active_mining:
                    # Calculate time elapsed since last update
                    time_elapsed = now - mining_op.last_update
                    hours_elapsed = time_elapsed.total_seconds() / 3600
                    
                    # Update progress
                    mining_op.hours_completed += hours_elapsed
                    mining_op.last_update = now
                    
                    # Calculate completion percentage
                    completion_pct = min(100.0, (mining_op.hours_completed / mining_op.total_duration_hours) * 100)
                    mining_op.completion_percentage = completion_pct
                    
                    # Extract resources based on progress
                    self._update_mining_resources(mining_op, completion_pct)
                    
                    # Check if completed
                    if completion_pct >= 100.0:
                        mining_op.is_completed = True
                        mining_op.is_active = False
                        
                        # Update room progress
                        room_progress = mining_op.room_progress
                        room_progress.state = RoomState.EXHAUSTED
                        room_progress.mining_completion_percent = 100.0
                
                db.commit()
                db.close()
                
            except Exception as e:
                print(f"Error updating mining operations: {e}")
            
            await asyncio.sleep(self.update_interval)
    
    async def update_daily_time_limits(self):
        """Reset daily time limits at midnight"""
        while self.running:
            try:
                db = next(get_db())
                now = datetime.utcnow()
                today = now.date()
                
                # Find runs that need daily reset
                runs_to_reset = db.query(DungeonRun).filter(
                    or_(
                        DungeonRun.last_reset_date.is_(None),
                        DungeonRun.last_reset_date < today
                    )
                ).all()
                
                for run in runs_to_reset:
                    run.today_time_used = 0
                    run.last_reset_date = today
                
                db.commit()
                db.close()
                
            except Exception as e:
                print(f"Error updating daily time limits: {e}")
            
            # Check every hour for midnight resets
            await asyncio.sleep(3600)
    
    async def check_dungeon_collapses(self):
        """Check for dungeons that should collapse due to time limits"""
        while self.running:
            try:
                db = next(get_db())
                now = datetime.utcnow()
                
                # Find dungeons that should collapse
                expiring_dungeons = db.query(Dungeon).filter(
                    and_(
                        Dungeon.dungeon_closes_at <= now,
                        Dungeon.status == DungeonStatus.ACTIVE
                    )
                ).all()
                
                for dungeon in expiring_dungeons:
                    await self._collapse_dungeon(db, dungeon)
                
                db.commit()
                db.close()
                
            except Exception as e:
                print(f"Error checking dungeon collapses: {e}")
            
            await asyncio.sleep(self.update_interval)
    
    async def process_dungeon_events(self):
        """Handle various dungeon events and state changes"""
        while self.running:
            try:
                db = next(get_db())
                
                # Process any pending dungeon events
                await self._process_contract_awards(db)
                await self._check_completion_conditions(db)
                
                db.commit()
                db.close()
                
            except Exception as e:
                print(f"Error processing dungeon events: {e}")
            
            await asyncio.sleep(self.update_interval * 5)  # Every 5 minutes
    
    def _update_mining_resources(self, mining_op: MiningOperation, completion_pct: float):
        """Calculate and update extracted resources based on mining progress"""
        target_resources = mining_op.target_resources
        current_resources = mining_op.resources_extracted
        
        for resource_type, total_amount in target_resources.items():
            # Calculate how much should be extracted at this completion level
            target_extracted = int((completion_pct / 100.0) * total_amount)
            current_extracted = current_resources.get(resource_type, 0)
            
            # Update if we should have more
            if target_extracted > current_extracted:
                current_resources[resource_type] = target_extracted
        
        mining_op.resources_extracted = current_resources
    
    async def _collapse_dungeon(self, db: Session, dungeon: Dungeon):
        """Handle dungeon collapse - apply penalties and close access"""
        dungeon.status = DungeonStatus.COLLAPSED
        
        # Find all active runs in this dungeon
        active_runs = db.query(DungeonRun).filter(
            and_(
                DungeonRun.dungeon_id == dungeon.id,
                DungeonRun.status.in_([RunStatus.ACTIVE, RunStatus.SUSPENDED])
            )
        ).all()
        
        # Apply failure penalties
        for run in active_runs:
            if not run.boss_defeated:
                run.status = RunStatus.FAILED
                run.failure_penalty_paid = dungeon.failure_penalty
                
                # Deduct penalty from guild treasury
                guild = run.guild
                guild.gold -= dungeon.failure_penalty
                
                # Update stock price negatively
                if hasattr(guild, 'share_price'):
                    penalty_impact = min(0.15, dungeon.failure_penalty / 10000)  # Max 15% drop
                    guild.share_price *= (1 - penalty_impact)
    
    async def _process_contract_awards(self, db: Session):
        """Process bidding results and award contracts"""
        # This will be implemented when we create the bidding system
        pass
    
    async def _check_completion_conditions(self, db: Session):
        """Check if any dungeons have been completed"""
        # Find runs that just defeated the boss
        completed_runs = db.query(DungeonRun).filter(
            and_(
                DungeonRun.boss_defeated == True,
                DungeonRun.status == RunStatus.ACTIVE
            )
        ).all()
        
        for run in completed_runs:
            run.status = RunStatus.COMPLETED
            run.completed_at = datetime.utcnow()
            
            # Award completion bonus
            run.completion_bonus_earned = run.dungeon.completion_bonus
            
            # Update guild treasury and stock price
            guild = run.guild
            guild.gold += run.dungeon.completion_bonus
            
            if hasattr(guild, 'share_price'):
                bonus_impact = min(0.25, run.dungeon.completion_bonus / 5000)  # Max 25% boost
                guild.share_price *= (1 + bonus_impact)
            
            # Mark dungeon as completed if this is first completion
            dungeon = run.dungeon
            if not dungeon.is_completed:
                dungeon.is_completed = True
                dungeon.completed_by_guild_id = guild.id
                dungeon.status = DungeonStatus.COMPLETED
    
    async def stop(self):
        """Stop all background tasks"""
        self.running = False

# Global instance
dungeon_time_manager = DungeonTimeManager()