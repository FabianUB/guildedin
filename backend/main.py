from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

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
async def root(request: Request):
    return templates.TemplateResponse("guild_dashboard.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("guild_dashboard.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "healthy"}

# HTMX API Routes
@app.post("/api/actions/recruit")
async def recruit_action():
    # Mock response - simulate recruiting an adventurer
    return HTMLResponse("""
    <aside class="guild-sidebar" id="guild-resources">
        <div class="guild-profile">
            <div class="guild-avatar">🏰</div>
            <h2 class="guild-name">TechCorp Guild</h2>
            <p class="guild-level">Level 12</p>
        </div>
        
        <div class="resource-stats">
            <div class="stat-item">
                <span class="stat-label">💰 Gold</span>
                <span class="stat-value">3950</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">⚡ Bandwidth</span>
                <span class="stat-value">80%</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">⭐ Reputation</span>
                <span class="stat-value">94</span>
            </div>
        </div>

        <div class="facilities-section">
            <h3 class="section-title">Facilities</h3>
            <div class="facility-item">
                <span class="facility-name">Executive Training Suite</span>
                <span class="facility-level">Lv.3</span>
            </div>
            <div class="facility-item">
                <span class="facility-name">Innovation Lab</span>
                <span class="facility-level">Lv.2</span>
            </div>
            <div class="facility-item">
                <span class="facility-name">Wellness Center</span>
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
        <div class="guild-profile">
            <div class="guild-avatar">🏰</div>
            <h2 class="guild-name">TechCorp Guild</h2>
            <p class="guild-level">Level 12</p>
        </div>
        
        <div class="resource-stats">
            <div class="stat-item">
                <span class="stat-label">💰 Gold</span>
                <span class="stat-value">4500</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">⚡ Bandwidth</span>
                <span class="stat-value">70%</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">⭐ Reputation</span>
                <span class="stat-value">95</span>
            </div>
        </div>

        <div class="facilities-section">
            <h3 class="section-title">Facilities</h3>
            <div class="facility-item">
                <span class="facility-name">Executive Training Suite</span>
                <span class="facility-level">Lv.3</span>
            </div>
            <div class="facility-item">
                <span class="facility-name">Innovation Lab</span>
                <span class="facility-level">Lv.2</span>
            </div>
            <div class="facility-item">
                <span class="facility-name">Wellness Center</span>
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
                <span class="stat-label">⚡ Bandwidth</span>
                <span class="stat-value">90%</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">⭐ Reputation</span>
                <span class="stat-value">98</span>
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

@app.post("/api/unlike/{post_id}")
async def unlike_post(post_id: int):
    # Mock response - simulate unliking a post
    return HTMLResponse(f'<button class="action-btn" hx-post="/api/like/{post_id}" hx-target="this" hx-swap="outerHTML">👍 12</button>')

@app.get("/api/market")
async def market_view():
    # Mock response - simulate market view
    return HTMLResponse("""
    <div class="feed-container">
        <div class="activity-post">
            <div class="post-inner">
                <h2 class="post-title">🏪 Adventurer Market</h2>
                <p class="post-content">Browse available corporate professionals looking for guild opportunities:</p>
                
                <div style="display: flex; flex-direction: column; gap: 12px; margin: 16px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: rgba(0,0,0,0.2); border: 1px solid #57534e;">
                        <div>
                            <strong>Marketing Strategist</strong> (Level 5)<br>
                            <small>Specializes in Brand Synergy & Customer Acquisition</small>
                        </div>
                        <button class="action-btn" hx-post="/api/recruit/1" hx-target="#guild-resources" hx-swap="outerHTML">Hire - 600G</button>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: rgba(0,0,0,0.2); border: 1px solid #57534e;">
                        <div>
                            <strong>Operations Manager</strong> (Level 7)<br>
                            <small>Expert in Process Optimization & Workflow Management</small>
                        </div>
                        <button class="action-btn" hx-post="/api/recruit/2" hx-target="#guild-resources" hx-swap="outerHTML">Hire - 850G</button>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: rgba(0,0,0,0.2); border: 1px solid #57534e;">
                        <div>
                            <strong>Innovation Director</strong> (Level 9)<br>
                            <small>Masters Creative Solutions & Disruptive Thinking</small>
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
