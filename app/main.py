from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import timedelta
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import Player
from app.auth import (
    get_current_player_from_cookie, 
    authenticate_player, 
    create_player, 
    create_access_token
)

app = FastAPI(
    title="GuildedIn API",
    description="LinkedIn parody RPG game API",
    version="1.0.0"
)

# Set up templates
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # SvelteKit default dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root(
    request: Request, 
    current_player: Player = Depends(get_current_player_from_cookie),
    db: Session = Depends(get_db)
):
    if current_player:
        # Player is logged in, show dashboard
        return templates.TemplateResponse("guild_dashboard.html", {"request": request, "player": current_player})
    else:
        # Not logged in, show landing page
        return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_player: Player = Depends(get_current_player_from_cookie),
    db: Session = Depends(get_db)
):
    if not current_player:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("guild_dashboard.html", {"request": request, "player": current_player})

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Authentication Routes
@app.post("/api/auth/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle user login"""
    
    # Authenticate user
    player = authenticate_player(db, email, password)
    if not player:
        return HTMLResponse(
            """<div class="error-message" style="display: block;">
                ❌ Invalid email or password. Please try again.
            </div>""",
            status_code=400
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(player.id)})
    
    # Return success with redirect
    response = HTMLResponse(
        """<div style="color: #10b981; text-align: center; padding: 20px;">
            ✅ Login successful! Redirecting to your guild...
            <script>
                setTimeout(() => {
                    window.location.href = "/dashboard";
                }, 1000);
            </script>
        </div>"""
    )
    
    # Set the session cookie
    response.set_cookie(
        key="session_token",
        value=access_token,
        max_age=30 * 24 * 60 * 60,  # 30 days
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    
    return response

@app.post("/api/auth/register")
async def register(
    email: str = Form(...),
    username: str = Form(...),
    display_name: str = Form(...),
    guild_name: str = Form(...),
    corporate_class: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle user registration"""
    
    # Validate password confirmation
    if password != confirm_password:
        return HTMLResponse(
            """<div class="error-message" style="display: block;">
                ❌ Passwords do not match. Please try again.
            </div>""",
            status_code=400
        )
    
    # Validate required fields
    if not all([email, username, display_name, guild_name, corporate_class, password]):
        return HTMLResponse(
            """<div class="error-message" style="display: block;">
                ❌ All fields are required. Please fill out the complete form.
            </div>""",
            status_code=400
        )
    
    try:
        # Create new player (this also creates the game session and guild)
        player = create_player(
            db=db,
            email=email,
            username=username,
            password=password,
            display_name=display_name,
            corporate_class=corporate_class,
            guild_name=guild_name
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(player.id)})
        
        # Return success with redirect
        response = HTMLResponse(
            f"""<div style="color: #10b981; text-align: center; padding: 20px;">
                ✅ Welcome to GuildedIn, {display_name}!<br>
                🏰 {guild_name} has been established!<br>
                Redirecting to your guild dashboard...
                <script>
                    setTimeout(() => {{
                        window.location.href = "/dashboard";
                    }}, 2000);
                </script>
            </div>"""
        )
        
        # Set the session cookie
        response.set_cookie(
            key="session_token",
            value=access_token,
            max_age=30 * 24 * 60 * 60,  # 30 days
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        return response
        
    except HTTPException as e:
        return HTMLResponse(
            f"""<div class="error-message" style="display: block;">
                ❌ {e.detail}
            </div>""",
            status_code=e.status_code
        )
    except Exception as e:
        return HTMLResponse(
            """<div class="error-message" style="display: block;">
                ❌ Registration failed. Please try again later.
            </div>""",
            status_code=500
        )

@app.post("/api/auth/logout")
async def logout():
    """Handle user logout"""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="session_token")
    return response

# HTMX API Routes
@app.post("/api/actions/recruit")
async def recruit_action():
    # Mock response - simulate recruiting an adventurer
    return HTMLResponse("""
    <aside class="guild-sidebar" id="guild-resources">
        <div class="ceo-profile">
            <div class="ceo-avatar">👨‍💼</div>
            <h2 class="ceo-name">Alex Rodriguez</h2>
            <p class="ceo-title">CEO of TechCorp Guild</p>
            <div class="ceo-background">
                <span class="background-badge">⚔️ Warrior</span>
            </div>
        </div>
        
        <div class="resource-stats">
            <div class="stat-item">
                <span class="stat-label">💰 Gold</span>
                <span class="stat-value">3950</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">✨ EXP Bank</span>
                <span class="stat-value">2,290</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">💰 Gold</span>
                <span class="stat-value">3950</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">✨ EXP Bank</span>
                <span class="stat-value">2,290</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">📈 Share Price</span>
                <span class="stat-value">152.3G</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">🏆 Guild Rank</span>
                <span class="stat-value rank-c">C</span>
            </div>
        </div>

        <div class="facilities-section">
            <h3 class="section-title">Facilities</h3>
            <div class="facility-item">
                <span class="facility-name">Training Grounds</span>
                <span class="facility-level">Lv.3</span>
            </div>
            <div class="facility-item">
                <span class="facility-name">Armory</span>
                <span class="facility-level">Lv.2</span>
            </div>
            <div class="facility-item">
                <span class="facility-name">Infirmary</span>
                <span class="facility-level">Lv.1</span>
            </div>
        </div>
    </aside>
    """)

@app.post("/api/actions/train")
async def train_action():
    # Mock response - simulate training adventurers
    return HTMLResponse("""
    <aside class="guild-sidebar" id="guild-resources">
        <div class="ceo-profile">
            <div class="ceo-avatar">👨‍💼</div>
            <h2 class="ceo-name">Alex Rodriguez</h2>
            <p class="ceo-title">CEO of TechCorp Guild</p>
            <div class="ceo-background">
                <span class="background-badge">⚔️ Warrior</span>
            </div>
        </div>
        
        <div class="resource-stats">
            <div class="stat-item">
                <span class="stat-label">💰 Gold</span>
                <span class="stat-value">4500</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">✨ EXP Bank</span>
                <span class="stat-value">2,190</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">📈 Share Price</span>
                <span class="stat-value">149.7G</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">🏆 Guild Rank</span>
                <span class="stat-value rank-c">C</span>
            </div>
        </div>

        <div class="facilities-section">
            <h3 class="section-title">Facilities</h3>
            <div class="facility-item">
                <span class="facility-name">Training Grounds</span>
                <span class="facility-level">Lv.3</span>
            </div>
            <div class="facility-item">
                <span class="facility-name">Armory</span>
                <span class="facility-level">Lv.2</span>
            </div>
            <div class="facility-item">
                <span class="facility-name">Infirmary</span>
                <span class="facility-level">Lv.1</span>
            </div>
        </div>
    </aside>
    """)

@app.post("/api/actions/upgrade")
async def upgrade_action():
    # Mock response - simulate upgrading facilities
    return HTMLResponse("""
    <aside class="guild-sidebar" id="guild-resources">
        <div class="guild-profile">
            <div class="guild-avatar">🏰</div>
            <h2 class="guild-name">TechCorp Guild</h2>
            <p class="guild-level">Level 13</p>
        </div>
        
        <div class="resource-stats">
            <div class="stat-item">
                <span class="stat-label">💰 Gold</span>
                <span class="stat-value">2750</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">✨ EXP Bank</span>
                <span class="stat-value">2,490</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">📈 Share Price</span>
                <span class="stat-value">155.8G</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">🏆 Guild Rank</span>
                <span class="stat-value rank-c">C</span>
            </div>
        </div>

        <div class="facilities-section">
            <h3 class="section-title">Facilities</h3>
            <div class="facility-item">
                <span class="facility-name">Executive Training Suite</span>
                <span class="facility-level">Lv.4</span>
            </div>
            <div class="facility-item">
                <span class="facility-name">Innovation Lab</span>
                <span class="facility-level">Lv.3</span>
            </div>
            <div class="facility-item">
                <span class="facility-name">Wellness Center</span>
                <span class="stat-value">Lv.2</span>
            </div>
        </div>
    </aside>
    """)

@app.post("/api/like/{post_id}")
async def like_post(post_id: int):
    # Mock response - simulate liking a post
    return HTMLResponse(f'<button class="action-btn" hx-post="/api/unlike/{post_id}" hx-target="this" hx-swap="outerHTML">👍 13</button>')

@app.post("/api/distribute-exp")
async def distribute_exp():
    # Mock response - simulate distributing EXP to adventurers
    return HTMLResponse("""
    <aside class="guild-sidebar" id="guild-resources">
        <div class="ceo-profile">
            <div class="ceo-avatar">👨‍💼</div>
            <h2 class="ceo-name">Alex Rodriguez</h2>
            <p class="ceo-title">CEO of TechCorp Guild</p>
            <div class="ceo-background">
                <span class="background-badge">⚔️ Warrior</span>
            </div>
        </div>
        
        <div class="resource-stats">
            <div class="stat-item">
                <span class="stat-label">💰 Gold</span>
                <span class="stat-value">4750</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">✨ EXP Bank</span>
                <span class="stat-value">2,140</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">⭐ Reputation</span>
                <span class="stat-value">92</span>
            </div>
        </div>

        <div class="facilities-section">
            <h3 class="section-title">Facilities</h3>
            <div class="facility-item">
                <span class="facility-name">Training Grounds</span>
                <span class="facility-level">Lv.3</span>
            </div>
            <div class="facility-item">
                <span class="facility-name">Armory</span>
                <span class="facility-level">Lv.2</span>
            </div>
            <div class="facility-item">
                <span class="facility-name">Infirmary</span>
                <span class="facility-level">Lv.1</span>
            </div>
        </div>
    </aside>
    """)

@app.post("/api/reserve-exp")
async def reserve_exp():
    # Mock response - simulate reserving EXP for interest
    return HTMLResponse("""
    <aside class="guild-sidebar" id="guild-resources">
        <div class="ceo-profile">
            <div class="ceo-avatar">👨‍💼</div>
            <h2 class="ceo-name">Alex Rodriguez</h2>
            <p class="ceo-title">CEO of TechCorp Guild</p>
            <div class="ceo-background">
                <span class="background-badge">⚔️ Warrior</span>
            </div>
        </div>
        
        <div class="resource-stats">
            <div class="stat-item">
                <span class="stat-label">💰 Gold</span>
                <span class="stat-value">4750</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">✨ EXP Bank</span>
                <span class="stat-value">1,840</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">⭐ Reputation</span>
                <span class="stat-value">92</span>
            </div>
        </div>

        <div class="facilities-section">
            <h3 class="section-title">Facilities</h3>
            <div class="facility-item">
                <span class="facility-name">Training Grounds</span>
                <span class="facility-level">Lv.3</span>
            </div>
            <div class="facility-item">
                <span class="facility-name">Armory</span>
                <span class="facility-level">Lv.2</span>
            </div>
            <div class="facility-item">
                <span class="facility-name">Infirmary</span>
                <span class="facility-level">Lv.1</span>
            </div>
        </div>
    </aside>
    """)

@app.post("/api/unlike/{post_id}")
async def unlike_post(post_id: int):
    # Mock response - simulate unliking a post
    return HTMLResponse(f'<button class="action-btn" hx-post="/api/like/{post_id}" hx-target="this" hx-swap="outerHTML">👍 12</button>')

@app.get("/api/exp-management")
async def exp_management_view():
    # Mock response - EXP banking interface
    return HTMLResponse("""
    <div class="feed-container">
        <div class="activity-post">
            <div class="post-inner">
                <h2 class="post-title">✨ EXP Management System</h2>
                <p class="post-content">Manage your guild's experience points through banking, distribution, and investment:</p>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 16px 0;">
                    <div style="background: rgba(0,0,0,0.2); border: 2px solid #57534e; padding: 16px;">
                        <h3 style="color: #10b981; font-family: 'Press Start 2P', monospace; font-size: 10px; margin-bottom: 12px;">💰 EXP Bank</h3>
                        <div style="margin-bottom: 12px;">
                            <strong>Available: 2,340 EXP</strong><br>
                            <small>Ready for distribution or investment</small>
                        </div>
                        <button class="action-btn" hx-post="/api/distribute-exp" hx-target="#guild-resources" hx-swap="outerHTML">Distribute to Adventurers</button>
                    </div>
                    
                    <div style="background: rgba(0,0,0,0.2); border: 2px solid #57534e; padding: 16px;">
                        <h3 style="color: #f59e0b; font-family: 'Press Start 2P', monospace; font-size: 10px; margin-bottom: 12px;">🏦 Reserved EXP</h3>
                        <div style="margin-bottom: 12px;">
                            <strong>Reserved: 500 EXP</strong><br>
                            <small>Earning 5% daily interest (25 EXP/day)</small>
                        </div>
                        <button class="action-btn" hx-post="/api/reserve-exp" hx-target="#guild-resources" hx-swap="outerHTML">Reserve More EXP</button>
                    </div>
                </div>
                
                <div style="background: linear-gradient(135deg, #1f2937, #111827); border: 2px solid #374151; padding: 12px; margin: 16px 0;">
                    <h4 style="color: #3b82f6; font-family: 'Press Start 2P', monospace; font-size: 9px; margin-bottom: 8px;">📊 Recent Transactions</h4>
                    <div style="font-size: 12px; color: #d1d5db;">
                        <div>• +250 EXP from Ancient Ruins dungeon</div>
                        <div>• -100 EXP distributed to Mike (Fighter)</div>
                        <div>• +25 EXP interest earned on reserves</div>
                    </div>
                </div>
                
                <div class="post-actions">
                    <button class="action-btn" hx-get="/dashboard" hx-target="#main-content" hx-swap="innerHTML">← Back to Feed</button>
                </div>
            </div>
        </div>
    </div>
    """)

@app.get("/api/market")
async def market_view():
    # Mock response - simulate market view
    return HTMLResponse("""
    <div class="feed-container">
        <div class="activity-post">
            <div class="post-inner">
                <h2 class="post-title">🏪 Adventurer Market</h2>
                <p class="post-content">Browse available adventurers seeking to join a guild:</p>
                
                <div style="display: flex; flex-direction: column; gap: 12px; margin: 16px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: rgba(0,0,0,0.2); border: 1px solid #57534e;">
                        <div>
                            <strong>Archer</strong> (Level 5)<br>
                            <small>Specializes in Ranged Combat & Precision Strikes</small>
                        </div>
                        <button class="action-btn" hx-post="/api/recruit/1" hx-target="#guild-resources" hx-swap="outerHTML">Hire - 600G</button>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: rgba(0,0,0,0.2); border: 1px solid #57534e;">
                        <div>
                            <strong>Cleric</strong> (Level 7)<br>
                            <small>Expert in Healing Magic & Divine Protection</small>
                        </div>
                        <button class="action-btn" hx-post="/api/recruit/2" hx-target="#guild-resources" hx-swap="outerHTML">Hire - 850G</button>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: rgba(0,0,0,0.2); border: 1px solid #57534e;">
                        <div>
                            <strong>Wizard</strong> (Level 9)<br>
                            <small>Masters Arcane Spells & Elemental Magic</small>
                        </div>
                        <button class="action-btn" hx-post="/api/recruit/3" hx-target="#guild-resources" hx-swap="outerHTML">Hire - 1200G</button>
                    </div>
                </div>
                
                <div class="post-actions">
                    <button class="action-btn" hx-get="/dashboard" hx-target="#main-content" hx-swap="innerHTML">← Back to Feed</button>
                </div>
            </div>
        </div>
    </div>
    """)

# Dungeon System Routes
@app.get("/dungeons/marketplace")
async def dungeon_marketplace(request: Request):
    return templates.TemplateResponse("dungeon_marketplace.html", {"request": request})

@app.get("/dungeons/active")
async def dungeon_active(request: Request):
    return templates.TemplateResponse("dungeon_active.html", {"request": request})

# Legacy route redirect
@app.get("/dungeons")
async def dungeon_redirect(request: Request):
    return templates.TemplateResponse("dungeon_marketplace.html", {"request": request})

@app.get("/api/dungeons/marketplace")
async def get_marketplace_dungeons():
    # Mock response - marketplace refresh
    return HTMLResponse("""
    <!-- Updated dungeon listings would go here -->
    <div style="text-align: center; color: #10b981; padding: 20px;">
        🔄 Marketplace refreshed - 3 dungeons available
    </div>
    """)

@app.get("/api/dungeons/details/{dungeon_id}")
async def get_dungeon_details(dungeon_id: int):
    # Mock response - dungeon details for sidebar
    dungeons = {
        1: {
            "name": "🏛️ Ancient Tokyo Ruins",
            "location": "Tokyo, Japan",
            "rank": "C",
            "rooms": 7,
            "bonus": "2,000G",
            "slots": "2/3",
            "high_bid": "1,200G",
            "closes": "3h 42m"
        },
        2: {
            "name": "⛰️ Himalayan Crystal Caves", 
            "location": "Nepal",
            "rank": "B",
            "rooms": 10,
            "bonus": "4,000G",
            "slots": "1/2", 
            "high_bid": "2,800G",
            "closes": "8h 15m"
        },
        3: {
            "name": "🏖️ Bermuda Portal",
            "location": "Atlantic Ocean", 
            "rank": "A",
            "rooms": 12,
            "bonus": "8,000G",
            "slots": "1/1",
            "high_bid": "5,500G",
            "closes": "12h 30m"
        }
    }
    
    dungeon = dungeons.get(dungeon_id, dungeons[1])
    
    return HTMLResponse(f"""
    <h3 class="section-title">📍 {dungeon['name']}</h3>
    <div class="dungeon-details">
        <div class="detail-row">
            <span>📍 Location:</span>
            <span class="detail-value">{dungeon['location']}</span>
        </div>
        <div class="detail-row">
            <span>🏆 Rank:</span>
            <span class="detail-value rank-{dungeon['rank'].lower()}">{dungeon['rank']}</span>
        </div>
        <div class="detail-row">
            <span>🏠 Total Rooms:</span>
            <span class="detail-value">{dungeon['rooms']}</span>
        </div>
        <div class="detail-row">
            <span>💰 Completion Bonus:</span>
            <span class="detail-value">{dungeon['bonus']}</span>
        </div>
        <div class="detail-row">
            <span>🎯 Available Slots:</span>
            <span class="detail-value">{dungeon['slots']}</span>
        </div>
        <div class="detail-row">
            <span>💎 Current High Bid:</span>
            <span class="detail-value">{dungeon['high_bid']}</span>
        </div>
    </div>
    
    <div class="bidding-section">
        <div class="bidding-status">⏰ Bidding closes in: {dungeon['closes']}</div>
        <input type="number" class="bid-input" placeholder="Enter your bid" id="bid-{dungeon_id}" 
               value="{int(dungeon['high_bid'].replace('G', '').replace(',', '')) + 100}">
        <button class="bid-button" hx-post="/api/dungeons/bid" hx-include="#bid-{dungeon_id}" 
                hx-vals='{{"dungeon_id": {dungeon_id}}}' hx-target="#selected-dungeon" hx-swap="innerHTML">
            💰 Submit Bid
        </button>
    </div>
    """)

@app.get("/api/dungeons/time-status")
async def get_time_status():
    # Mock response - time tracking
    return HTMLResponse("""
    <div class="time-remaining">⏰ 4h 12m remaining</div>
    <div class="daily-limit">Daily: 6h 48m used / 8h limit</div>
    """)

@app.get("/api/dungeons/room-status")
async def get_room_status():
    # Mock response - updated room states
    return HTMLResponse("""
    <!-- Entrance -->
    <div class="room-cell" hx-post="/api/dungeons/advance" hx-vals='{"room": 1}' hx-target="#dungeon-main">
        <div class="room-number">START</div>
        <div class="room-icon">🚪</div>
        <div class="room-status">Entrance</div>
    </div>

    <!-- Room 1 - Current -->
    <div class="room-cell current" hx-post="/api/dungeons/combat" hx-target="#combat-modal" hx-swap="innerHTML">
        <div class="room-number">1</div>
        <div class="room-icon">⚔️</div>
        <div class="room-status">Combat Ready</div>
    </div>

    <!-- Room 2 - Mining Progress Updated -->
    <div class="room-cell cleared mining">
        <div class="room-number">2</div>
        <div class="room-icon">⛏️</div>
        <div class="room-status">Mining 73%</div>
        <div class="mining-progress">
            <div class="mining-fill" style="width: 73%;"></div>
        </div>
    </div>

    <!-- Remaining rooms (3-9) -->
    <div class="room-cell">
        <div class="room-number">3</div>
        <div class="room-icon">❓</div>
        <div class="room-status">Unexplored</div>
    </div>

    <div class="room-cell">
        <div class="room-number">4</div>
        <div class="room-icon">❓</div>
        <div class="room-status">Unexplored</div>
    </div>

    <div class="room-cell">
        <div class="room-number">5</div>
        <div class="room-icon">❓</div>
        <div class="room-status">Unexplored</div>
    </div>

    <div class="room-cell">
        <div class="room-number">6</div>
        <div class="room-icon">❓</div>
        <div class="room-status">Unexplored</div>
    </div>

    <div class="room-cell">
        <div class="room-number">7</div>
        <div class="room-icon">❓</div>
        <div class="room-status">Unexplored</div>
    </div>

    <div class="room-cell">
        <div class="room-number">8</div>
        <div class="room-icon">❓</div>
        <div class="room-status">Unexplored</div>
    </div>

    <div class="room-cell">
        <div class="room-number">9</div>
        <div class="room-icon">❓</div>
        <div class="room-status">Unexplored</div>
    </div>

    <!-- Boss Room -->
    <div class="room-cell boss">
        <div class="room-number">10</div>
        <div class="room-icon">👹</div>
        <div class="room-status">Frost Titan</div>
    </div>
    """)

@app.post("/api/dungeons/combat")
async def start_combat():
    # Mock response - combat modal
    return HTMLResponse("""
    <div class="combat-modal">
        <div class="combat-content">
            <h2 class="combat-title">⚔️ Combat in Progress</h2>
            <div style="text-align: center; margin: 20px 0;">
                <div style="font-size: 14px; margin-bottom: 16px;">
                    Your party engages 3 Crystal Golems!
                </div>
                <div style="background: #1f2937; border: 2px solid #374151; padding: 12px; margin: 12px 0;">
                    <div style="font-family: 'Press Start 2P', monospace; font-size: 8px; color: #10b981; margin-bottom: 8px;">
                        COMBAT LOG
                    </div>
                    <div style="font-size: 12px; line-height: 1.6; text-align: left;">
                        • Sarah casts Healing Light (+45 HP to party)<br>
                        • Mike attacks with Sword Strike (78 damage)<br>
                        • Lisa uses Shield Bash (65 damage, stun)<br>
                        • Golem #1 destroyed!
                    </div>
                </div>
                <div style="margin: 16px 0;">
                    <strong style="color: #10b981;">Victory!</strong><br>
                    💰 +400 Gold • ✨ +180 EXP
                </div>
            </div>
            <div style="display: flex; gap: 12px; justify-content: center;">
                <button class="action-button" hx-post="/api/dungeons/advance" hx-vals='{"room": 2}' hx-target="#dungeon-main" hx-swap="innerHTML" onclick="document.getElementById('combat-modal').style.display='none'">
                    ➡️ Advance to Room 2
                </button>
                <button class="action-button" hx-post="/api/dungeons/start-mining" hx-vals='{"room": 1}' hx-target="#room-grid" hx-swap="innerHTML" onclick="document.getElementById('combat-modal').style.display='none'">
                    ⛏️ Start Mining Here
                </button>
            </div>
        </div>
    </div>
    """)

@app.get("/api/dungeons/party-status")
async def get_party_status():
    # Mock response - party health updates
    return HTMLResponse("""
    <h3 style="font-family: 'Press Start 2P', monospace; font-size: 9px; color: #10b981; margin: 0 0 8px 0;">Party Status</h3>
    
    <div class="party-member">
        <span>Sarah (Healer)</span>
        <div class="health-bar">
            <div class="health-fill" style="width: 88%;"></div>
        </div>
    </div>
    
    <div class="party-member">
        <span>Mike (Fighter)</span>
        <div class="health-bar">
            <div class="health-fill" style="width: 76%;"></div>
        </div>
    </div>
    
    <div class="party-member">
        <span>Lisa (Paladin)</span>
        <div class="health-bar">
            <div class="health-fill" style="width: 82%;"></div>
        </div>
    </div>
    """)

@app.post("/api/dungeons/bid")
async def submit_bid():
    # Mock response - bid submission (only costs money, not actions)
    return HTMLResponse("""
    <h3 class="section-title">💰 Bid Submitted</h3>
    <div style="color: #10b981; font-size: 12px; margin: 8px 0;">
        ✓ Bid of 1,500G submitted successfully!<br>
        Status: Pending review<br>
        Results in: 3h 41m
    </div>
    <button class="bid-button" disabled>
        Bid Submitted
    </button>
    """)

# Server-Sent Events for real-time updates
from fastapi.responses import StreamingResponse
import json
import asyncio

@app.get("/api/dungeons/events")
async def dungeon_events():
    async def event_generator():
        while True:
            # Mining progress update
            yield f"event: mining-update\ndata: {json.dumps({'room': 2, 'progress': 75})}\n\n"
            await asyncio.sleep(30)
            
            # Time update
            yield f"event: time-update\ndata: {json.dumps({'remaining_minutes': 250})}\n\n"
            await asyncio.sleep(60)
    
    return StreamingResponse(event_generator(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
