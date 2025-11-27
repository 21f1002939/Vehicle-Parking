from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from flask_login import LoginManager, current_user
from flask_caching import Cache
from models import db, User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime, timedelta
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'my-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Redis & Celery Configuration
app.config['broker_url'] = 'redis://localhost:6379/0'
app.config['result_backend'] = 'redis://localhost:6379/0'

# Flask-Caching Configuration
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/1'
app.config['CACHE_DEFAULT_TIMEOUT'] = 60

app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_NAME'] = 'parking_session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)

# Check if Redis is available
REDIS_AVAILABLE = False
try:
    import redis
    r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=1)
    r.ping()
    REDIS_AVAILABLE = True
    print("[OK] Redis connection successful!")
except Exception as e:
    print(f"[WARNING] Redis not available: {e}")
    print("   Running without Redis caching and Celery")
    print("   To enable: Install Redis and restart the application")
    # Fallback to simple cache
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 60

# Enable CORS for all origins
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Accept"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["Content-Type", "Set-Cookie"]
)

db.init_app(app)

# Initialize Flask-Caching
cache = Cache(app)

# Initialize Celery only if Redis is available
celery = None
if REDIS_AVAILABLE:
    try:
        from celery_config import make_celery
        celery = make_celery(app)
    except Exception as e:
        pass

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# Return JSON for unauthorized API requests instead of redirecting
@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({
        'status': 'error',
        'message': 'Authentication required. Please log in.'
    }), 401

# Add after_request handler to ensure CORS headers are set properly
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Import and register blueprints
from auth import auth_bp
from controllers import admin_bp, user_bp, init_cache

# Initialize cache in controllers
init_cache(cache)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

DEFAULT_ADMIN = {
    'username': 'admin',
    'email': 'admin@parkingapp.com',
    'password': 'admin123',
    'phone_number': '9999999999'
}


def init_database():
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(is_admin=True).first()
        
        if not admin:
            admin = User(
                username=DEFAULT_ADMIN['username'],
                email=DEFAULT_ADMIN['email'],
                is_admin=True,
                is_active=True,
                phone_number=DEFAULT_ADMIN['phone_number']
            )
            admin.set_password(DEFAULT_ADMIN['password'])
            db.session.add(admin)
            db.session.commit()
            print("Database initialized with default admin user.")
        else:
            print("Database already initialized.")


@app.route('/')
def index():
    return render_template('index.html')


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Resource not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'status': 'error',
        'message': 'Bad request'
    }), 400


if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
