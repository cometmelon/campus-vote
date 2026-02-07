# CampusVote - Campus Election Dashboard System

A modern, full-stack web application for managing campus elections with secure voting, batch email notifications, and real-time dashboards.

## 🚀 Features

### Admin Features
- **Dashboard**: Real-time KPIs (total students, active elections, voter turnout, clubs)
- **Election Management**: Create, activate, and end elections with multiple candidates
- **Voting Portal**: Send batch voting links via email with load balancing
- **Club Management**: Register and manage student organizations
- **Department Analytics**: View turnout statistics by department

### Student Features
- **Personal Dashboard**: View active elections for your department
- **Secure Voting**: One-time unique voting links sent via email
- **Anonymous Votes**: Secure, anonymous vote casting
- **Club Discovery**: Browse and explore campus clubs

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM with SQLite (dev) / PostgreSQL (prod)
- **Pydantic**: Data validation and settings
- **JWT Authentication**: Secure token-based auth
- **Resend**: Email service for voting links
- **Bcrypt**: Password hashing

### Frontend
- **React 18**: UI library
- **Vite**: Build tool and dev server
- **TanStack Query**: Data fetching and caching
- **Wouter**: Lightweight routing
- **Tailwind CSS**: Utility-first styling
- **shadcn/ui**: Component library
- **Recharts**: Data visualization

## 📦 Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional)
cp .env.example .env
# Edit .env and add your RESEND_API_KEY if you have one

# Run the server
uvicorn main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

The frontend will be available at `http://localhost:5174`

## 🔑 Demo Credentials

### Admin Account
- **Student ID**: `admin`
- **Password**: `admin`

### Student Account
- **Student ID**: `student`
- **Password**: `student`

## 📁 Project Structure

```
campus-vote/
├── backend/
│   ├── models/          # SQLAlchemy models
│   ├── routers/         # API endpoints
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   ├── main.py          # FastAPI app
│   └── seed.py          # Demo data seeding
│
└── frontend/
    ├── src/
    │   ├── components/  # Reusable UI components
    │   ├── context/     # React context (Auth)
    │   ├── lib/         # Utilities and API client
    │   ├── pages/       # Page components
    │   ├── App.jsx      # Main app with routing
    │   └── main.jsx     # Entry point
    ├── public/          # Static assets
    └── index.html       # HTML template
```

## 🔄 Database

The application uses **SQLite** for local development (auto-created as `campusvote.db`). For production, configure PostgreSQL via the `DATABASE_URL` environment variable.

### Seed Data
The database is automatically seeded with demo data on startup:
- 6 departments (CSE, ECE, MECH, CIVIL, ARTS, SCI)
- Admin and student users
- Sample elections (active, planned, finished)
- Candidates for each election
- Sample club

To reset the database:
```bash
# Stop the backend
# Delete campusvote.db
# Restart the backend - it will recreate and reseed
```

## 📧 Email Configuration

The app uses [Resend](https://resend.com) for sending voting links.

1. Sign up at https://resend.com
2. Get your API key
3. Add to `backend/.env`:
   ```
   RESEND_API_KEY=re_your_key_here
   FROM_EMAIL=noreply@yourdomain.com
   ```

**Without Resend**: The app will simulate email sending and log to console.

## 🎯 Usage

### Creating an Election (Admin)
1. Login as admin
2. Go to **Elections** page
3. Click **Create Election**
4. Fill in details and add candidates
5. Submit to create

### Activating & Sending Links (Admin)
1. Go to **Elections** page
2. Click **Activate** on a planned election
3. Go to **Voting Portal**
4. Select the active election
5. Click **Send Links** to email students

### Voting (Student)
1. Check your email for the voting link
2. Click the unique link
3. Select your candidate
4. Submit vote (one-time, anonymous)

## 🚢 Deployment

### Backend (Render)
1. Create a new Web Service on Render
2. Connect your GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `DATABASE_URL` (PostgreSQL)
   - `SECRET_KEY`
   - `RESEND_API_KEY`

### Frontend (Vercel)
1. Import project on Vercel
2. Set root directory to `frontend`
3. Build command: `npm run build`
4. Output directory: `dist`
5. Add environment variable:
   - `VITE_API_BASE` (your backend URL)

## 📝 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

### Key Endpoints
- `POST /auth/login` - User login
- `GET /elections` - List elections
- `POST /elections` - Create election (admin)
- `POST /voting/send-links` - Send voting links (admin)
- `POST /voting/cast/{token}` - Cast vote
- `GET /dashboard/stats` - Dashboard KPIs (admin)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use this project for learning or production.

## 🐛 Troubleshooting

### Backend won't start
- Check Python version (3.9+)
- Ensure virtual environment is activated
- Delete `campusvote.db` and restart

### Frontend won't start
- Check Node version (18+)
- Delete `node_modules` and run `npm install` again
- Check if port 5174 is available

### Buttons not working
- Open browser console (F12) to see error logs
- Check if backend is running on port 8000
- Verify API calls in Network tab

### Database issues
- Delete `campusvote.db` file
- Restart backend to recreate fresh database

## 📞 Support

For issues or questions, please open an issue on GitHub.

---

Built with ❤️ for campus democracy
