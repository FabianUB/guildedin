# GuildedIn 🏰

> LinkedIn parody RPG where adventurers find their guild!

A fantasy-themed professional networking platform that combines LinkedIn's functionality with RPG game mechanics. Think "LinkedIn but for adventurers seeking guilds."

## 🎮 Concept

Professional networking meets fantasy RPG:
- **Adventurer Profiles**: LinkedIn profiles styled as RPG character sheets
- **Guild Pages**: Company pages with fantasy guild aesthetics  
- **Quest Listings**: Job postings as dungeon quests
- **Corporate Classes**: Job roles disguised as RPG classes (HR Manager = Summoner, Stakeholder Manager = Warlock, etc.)
- **Professional Stats**: LinkedIn skills as RPG attributes (Personal Brand = Charisma, Bandwidth = Constitution, etc.)

## 🏗️ Tech Stack

- **Backend**: Python + FastAPI + uv + PostgreSQL
- **Frontend**: SvelteKit + Tailwind CSS
- **Database**: PostgreSQL with Alembic migrations
- **Styling**: Fantasy RPG theme with professional layout

## 🚀 Quick Start

### Backend
```bash
cd backend
uv run python scripts/dev.py
```

### Frontend  
```bash
cd frontend
npm install --legacy-peer-deps  # if dependencies fail
npm run dev
```

### Database
```bash
# SQLite database created automatically - no setup needed!
cd backend  
uv run alembic upgrade head
```

**Development**: Uses SQLite (no setup required)  
**Production**: Uses PostgreSQL (set `ENVIRONMENT=production` in `.env`)

## 🎨 Corporate RPG Classes

Our LinkedIn parody job titles that secretly map to RPG classes:

- **HR Manager** (Summoner) - recruits and manages teams
- **Conflict Strategist** (Fighter) - handles disputes and negotiations  
- **Ethics Officer** (Paladin) - upholds company values
- **PR Manager** (Bard) - crafts narratives and reputation
- **Sustainability Officer** (Druid) - environmental/social responsibility
- **Asset Manager** (Rogue) - optimizes resources and finds "opportunities"
- **Wellness Coordinator** (Healer) - employee health and work-life balance
- **Stakeholder Manager** (Warlock) - derives power from appeasing "patrons"
- **Innovation Director** (Artificer) - creates new solutions and processes
- **Performance Coach** (Monk) - focuses on mindset and continuous improvement

## 📊 Professional Competencies (RPG Stats)

LinkedIn buzzwords that map to classic RPG attributes:

- **Personal Brand** (Charisma) - networking power and influence
- **Bandwidth** (Constitution) - workload capacity without burnout  
- **Synergy** (Strength) - ability to drive team performance
- **Growth Mindset** (Intelligence) - learning agility and strategic thinking
- **Agility** (Dexterity) - pivoting quickly to market changes
- **Optics** (Wisdom) - perception management and reading the room

## 🏰 Development Status

- [x] Project structure and backend setup
- [x] Frontend SvelteKit + Tailwind setup  
- [x] Database models and schemas
- [ ] Core UI components
- [ ] Authentication system
- [ ] Real-time features