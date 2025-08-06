from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ..models.dungeon_system import Dungeon, DungeonContract, DungeonStatus, ContractStatus, DungeonRank
from ..models.dungeon_progression import DungeonRun, RunStatus
from ..models.guild import Guild, GuildRank

class DungeonBiddingService:
    """Handles dungeon discovery, bidding, and contract awards"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_dungeon_bid(self, guild_id: int, dungeon_id: int, bid_amount: int) -> Dict:
        """Submit a bid for dungeon access"""
        
        # Validate guild and dungeon
        guild = self.db.query(Guild).filter(Guild.id == guild_id).first()
        dungeon = self.db.query(Dungeon).filter(Dungeon.id == dungeon_id).first()
        
        if not guild or not dungeon:
            return {"success": False, "error": "Guild or dungeon not found"}
        
        # Check if guild rank is sufficient
        if not self._can_guild_access_dungeon(guild.guild_rank, dungeon.difficulty_rank):
            return {"success": False, "error": f"Guild rank {guild.guild_rank.value} insufficient for {dungeon.difficulty_rank.value}-rank dungeon"}
        
        # Check if bidding is still open
        if dungeon.status != DungeonStatus.BIDDING:
            return {"success": False, "error": "Bidding period has ended"}
        
        if datetime.utcnow() > dungeon.bidding_closes_at:
            return {"success": False, "error": "Bidding deadline passed"}
        
        # Check if guild has sufficient funds
        if guild.gold < bid_amount:
            return {"success": False, "error": "Insufficient gold for bid"}
        
        # Check if guild already has a bid
        existing_bid = self.db.query(DungeonContract).filter(
            and_(
                DungeonContract.guild_id == guild_id,
                DungeonContract.dungeon_id == dungeon_id,
                DungeonContract.status == ContractStatus.PENDING
            )
        ).first()
        
        if existing_bid:
            # Update existing bid
            existing_bid.bid_amount = bid_amount
            existing_bid.bid_submitted_at = datetime.utcnow()
            self.db.commit()
            
            return {
                "success": True, 
                "message": "Bid updated successfully",
                "contract_id": existing_bid.id,
                "bid_amount": bid_amount
            }
        else:
            # Create new bid
            contract = DungeonContract(
                dungeon_id=dungeon_id,
                guild_id=guild_id,
                bid_amount=bid_amount,
                status=ContractStatus.PENDING
            )
            
            self.db.add(contract)
            self.db.commit()
            
            return {
                "success": True,
                "message": "Bid submitted successfully", 
                "contract_id": contract.id,
                "bid_amount": bid_amount
            }
    
    def process_bidding_results(self, dungeon_id: int) -> Dict:
        """Process bidding results and award contracts"""
        
        dungeon = self.db.query(Dungeon).filter(Dungeon.id == dungeon_id).first()
        if not dungeon:
            return {"success": False, "error": "Dungeon not found"}
        
        # Get all pending bids, ordered by amount (highest first)
        pending_bids = self.db.query(DungeonContract).filter(
            and_(
                DungeonContract.dungeon_id == dungeon_id,
                DungeonContract.status == ContractStatus.PENDING
            )
        ).order_by(desc(DungeonContract.bid_amount)).all()
        
        if not pending_bids:
            return {"success": False, "error": "No bids received"}
        
        # Award contracts based on available slots
        contracts_awarded = 0
        max_contracts = dungeon.max_guild_contracts
        awarded_contracts = []
        
        for bid in pending_bids:
            if contracts_awarded >= max_contracts:
                # Reject remaining bids
                bid.status = ContractStatus.REJECTED
                continue
            
            # Award this contract
            guild = self.db.query(Guild).filter(Guild.id == bid.guild_id).first()
            
            # Deduct bid amount from guild treasury
            guild.gold -= bid.bid_amount
            
            # Award contract
            bid.status = ContractStatus.AWARDED
            bid.awarded_at = datetime.utcnow()
            bid.contract_value = bid.bid_amount
            bid.access_expires_at = dungeon.dungeon_closes_at
            
            # Create initial dungeon run
            run = DungeonRun(
                dungeon_id=dungeon_id,
                guild_id=bid.guild_id,
                contract_id=bid.id,
                status=RunStatus.PREPARING
            )
            self.db.add(run)
            
            awarded_contracts.append({
                "guild_id": bid.guild_id,
                "guild_name": guild.name,
                "bid_amount": bid.bid_amount
            })
            
            contracts_awarded += 1
        
        # Update dungeon status
        dungeon.status = DungeonStatus.ACTIVE
        dungeon.current_contracts = contracts_awarded
        
        self.db.commit()
        
        return {
            "success": True,
            "contracts_awarded": contracts_awarded,
            "total_bids": len(pending_bids),
            "awarded_contracts": awarded_contracts
        }
    
    def get_available_dungeons_for_guild(self, guild_id: int) -> List[Dict]:
        """Get dungeons that a guild can bid on"""
        
        guild = self.db.query(Guild).filter(Guild.id == guild_id).first()
        if not guild:
            return []
        
        # Find dungeons in bidding phase that guild can access
        available_dungeons = self.db.query(Dungeon).filter(
            and_(
                Dungeon.status == DungeonStatus.BIDDING,
                Dungeon.bidding_closes_at > datetime.utcnow()
            )
        ).all()
        
        accessible_dungeons = []
        for dungeon in available_dungeons:
            if self._can_guild_access_dungeon(guild.guild_rank, dungeon.difficulty_rank):
                # Check if guild already has a bid
                existing_bid = self.db.query(DungeonContract).filter(
                    and_(
                        DungeonContract.guild_id == guild_id,
                        DungeonContract.dungeon_id == dungeon.id,
                        DungeonContract.status == ContractStatus.PENDING
                    )
                ).first()
                
                accessible_dungeons.append({
                    "id": dungeon.id,
                    "name": dungeon.name,
                    "location": dungeon.location_name,
                    "difficulty_rank": dungeon.difficulty_rank.value,
                    "total_rooms": dungeon.total_rooms,
                    "base_loot_value": dungeon.base_loot_value,
                    "completion_bonus": dungeon.completion_bonus,
                    "failure_penalty": dungeon.failure_penalty,
                    "max_contracts": dungeon.max_guild_contracts,
                    "current_contracts": dungeon.current_contracts,
                    "bidding_closes_at": dungeon.bidding_closes_at.isoformat(),
                    "dungeon_closes_at": dungeon.dungeon_closes_at.isoformat(),
                    "existing_bid": existing_bid.bid_amount if existing_bid else None
                })
        
        return accessible_dungeons
    
    def get_dungeon_bidding_status(self, dungeon_id: int) -> Dict:
        """Get current bidding status for a dungeon"""
        
        dungeon = self.db.query(Dungeon).filter(Dungeon.id == dungeon_id).first()
        if not dungeon:
            return {"error": "Dungeon not found"}
        
        # Get bid statistics (without revealing specific bids)
        total_bids = self.db.query(DungeonContract).filter(
            and_(
                DungeonContract.dungeon_id == dungeon_id,
                DungeonContract.status == ContractStatus.PENDING
            )
        ).count()
        
        # Get highest bid amount (for market intelligence)
        highest_bid = self.db.query(DungeonContract).filter(
            and_(
                DungeonContract.dungeon_id == dungeon_id,
                DungeonContract.status == ContractStatus.PENDING
            )
        ).order_by(desc(DungeonContract.bid_amount)).first()
        
        return {
            "dungeon_id": dungeon_id,
            "name": dungeon.name,
            "status": dungeon.status.value,
            "total_bids": total_bids,
            "max_contracts": dungeon.max_guild_contracts,
            "highest_bid": highest_bid.bid_amount if highest_bid else 0,
            "bidding_closes_at": dungeon.bidding_closes_at.isoformat(),
            "time_remaining": self._get_time_remaining(dungeon.bidding_closes_at)
        }
    
    def _can_guild_access_dungeon(self, guild_rank: GuildRank, dungeon_rank: DungeonRank) -> bool:
        """Check if guild rank is sufficient for dungeon"""
        rank_values = {"E": 1, "D": 2, "C": 3, "B": 4, "A": 5, "S": 6}
        return rank_values[guild_rank.value] >= rank_values[dungeon_rank.value]
    
    def _get_time_remaining(self, deadline: datetime) -> Dict:
        """Calculate time remaining until deadline"""
        now = datetime.utcnow()
        if now >= deadline:
            return {"expired": True}
        
        remaining = deadline - now
        days = remaining.days
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        return {
            "expired": False,
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "total_minutes": int(remaining.total_seconds() / 60)
        }

def generate_new_dungeon(db: Session, rank: DungeonRank, location_data: Dict) -> Dungeon:
    """Generate a new dungeon discovery"""
    
    # Calculate dungeon parameters based on rank
    rank_multipliers = {
        DungeonRank.E: {"rooms": 3, "loot": 100, "bonus": 500, "penalty": 200},
        DungeonRank.D: {"rooms": 5, "loot": 200, "bonus": 1000, "penalty": 500},
        DungeonRank.C: {"rooms": 7, "loot": 400, "bonus": 2000, "penalty": 1000},
        DungeonRank.B: {"rooms": 10, "loot": 800, "bonus": 4000, "penalty": 2000},
        DungeonRank.A: {"rooms": 12, "loot": 1500, "bonus": 8000, "penalty": 4000},
        DungeonRank.S: {"rooms": 15, "loot": 3000, "bonus": 15000, "penalty": 8000}
    }
    
    multiplier = rank_multipliers[rank]
    
    # Set bidding and expiration times
    bidding_duration = timedelta(hours=24)  # 24 hours to bid
    dungeon_duration = timedelta(days=7)    # 1 week to complete
    
    dungeon = Dungeon(
        name=location_data["name"],
        description=location_data.get("description", "A mysterious dungeon has appeared..."),
        difficulty_rank=rank,
        location_name=location_data["location"],
        latitude=location_data.get("latitude"),
        longitude=location_data.get("longitude"),
        region=location_data.get("region", "Unknown"),
        total_rooms=multiplier["rooms"],
        boss_room_number=multiplier["rooms"],
        max_guild_contracts=location_data.get("max_contracts", 1),
        base_loot_value=multiplier["loot"],
        completion_bonus=multiplier["bonus"],
        failure_penalty=multiplier["penalty"],
        bidding_closes_at=datetime.utcnow() + bidding_duration,
        dungeon_closes_at=datetime.utcnow() + dungeon_duration,
        status=DungeonStatus.BIDDING
    )
    
    db.add(dungeon)
    db.commit()
    
    # Generate rooms for this dungeon
    generate_dungeon_rooms(db, dungeon)
    
    return dungeon

def generate_dungeon_rooms(db: Session, dungeon: Dungeon):
    """Generate rooms for a dungeon"""
    from ..models.dungeon_system import DungeonRoom
    
    for room_num in range(1, dungeon.total_rooms + 1):
        is_boss = (room_num == dungeon.boss_room_number)
        
        # Scale enemy difficulty with room number and dungeon rank
        base_difficulty = {"E": 10, "D": 20, "C": 35, "B": 50, "A": 70, "S": 90}
        room_difficulty = base_difficulty[dungeon.difficulty_rank.value] + (room_num * 5)
        
        room = DungeonRoom(
            dungeon_id=dungeon.id,
            room_number=room_num,
            name=f"Chamber {room_num}" if not is_boss else f"Boss Chamber - {dungeon.name} Core",
            is_boss_room=is_boss,
            enemy_configuration=_generate_enemy_config(dungeon.difficulty_rank, room_num, is_boss),
            combat_difficulty=room_difficulty,
            base_loot={"gold": dungeon.base_loot_value, "exp": dungeon.base_loot_value // 2},
            mining_resources=_generate_mining_resources(dungeon.difficulty_rank, room_num),
            mining_duration_hours=4 if not is_boss else 8
        )
        
        db.add(room)
    
    db.commit()

def _generate_enemy_config(rank: DungeonRank, room_num: int, is_boss: bool) -> Dict:
    """Generate enemy configuration for a room"""
    if is_boss:
        return {
            "boss": {"type": f"{rank.value}_rank_boss", "level": room_num * 10, "count": 1}
        }
    
    # Regular room enemies
    enemy_counts = {"E": 2, "D": 3, "C": 4, "B": 5, "A": 6, "S": 8}
    base_count = enemy_counts[rank.value]
    
    return {
        "minions": {
            "type": f"{rank.value}_rank_minion",
            "level": room_num * 5,
            "count": base_count + (room_num // 3)
        }
    }

def _generate_mining_resources(rank: DungeonRank, room_num: int) -> Dict:
    """Generate mining resources for a room"""
    base_resources = {
        "iron_ore": 10 * room_num,
        "precious_gems": 2 * room_num,
        "magical_crystals": 1 * room_num
    }
    
    # Scale by rank
    rank_multipliers = {"E": 0.5, "D": 0.8, "C": 1.0, "B": 1.5, "A": 2.0, "S": 3.0}
    multiplier = rank_multipliers[rank.value]
    
    return {k: int(v * multiplier) for k, v in base_resources.items()}