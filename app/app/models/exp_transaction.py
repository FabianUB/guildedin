from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base

class ExpTransactionType(PyEnum):
    EARNED = "earned"           # EXP gained from dungeon
    DISTRIBUTED = "distributed" # EXP given to adventurer
    RESERVED = "reserved"       # EXP moved to reserves
    UNRESERVED = "unreserved"   # EXP taken from reserves
    INTEREST = "interest"       # Interest earned on reserves
    SPENT = "spent"            # EXP used as currency

class ExpTransaction(Base):
    """Track all EXP movements in the guild banking system"""
    __tablename__ = "exp_transactions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Transaction Details
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=False)
    transaction_type = Column(Enum(ExpTransactionType), nullable=False)
    amount = Column(Integer, nullable=False)  # Can be negative for spending
    
    # Context
    description = Column(String, nullable=False)  # "EXP from Ancient Ruins dungeon"
    adventurer_id = Column(Integer, ForeignKey("adventurers.id"), nullable=True)  # If distributed to adventurer
    dungeon_run_id = Column(Integer, nullable=True)  # If earned from dungeon
    
    # Balances after transaction
    exp_bank_balance = Column(Integer, nullable=False)
    exp_reserved_balance = Column(Integer, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    guild = relationship("Guild")
    adventurer = relationship("Adventurer")