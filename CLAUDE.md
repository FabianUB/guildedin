# GuildedIn - Claude Development Notes

## 🎮 Core Game Concept (IMPORTANT DISTINCTION)

**This is NOT a social networking platform!** 

GuildedIn is a **Monster Rancher-style management game** with LinkedIn parody theming:

- **Authentication/Users**: Real users for save/load data, leaderboards, progress tracking
- **Adventurer Profiles**: AI-generated bot characters OR async versions of other users' adventurers
- **Gameplay Loop**: Recruit → Train → Dungeon → Loot → Upgrade → Repeat

Think: "Monster Rancher meets LinkedIn" NOT "LinkedIn meets RPG"

## 🎨 UI/UX Design Strategy

### Pixel-Art LinkedIn Interface
- **Visual Style**: 16-bit/pixel-art version of LinkedIn's layout and components
- **Feed**: Activity feed showing dungeon completions, achievements, new recruits (pixel art posts)
- **Adventurer Profiles**: Character sheets that look like pixelated LinkedIn profiles with 8-bit avatars
- **Guild Pages**: Pixel-art company pages showing guild stats, culture, achievements
- **Recruitment**: Browse adventurers like LinkedIn job search but with retro gaming aesthetic
- **Professional Layout**: LinkedIn's clean structure but rendered in nostalgic pixel-art style

### Custom Game Interface (Pixel-Art RPG Style)
- **Dungeon Expeditions**: Classic 16-bit RPG combat/adventure interface
- **Training Facilities**: Retro game-style upgrade/skill development screens
- **Equipment Management**: Pixel-art inventory and gear optimization
- **Guild Management**: Base building with classic simulation game pixel art

**Visual Identity**: LinkedIn's familiar UX patterns but with charming 16-bit pixel art aesthetic throughout.

## 🏗️ Game Architecture

### Real User System
- Authentication for save/load
- Progress tracking & leaderboards  
- Account management
- Cross-player async interactions

### Bot Adventurer System  
- AI-generated corporate characters with LinkedIn parody profiles
- Async copies of other users' trained adventurers
- Recruit from a pool of available "professionals"
- Each has corporate class, stats, and silly LinkedIn-style descriptions

### Core Gameplay Loop
1. **Recruit** adventurers from the "talent pool" (pixel-art LinkedIn-style interface)
2. **Train/Upgrade** their professional competencies (retro RPG training UI)
3. **Form teams** for dungeon expeditions (classic party management)
4. **Complete dungeons** to earn loot and experience (16-bit RPG combat)
5. **Upgrade facilities** (pixel-art base management)
6. **Browse feed** of achievements and activity (pixelated LinkedIn-style feed)

## 🎯 Technical Implementation

### Database Models Needed
- `User` - Real players (authentication, progress, leaderboards)
- `Adventurer` - Bot characters with corporate classes & stats  
- `Guild` - Player's managed guild/company
- `Dungeon` - Quest content and rewards
- `Equipment` - Corporate "tools" and certifications
- `Facility` - Guild upgrades (training rooms, etc.)

### Frontend Structure (HTMX + FastAPI)
- **Guild Dashboard** - Pixel-art LinkedIn-style activity feed with real-time updates
- **Adventurer Profiles** - 16-bit LinkedIn profile layout for characters
- **Guild Pages** - Pixelated company page style for guilds
- **Recruitment Hub** - Retro LinkedIn job/talent search interface
- **Training Center** - Classic RPG upgrade interface
- **Dungeon Portal** - 16-bit RPG adventure interface
- **Inventory** - Pixel-art equipment management
- **Leaderboards** - Retro-styled rankings

## Corporate RPG Classes (Bot Adventurers)
- HR Manager (Summoner) - recruits teams
- Conflict Strategist (Fighter) - handles tough negotiations  
- Ethics Officer (Paladin) - maintains standards
- PR Manager (Bard) - manages reputation
- Sustainability Officer (Druid) - environmental focus
- Asset Manager (Rogue) - finds "creative solutions"
- Wellness Coordinator (Healer) - team support
- Stakeholder Manager (Warlock) - patron relationships  
- Innovation Director (Artificer) - creates solutions
- Performance Coach (Monk) - mindset & optimization

## Professional Competencies (RPG Stats)
- Personal Brand (Charisma) - networking & influence
- Bandwidth (Constitution) - workload capacity  
- Synergy (Strength) - team performance
- Growth Mindset (Intelligence) - learning & strategy
- Agility (Dexterity) - adaptation to change
- Optics (Wisdom) - perception management

## Development Commands
```bash
# Backend + Frontend (HTMX served by FastAPI)
cd backend && uv run python main.py

# Database migrations (SQLite for development)
cd backend && uv run alembic upgrade head

# Production deployment (PostgreSQL)
# Set ENVIRONMENT=production and DATABASE_URL in .env
cd backend && uv run alembic upgrade head
```

## Database Setup 🗄️
**Development**: Uses SQLite (`guildedin.db`) - no setup required!
**Production**: Uses PostgreSQL - set `ENVIRONMENT=production` in `.env`

## Current Status
- [x] Project structure setup
- [x] FastAPI backend with uv
- [x] **HTMX frontend with pixel-art styling**
- [x] **Database models restructured for Monster Rancher gameplay**
- [x] **Complete database schema with migrations**
- [x] **LinkedIn-inspired guild dashboard with HTMX interactivity**
- [ ] Bot adventurer generation system
- [ ] Connect HTMX frontend to database models
- [ ] Custom pixel-art RPG UI (dungeons, training, base management)
- [ ] Core gameplay mechanics
- [ ] Loot and equipment system
- [ ] Pixel art assets and sprite work

## Database Schema Complete ✅
- **Player** - Real users (authentication, save data, leaderboards)
- **Adventurer** - Bot characters with corporate classes & LinkedIn parodies
- **Guild** - Player's managed company with facilities and resources
- **Dungeon/DungeonRun** - Quest system with team expeditions
- **Equipment** - Corporate tools and certifications (loot system)
- **Facility** - Upgradeable guild buildings
- **Activity** - LinkedIn-style activity feed for achievements

## **NEW: Calendar & Daily Management System** 📅
- **GameRun** - Individual playthrough tracking (win/lose conditions, difficulty)
- **DailyPlan** - Daily action planning and execution results
- **Calendar** - Global calendar with special events and market conditions
- **DailyExpense** - Detailed cost tracking and income breakdown
- **ExpenseTemplate** - Cost calculation templates based on guild state

## **Daily Loop Mechanics** 🔄
1. **Morning**: Check guild status, pay daily costs
2. **Plan Day**: Choose action type:
   - **Full Day**: Dungeon expedition (high risk/reward)
   - **Partial Day**: Multiple smaller actions (recruit, train, upgrade)
3. **Execute**: Actions consume time/money resources
4. **Evening**: Calculate results and daily expenses
5. **End Day**: Player advances calendar → repeat until win/lose