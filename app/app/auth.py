from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .models.user import Player
from .models.database import get_db

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"  # TODO: Move to environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token bearer
security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None

def authenticate_player(db: Session, email: str, password: str) -> Optional[Player]:
    """Authenticate a player with email and password"""
    player = db.query(Player).filter(Player.email == email).first()
    if not player:
        return None
    if not verify_password(password, player.hashed_password):
        return None
    return player

def get_current_player_from_cookie(
    session_token: Optional[str] = Cookie(None), 
    db: Session = Depends(get_db)
) -> Optional[Player]:
    """Get current player from session cookie (optional)"""
    if not session_token:
        return None
    
    payload = verify_token(session_token)
    if not payload:
        return None
    
    player_id = payload.get("sub")
    if not player_id:
        return None
    
    player = db.query(Player).filter(Player.id == int(player_id)).first()
    return player

def get_current_player_required(
    session_token: Optional[str] = Cookie(None), 
    db: Session = Depends(get_db)
) -> Player:
    """Get current player from session cookie (required)"""
    player = get_current_player_from_cookie(session_token, db)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return player

def create_player(
    db: Session, 
    email: str, 
    username: str, 
    password: str,
    display_name: str,
    corporate_class: str,
    guild_name: str
) -> Player:
    """Create a new player account"""
    
    # Check if email or username already exists
    existing_player = db.query(Player).filter(
        (Player.email == email) | (Player.username == username)
    ).first()
    
    if existing_player:
        if existing_player.email == email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new player
    from .models.user import CorporateClass
    hashed_password = hash_password(password)
    
    player = Player(
        email=email,
        username=username,
        hashed_password=hashed_password,
        display_name=display_name,
        corporate_class=CorporateClass(corporate_class),
        current_position=f"Aspiring {corporate_class.replace('_', ' ').title().replace('Manager', 'Manager')}",
        professional_summary=f"Eager professional ready to build the next great guild!",
        location="Global Network"
    )
    
    db.add(player)
    db.commit()
    db.refresh(player)
    
    # Create initial game session for new player with custom guild name
    from .services.game_session_service import GameSessionService
    session_service = GameSessionService(db)
    game_session = session_service.create_new_session(player.id, guild_name)
    
    return player