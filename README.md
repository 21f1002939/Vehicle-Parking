# Vehicle Parking Management System

A comprehensive web-based parking management system built with Flask, Vue.js, Redis, and Celery for automated background jobs.

## Features

### Admin Features
- Dashboard with real-time statistics and analytics
- Manage parking lots (create, update, delete)
- Auto-generate parking spots for each lot
- View all parking spots and their occupancy status
- User management
- Revenue and occupancy reports with interactive charts

### User Features
- User registration and secure login
- Browse available parking lots with live availability
- Book parking spots with automatic allocation
- Release parking spots with automatic cost calculation
- View complete booking history
- Personal usage statistics and charts
- Export parking history to CSV

### Background Jobs (Celery)
- **Daily Reminders:** Automated notifications at 6 PM for users who haven't booked
- **Monthly Reports:** Comprehensive activity reports sent on 1st of each month
- **CSV Export:** Asynchronous parking history export

## Technology Stack

**Backend:**
- Flask 3.0.0 (Python web framework)
- Flask-Login (Session-based authentication)
- Flask-CORS (Cross-origin support)
- Flask-Caching (Redis caching for performance)
- SQLAlchemy (Database ORM)
- SQLite (Database)
- Celery 5.3.4 (Background job processing)
- Redis (Message broker & caching)

**Frontend:**
- Vue 3 (Progressive JavaScript framework)
- Vue Router 4 (Client-side routing)
- Axios (HTTP client)
- Vite (Build tool)
- Chart.js (Data visualization)

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Redis server (Memurai for Windows or redis-server for Linux/Mac)

## Installation & Setup

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The backend will run on `http://127.0.0.1:5000`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:5174`

### 3. Redis Setup

**Windows:**
- Download and install Memurai: https://www.memurai.com/
- Run: `memurai-server`

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
redis-server

# Mac with Homebrew
brew install redis
redis-server
```

### 4. Celery Setup (Optional - For Background Jobs)

**Terminal 1 - Celery Worker:**
```bash
cd backend
celery -A app.celery worker --loglevel=info --pool=solo
```

**Terminal 2 - Celery Beat Scheduler:**
```bash
cd backend
celery -A app.celery beat --loglevel=info
```

## Default Admin Credentials

- **Username:** admin
- **Password:** admin123

## Project Structure

```
Vehicles_parking/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── auth.py                # Authentication routes
│   ├── controllers.py         # Admin and user API endpoints
│   ├── models.py              # Database models
│   ├── celery_config.py       # Celery configuration
│   ├── tasks.py               # Background job definitions
│   ├── run_celery.py          # Celery worker startup script
│   ├── requirements.txt       # Python dependencies
│   ├── templates/
│   │   └── index.html         # Landing page
│   └── instance/
│       └── parking_app.db     # SQLite database
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AdminDashboard.vue
│   │   │   ├── AdminParkingLots.vue
│   │   │   ├── AdminParkingLotDetails.vue
│   │   │   ├── AdminUsers.vue
│   │   │   ├── AdminCharts.vue
│   │   │   ├── UserDashboard.vue
│   │   │   ├── UserBooking.vue
│   │   │   ├── UserHistory.vue
│   │   │   ├── LoginPage.vue
│   │   │   ├── RegisterPage.vue
│   │   │   └── Navbar.vue
│   │   ├── router/
│   │   │   └── index.js       # Vue Router configuration
│   │   ├── axios.js           # HTTP client configuration
│   │   ├── App.vue            # Root component
│   │   └── main.js            # Application entry point
│   ├── vite.config.js         # Vite configuration
│   └── package.json           # Node dependencies
│
└── README.md                  # This file
```

## Database Models

- **User:** User accounts (admin/regular users) with authentication
- **ParkingLot:** Parking lot information including location and pricing
- **ParkingSpot:** Individual parking spots with availability status
- **Reservation:** Booking records with timestamps and cost tracking

## API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - User registration
- `POST /login` - User login
- `POST /logout` - User logout
- `GET /me` - Get current user info
- `POST /change-password` - Change password

### Admin (`/api/admin`)
- `GET /dashboard` - Admin statistics
- `GET /parking-lots` - List all parking lots
- `POST /parking-lots` - Create new parking lot
- `GET /parking-lots/:id` - Get parking lot details
- `PUT /parking-lots/:id` - Update parking lot
- `DELETE /parking-lots/:id` - Delete parking lot
- `GET /users` - List all users
- `GET /charts/parking-lots` - Analytics and charts

### User (`/api/user`)
- `GET /dashboard` - User dashboard
- `GET /parking-lots/available` - Available parking lots
- `POST /book-spot` - Book parking spot
- `POST /release-spot/:id` - Release parking spot
- `GET /charts/my-usage` - Personal usage statistics
- `POST /export-history` - Export parking history to CSV

## Running the Application

### Minimal Setup (Without Background Jobs)
1. Start Redis: `memurai-server` or `redis-server`
2. Start Backend: `cd backend && python app.py`
3. Start Frontend: `cd frontend && npm run dev`
4. Visit: `http://localhost:5174`

### Full Setup (With Background Jobs)
1. Start Redis
2. Start Backend
3. Start Frontend
4. Start Celery Worker: `cd backend && celery -A app.celery worker --loglevel=info --pool=solo`
5. Start Celery Beat: `cd backend && celery -A app.celery beat --loglevel=info`

## Usage

### As Admin
1. Login with admin credentials
2. Create parking lots with number of spots
3. View dashboard with statistics
4. Monitor user activity and bookings
5. View analytics and revenue reports

### As User
1. Register a new account
2. Login with your credentials
3. Browse available parking lots
4. Book a parking spot
5. Release spot when done (cost is calculated automatically)
6. View booking history and personal statistics
7. Export history to CSV

## Key Features Explained

### Automatic Spot Allocation
When a parking lot is created, the system automatically generates parking spots with numbering (A-01, A-02, etc.)

### Smart Cost Calculation
Cost is calculated based on parking duration and hourly rate when the spot is released.

### Real-time Availability
The system shows live availability of parking spots across all locations.

### Background Jobs
- Daily reminders for inactive users
- Monthly activity reports with statistics
- Asynchronous CSV export to avoid blocking the UI

### Performance Optimization
- Redis caching for frequently accessed data
- Optimized database queries
- Automatic cache invalidation on data changes

## Technologies Used

This project demonstrates proficiency in:
- **Backend Development:** Flask, SQLAlchemy, RESTful APIs
- **Frontend Development:** Vue.js, SPA architecture, component-based design
- **Database:** SQLAlchemy ORM, relational database design
- **Authentication:** Session-based authentication with Flask-Login
- **Asynchronous Processing:** Celery for background jobs
- **Caching:** Redis for performance optimization
- **Real-time Updates:** Dynamic data fetching and display

## License

This project is developed for educational purposes.
