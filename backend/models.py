from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # For Flask-Login
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    reservations = db.relationship('Reservation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_role(self):
        return 'admin' if self.is_admin else 'user'
    
    def __repr__(self):
        return f'<User {self.username} - Role: {self.get_role()}>'

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prime_location_name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price per hour
    address = db.Column(db.String(500), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    number_of_spots = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    parking_spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade='all, delete-orphan')
    
    def get_available_spots_count(self):
        return sum(1 for spot in self.parking_spots if spot.status == 'A')
    
    def get_occupied_spots_count(self):
        return sum(1 for spot in self.parking_spots if spot.status == 'O')
    
    def __repr__(self):
        return f'<ParkingLot {self.prime_location_name}>'

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    spot_number = db.Column(db.String(20), nullable=False)  # e.g., "A-01", "B-15"
    status = db.Column(db.String(1), default='A', nullable=False)  # 'O' - Occupied, 'A' - Available
    vehicle_type = db.Column(db.String(20), default='4-wheeler', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('lot_id', 'spot_number', name='unique_spot_per_lot'),)
    
    def is_available(self):
        return self.status == 'A'
    
    def mark_occupied(self):
        self.status = 'O'
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_available(self):
        self.status = 'A'
        self.updated_at = datetime.now(timezone.utc)
    
    def __repr__(self):
        return f'<ParkingSpot {self.spot_number} - Status: {self.status}>'

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=True)  # Vehicle registration number
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, default=0.0, nullable=True)
    status = db.Column(db.String(20), default='active', nullable=False)  # 'active', 'completed', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def calculate_cost(self):
        if self.leaving_timestamp:
            duration = (self.leaving_timestamp - self.parking_timestamp).total_seconds() / 3600
            price_per_hour = self.parking_spot.parking_lot.price
            self.parking_cost = round(max(duration, 1) * price_per_hour, 2)
        return self.parking_cost
    
    def complete_reservation(self):
        self.leaving_timestamp = datetime.now(timezone.utc)
        self.status = 'completed'
        self.calculate_cost()
        self.parking_spot.mark_available()
        self.updated_at = datetime.now(timezone.utc)
    
    def get_duration_hours(self):
        if self.leaving_timestamp:
            return round((self.leaving_timestamp - self.parking_timestamp).total_seconds() / 3600, 2)
        else:
            return round((datetime.now(timezone.utc) - self.parking_timestamp).total_seconds() / 3600, 2)
    
    def __repr__(self):
        return f'<Reservation User:{self.user_id} Spot:{self.spot_id} Status:{self.status}>'

def create_admin_user():
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@parkingapp.com',
            is_admin=True,
            phone_number='0000000000'
        )
        admin.set_password('admin123') 
        db.session.add(admin)
        db.session.commit()
    return admin

def init_db(app):
    with app.app_context():
        db.create_all()
        create_admin_user()
