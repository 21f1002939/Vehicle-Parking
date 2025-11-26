from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from functools import wraps

# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({
                'status': 'error',
                'message': 'Admin access required.'
            }), 403
        return f(*args, **kwargs)
    return decorated_function


def user_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.is_admin:
            return jsonify({
                'status': 'error',
                'message': 'This endpoint is for regular users only.'
            }), 403
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({
                'status': 'error',
                'message': 'Username, email, and password are required'
            }), 400
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'status': 'error',
                'message': 'Username already exists'
            }), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'status': 'error',
                'message': 'Email already registered'
            }), 400
        
        new_user = User(
            username=data['username'],
            email=data['email'],
            phone_number=data.get('phone_number', ''),
            is_admin=False
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        
        return jsonify({
            'status': 'success',
            'message': 'Registration successful',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'role': new_user.get_role()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Registration failed: {str(e)}'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('password'):
            return jsonify({
                'status': 'error',
                'message': 'Username/Email and password are required'
            }), 400
        
        user = None
        if data.get('username'):
            user = User.query.filter_by(username=data['username']).first()
        elif data.get('email'):
            user = User.query.filter_by(email=data['email']).first()
        else:
            return jsonify({
                'status': 'error',
                'message': 'Please provide username or email'
            }), 400
        
        if not user or not user.check_password(data['password']):
            return jsonify({
                'status': 'error',
                'message': 'Invalid credentials'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'status': 'error',
                'message': 'Account is deactivated. Please contact admin.'
            }), 403
        
        login_user(user, remember=True)
        session.permanent = True
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.get_role(),
                'is_admin': user.is_admin
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Login failed: {str(e)}'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    username = current_user.username
    logout_user()
    return jsonify({
        'status': 'success',
        'message': f'User {username} logged out successfully'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        'status': 'success',
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'phone_number': current_user.phone_number,
            'role': current_user.get_role(),
            'is_admin': current_user.is_admin,
            'created_at': current_user.created_at.isoformat()
        }
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    try:
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({
                'status': 'error',
                'message': 'Current password and new password are required'
            }), 400
        
        if not current_user.check_password(data['current_password']):
            return jsonify({
                'status': 'error',
                'message': 'Current password is incorrect'
            }), 401
        
        current_user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Password change failed: {str(e)}'
        }), 500
