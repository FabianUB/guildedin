from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.dungeon_progression import DungeonRun, RoomProgress, MiningOperation, DungeonBattle, RunStatus, RoomState
from ..models.dungeon_system import DungeonRoom, Dungeon
from ..models.adventurer import Adventurer

class DungeonProgressionService:
    """Handles dungeon room progression and state management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def enter_dungeon(self, run_id: int, adventurer_ids: List[int]) -> Dict:
        """Start or resume a dungeon run with selected adventurers"""
        
        run = self.db.query(DungeonRun).filter(DungeonRun.id == run_id).first()
        if not run:
            return {"success": False, "error": "Dungeon run not found"}
        
        # Check if guild has time remaining today
        time_check = self._check_daily_time_limit(run)
        if not time_check["can_enter"]:
            return {"success": False, "error": time_check["reason"]}
        
        # Validate adventurers belong to guild and are available
        adventurers = self.db.query(Adventurer).filter(
            and_(
                Adventurer.id.in_(adventurer_ids),
                Adventurer.guild_id == run.guild_id
            )
        ).all()
        
        if len(adventurers) != len(adventurer_ids):
            return {"success": False, "error": "Some adventurers not found or don't belong to guild"}
        
        # Update run status and party
        run.status = RunStatus.ACTIVE
        run.party_adventurers = adventurer_ids
        run.party_size = len(adventurer_ids)
        run.last_activity = datetime.utcnow()
        
        if not run.started_at:
            run.started_at = datetime.utcnow()
        
        # Initialize room progress if first time
        self._initialize_room_progress(run)
        
        self.db.commit()
        
        return {
            "success": True,
            "message": "Entered dungeon successfully",
            "current_room": run.current_room,
            "party_size": run.party_size,
            "time_remaining_today": self._get_remaining_time_today(run)
        }
    
    def advance_to_room(self, run_id: int, target_room: int) -> Dict:
        """Move party to the next room"""
        
        run = self.db.query(DungeonRun).filter(DungeonRun.id == run_id).first()
        if not run:
            return {"success": False, "error": "Dungeon run not found"}
        
        if run.status != RunStatus.ACTIVE:
            return {"success": False, "error": "Dungeon run not active"}
        
        # Validate room progression (can only advance one room at a time)
        if target_room != run.current_room + 1:
            return {"success": False, "error": "Can only advance one room at a time"}
        
        # Check if previous room is cleared (if not at entrance)
        if run.current_room > 0:
            prev_room_progress = self.db.query(RoomProgress).filter(
                and_(
                    RoomProgress.run_id == run_id,
                    RoomProgress.room_id == self._get_room_id(run.dungeon_id, run.current_room)
                )
            ).first()
            
            if not prev_room_progress or prev_room_progress.state not in [RoomState.CLEARED, RoomState.MINING, RoomState.EXHAUSTED]:
                return {"success": False, "error": "Previous room not cleared"}
        
        # Check if target room exists
        target_room_obj = self.db.query(DungeonRoom).filter(
            and_(
                DungeonRoom.dungeon_id == run.dungeon_id,
                DungeonRoom.room_number == target_room
            )
        ).first()
        
        if not target_room_obj:
            return {"success": False, "error": "Target room does not exist"}
        
        # Update run position
        run.current_room = target_room
        run.furthest_room_reached = max(run.furthest_room_reached, target_room)
        run.last_activity = datetime.utcnow()
        
        # Create/update room progress
        room_progress = self._get_or_create_room_progress(run_id, target_room_obj.id, run.guild_id)
        
        if room_progress.state == RoomState.UNEXPLORED:
            room_progress.state = RoomState.COMBAT
            room_progress.first_entered_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "success": True,
            "current_room": target_room,
            "room_info": self._get_room_info(target_room_obj),
            "room_state": room_progress.state.value,
            "can_advance": False  # Must clear room first
        }
    
    def initiate_combat(self, run_id: int, room_number: int) -> Dict:
        """Start combat in current room"""
        
        run = self.db.query(DungeonRun).filter(DungeonRun.id == run_id).first()
        if not run:
            return {"success": False, "error": "Run not found"}
        
        if run.current_room != room_number:
            return {"success": False, "error": "Not in specified room"}
        
        room = self.db.query(DungeonRoom).filter(
            and_(
                DungeonRoom.dungeon_id == run.dungeon_id,
                DungeonRoom.room_number == room_number
            )
        ).first()
        
        room_progress = self._get_or_create_room_progress(run_id, room.id, run.guild_id)
        
        if room_progress.state != RoomState.COMBAT:
            return {"success": False, "error": "Room not ready for combat"}
        
        # Get party adventurers
        adventurers = self.db.query(Adventurer).filter(
            Adventurer.id.in_(run.party_adventurers)
        ).all()
        
        # Simulate combat (placeholder for future auto-battler)
        combat_result = self._simulate_combat(adventurers, room.enemy_configuration, room.combat_difficulty)
        
        # Create battle record
        battle = DungeonBattle(
            run_id=run_id,
            room_id=room.id,
            room_number=room_number,
            participating_adventurers=self._serialize_adventurers(adventurers),
            enemy_configuration=room.enemy_configuration,
            result=combat_result["result"],
            battle_duration_minutes=combat_result["duration"],
            damage_dealt=combat_result["damage_dealt"],
            damage_taken=combat_result["damage_taken"],
            exp_gained=combat_result["exp_gained"],
            loot_gained=combat_result["loot_gained"],
            battle_log=combat_result["battle_log"]
        )
        
        self.db.add(battle)
        
        # Update room progress based on result
        if combat_result["result"] == "victory":
            room_progress.state = RoomState.CLEARED
            room_progress.combat_completed = True
            room_progress.combat_completed_at = datetime.utcnow()
            room_progress.loot_collected = combat_result["loot_gained"]
            
            # Update run statistics
            run.rooms_cleared += 1
            run.enemies_defeated += combat_result["enemies_killed"]
            
            # Add loot to run totals
            self._add_loot_to_run(run, combat_result["loot_gained"])
            
            # Check if boss room
            if room.is_boss_room:
                run.boss_defeated = True
                run.status = RunStatus.COMPLETED
                run.completed_at = datetime.utcnow()
        
        elif combat_result["result"] == "defeat":
            # Party defeated - end run
            run.status = RunStatus.FAILED
            room_progress.combat_result = "defeat"
        
        # Update adventurer experience
        for adventurer in adventurers:
            adventurer.experience += combat_result["exp_gained"] // len(adventurers)
        
        self.db.commit()
        
        return {
            "success": True,
            "result": combat_result["result"],
            "loot_gained": combat_result["loot_gained"],
            "exp_gained": combat_result["exp_gained"],
            "battle_duration": combat_result["duration"],
            "room_cleared": combat_result["result"] == "victory",
            "can_advance": combat_result["result"] == "victory" and not room.is_boss_room,
            "boss_defeated": room.is_boss_room and combat_result["result"] == "victory"
        }
    
    def retreat_from_dungeon(self, run_id: int) -> Dict:
        """Leave dungeon and return to entrance"""
        
        run = self.db.query(DungeonRun).filter(DungeonRun.id == run_id).first()
        if not run:
            return {"success": False, "error": "Run not found"}
        
        # Update run status
        run.status = RunStatus.SUSPENDED
        run.current_room = 0  # Back to entrance
        run.last_activity = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "success": True,
            "message": "Successfully retreated from dungeon",
            "loot_preserved": True,
            "can_resume": True
        }
    
    def start_mining_operation(self, run_id: int, room_number: int, miners_count: int = 1) -> Dict:
        """Start mining operation in a cleared room"""
        
        run = self.db.query(DungeonRun).filter(DungeonRun.id == run_id).first()
        if not run:
            return {"success": False, "error": "Run not found"}
        
        room = self.db.query(DungeonRoom).filter(
            and_(
                DungeonRoom.dungeon_id == run.dungeon_id,
                DungeonRoom.room_number == room_number
            )
        ).first()
        
        room_progress = self.db.query(RoomProgress).filter(
            and_(
                RoomProgress.run_id == run_id,
                RoomProgress.room_id == room.id
            )
        ).first()
        
        if not room_progress or room_progress.state != RoomState.CLEARED:
            return {"success": False, "error": "Room not cleared or not accessible"}
        
        # Check if mining already started
        existing_mining = self.db.query(MiningOperation).filter(
            RoomProgress.room_progress_id == room_progress.id
        ).first()
        
        if existing_mining:
            return {"success": False, "error": "Mining operation already in progress"}
        
        # Create mining operation
        mining_op = MiningOperation(
            run_id=run_id,
            room_progress_id=room_progress.id,
            guild_id=run.guild_id,
            miners_assigned=miners_count,
            total_duration_hours=room.mining_duration_hours,
            target_resources=room.mining_resources,
            estimated_completion=datetime.utcnow() + timedelta(hours=room.mining_duration_hours)
        )
        
        self.db.add(mining_op)
        
        # Update room state
        room_progress.state = RoomState.MINING
        room_progress.mining_started_at = datetime.utcnow()
        
        # Update run statistics
        run.mining_operations += 1
        
        self.db.commit()
        
        return {
            "success": True,
            "mining_duration_hours": room.mining_duration_hours,
            "estimated_completion": mining_op.estimated_completion.isoformat(),
            "target_resources": room.mining_resources,
            "miners_assigned": miners_count
        }
    
    def get_dungeon_status(self, run_id: int) -> Dict:
        """Get complete status of dungeon run"""
        
        run = self.db.query(DungeonRun).filter(DungeonRun.id == run_id).first()
        if not run:
            return {"error": "Run not found"}
        
        # Get all room progress
        rooms_progress = self.db.query(RoomProgress).filter(
            RoomProgress.run_id == run_id
        ).all()
        
        # Get active mining operations
        active_mining = self.db.query(MiningOperation).filter(
            and_(
                MiningOperation.run_id == run_id,
                MiningOperation.is_active == True
            )
        ).all()
        
        return {
            "run_id": run_id,
            "status": run.status.value,
            "current_room": run.current_room,
            "furthest_room": run.furthest_room_reached,
            "rooms_cleared": run.rooms_cleared,
            "total_rooms": run.dungeon.total_rooms,
            "time_used_today": run.today_time_used,
            "time_limit_today": run.time_limit_per_day,
            "total_loot": run.total_loot_gained,
            "party_size": run.party_size,
            "boss_defeated": run.boss_defeated,
            "rooms_progress": [self._serialize_room_progress(rp) for rp in rooms_progress],
            "active_mining": [self._serialize_mining_operation(mo) for mo in active_mining]
        }
    
    def _check_daily_time_limit(self, run: DungeonRun) -> Dict:
        """Check if guild can enter dungeon today"""
        if run.today_time_used >= run.time_limit_per_day:
            return {"can_enter": False, "reason": "Daily time limit exceeded"}
        
        return {"can_enter": True, "remaining_minutes": run.time_limit_per_day - run.today_time_used}
    
    def _get_remaining_time_today(self, run: DungeonRun) -> int:
        """Get remaining time in minutes for today"""
        return max(0, run.time_limit_per_day - run.today_time_used)
    
    def _initialize_room_progress(self, run: DungeonRun):
        """Initialize room progress for new runs"""
        dungeon_rooms = self.db.query(DungeonRoom).filter(
            DungeonRoom.dungeon_id == run.dungeon_id
        ).all()
        
        for room in dungeon_rooms:
            existing = self.db.query(RoomProgress).filter(
                and_(
                    RoomProgress.run_id == run.id,
                    RoomProgress.room_id == room.id
                )
            ).first()
            
            if not existing:
                room_progress = RoomProgress(
                    run_id=run.id,
                    room_id=room.id,
                    guild_id=run.guild_id,
                    state=RoomState.UNEXPLORED
                )
                self.db.add(room_progress)
    
    def _get_or_create_room_progress(self, run_id: int, room_id: int, guild_id: int) -> RoomProgress:
        """Get existing room progress or create new one"""
        room_progress = self.db.query(RoomProgress).filter(
            and_(
                RoomProgress.run_id == run_id,
                RoomProgress.room_id == room_id
            )
        ).first()
        
        if not room_progress:
            room_progress = RoomProgress(
                run_id=run_id,
                room_id=room_id,
                guild_id=guild_id,
                state=RoomState.UNEXPLORED
            )
            self.db.add(room_progress)
        
        return room_progress
    
    def _get_room_id(self, dungeon_id: int, room_number: int) -> int:
        """Get room ID by dungeon and room number"""
        room = self.db.query(DungeonRoom).filter(
            and_(
                DungeonRoom.dungeon_id == dungeon_id,
                DungeonRoom.room_number == room_number
            )
        ).first()
        return room.id if room else None
    
    def _get_room_info(self, room: DungeonRoom) -> Dict:
        """Serialize room information"""
        return {
            "id": room.id,
            "number": room.room_number,
            "name": room.name,
            "description": room.description,
            "is_boss_room": room.is_boss_room,
            "combat_difficulty": room.combat_difficulty,
            "enemy_count": len(room.enemy_configuration.get("minions", {})) + len(room.enemy_configuration.get("boss", {})),
            "mining_resources": room.mining_resources,
            "mining_duration": room.mining_duration_hours
        }
    
    def _simulate_combat(self, adventurers: List[Adventurer], enemies: Dict, difficulty: int) -> Dict:
        """Simulate auto-battle combat (placeholder implementation)"""
        # This is a simplified simulation - will be replaced with proper auto-battler
        
        party_power = sum(adv.level * 10 + adv.strength + adv.dexterity for adv in adventurers)
        enemy_power = difficulty * 10
        
        # Simple probability-based outcome
        success_chance = min(0.95, max(0.05, party_power / (party_power + enemy_power)))
        
        import random
        if random.random() < success_chance:
            result = "victory"
            exp_gained = difficulty * 5
            gold_gained = difficulty * 3
            damage_taken = random.randint(10, 30)
        else:
            result = "defeat"
            exp_gained = difficulty * 2  # Partial exp for effort
            gold_gained = 0
            damage_taken = random.randint(50, 80)
        
        return {
            "result": result,
            "duration": random.randint(5, 15),  # 5-15 minutes
            "damage_dealt": random.randint(100, 300),
            "damage_taken": damage_taken,
            "exp_gained": exp_gained,
            "loot_gained": {"gold": gold_gained, "exp": exp_gained},
            "enemies_killed": len(enemies.get("minions", [])) if result == "victory" else 0,
            "battle_log": [f"Combat simulation: {result}"]
        }
    
    def _serialize_adventurers(self, adventurers: List[Adventurer]) -> List[Dict]:
        """Serialize adventurers for battle record"""
        return [
            {
                "id": adv.id,
                "name": adv.display_name,
                "class": adv.adventurer_class.value,
                "level": adv.level,
                "health": adv.current_health,
                "stats": {
                    "strength": adv.strength,
                    "dexterity": adv.dexterity,
                    "constitution": adv.constitution,
                    "intelligence": adv.intelligence
                }
            }
            for adv in adventurers
        ]
    
    def _add_loot_to_run(self, run: DungeonRun, loot: Dict):
        """Add loot to run totals"""
        current_loot = run.total_loot_gained or {}
        
        for item_type, amount in loot.items():
            current_loot[item_type] = current_loot.get(item_type, 0) + amount
        
        run.total_loot_gained = current_loot
    
    def _serialize_room_progress(self, room_progress: RoomProgress) -> Dict:
        """Serialize room progress for API"""
        return {
            "room_number": room_progress.room.room_number,
            "state": room_progress.state.value,
            "combat_completed": room_progress.combat_completed,
            "loot_collected": room_progress.loot_collected,
            "mining_completion": room_progress.mining_completion_percent,
            "first_entered": room_progress.first_entered_at.isoformat() if room_progress.first_entered_at else None
        }
    
    def _serialize_mining_operation(self, mining_op: MiningOperation) -> Dict:
        """Serialize mining operation for API"""
        return {
            "id": mining_op.id,
            "room_number": mining_op.room_progress.room.room_number,
            "completion_percentage": mining_op.completion_percentage,
            "resources_extracted": mining_op.resources_extracted,
            "estimated_completion": mining_op.estimated_completion.isoformat(),
            "miners_assigned": mining_op.miners_assigned
        }