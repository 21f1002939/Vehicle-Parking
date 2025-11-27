from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, User, ParkingLot, ParkingSpot, Reservation
from auth import admin_required, user_required
from datetime import datetime, timezone
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Import cache from app (will be set after app initialization)
cache = None

def init_cache(cache_instance):
    global cache
    cache = cache_instance

# Helper function to use cache safely
def safe_cache_get(key, default=None):
    """Safely get from cache, return default if cache not available"""
    try:
        if cache:
            return cache.get(key)
    except:
        pass
    return default

def safe_cache_set(key, value, timeout=60):
    """Safely set cache, ignore if cache not available"""
    try:
        if cache:
            cache.set(key, value, timeout=timeout)
    except:
        pass

def safe_cache_delete(key):
    """Safely delete from cache, ignore if cache not available"""
    try:
        if cache:
            cache.delete(key)
    except:
        pass

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    try:
        total_lots = ParkingLot.query.count()
        total_spots = ParkingSpot.query.count()
        available_spots = ParkingSpot.query.filter_by(status='A').count()
        occupied_spots = ParkingSpot.query.filter_by(status='O').count()
        total_users = User.query.filter_by(is_admin=False).count()
        active_reservations = Reservation.query.filter_by(status='active').count()
        completed_reservations = Reservation.query.filter_by(status='completed').count()
        
        recent_reservations = Reservation.query.order_by(
            Reservation.created_at.desc()
        ).limit(10).all()
        
        recent_data = []
        for res in recent_reservations:
            recent_data.append({
                'id': res.id,
                'user': res.user.username,
                'parking_lot': res.parking_spot.parking_lot.prime_location_name,
                'spot': res.parking_spot.spot_number,
                'status': res.status,
                'parking_time': res.parking_timestamp.isoformat(),
                'duration': res.get_duration_hours() if res.status == 'active' else None,
                'cost': res.parking_cost
            })
        
        response_data = {
            'status': 'success',
            'dashboard': {
                'parking_lots': {
                    'total': total_lots
                },
                'parking_spots': {
                    'total': total_spots,
                    'available': available_spots,
                    'occupied': occupied_spots
                },
                'users': {
                    'total': total_users
                },
                'reservations': {
                    'active': active_reservations,
                    'completed': completed_reservations,
                    'total': active_reservations + completed_reservations
                },
                'recent_activity': recent_data
            }
        }
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to load dashboard: {str(e)}'
        }), 500

# ============= PARKING LOT MANAGEMENT =============

@admin_bp.route('/parking-lots', methods=['GET'])
@admin_required
def get_all_parking_lots():
    try:
        lots = ParkingLot.query.all()
        
        lots_data = []
        for lot in lots:
            lots_data.append({
                'id': lot.id,
                'name': lot.prime_location_name,
                'price': lot.price,
                'address': lot.address,
                'pin_code': lot.pin_code,
                'total_spots': lot.number_of_spots,
                'available_spots': lot.get_available_spots_count(),
                'occupied_spots': lot.get_occupied_spots_count(),
                'description': lot.description,
                'created_at': lot.created_at.isoformat()
            })
        
        response_data = {
            'status': 'success',
            'parking_lots': lots_data,
            'total': len(lots_data)
        }
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch parking lots: {str(e)}'
        }), 500

@admin_bp.route('/parking-lots', methods=['POST'])
@admin_required
def create_parking_lot():
    try:
        data = request.get_json()
        
        required_fields = ['name', 'price', 'address', 'pin_code', 'number_of_spots']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        if data['number_of_spots'] <= 0 or data['number_of_spots'] > 1000:
            return jsonify({
                'status': 'error',
                'message': 'Number of spots must be between 1 and 1000'
            }), 400
        
        new_lot = ParkingLot(
            prime_location_name=data['name'],
            price=float(data['price']),
            address=data['address'],
            pin_code=data['pin_code'],
            number_of_spots=int(data['number_of_spots']),
            description=data.get('description', '')
        )
        
        db.session.add(new_lot)
        db.session.flush()  # Get the lot ID before creating spots
        
        spots_created = []
        num_spots = int(data['number_of_spots'])
        
        section_size = 100
        sections = (num_spots + section_size - 1) // section_size  # Ceiling division
        
        spot_number = 1
        for section_idx in range(sections):
            section_letter = chr(65 + section_idx)  # A, B, C, etc.
            
            remaining_spots = num_spots - (section_idx * section_size)
            spots_in_section = min(section_size, remaining_spots)
            
            for i in range(1, spots_in_section + 1):
                spot = ParkingSpot(
                    lot_id=new_lot.id,
                    spot_number=f"{section_letter}-{i:02d}",  # e.g., A-01, A-02
                    status='A',  # Available
                    vehicle_type='4-wheeler'
                )
                db.session.add(spot)
                spots_created.append(spot.spot_number)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Parking lot created with {len(spots_created)} spots',
            'parking_lot': {
                'id': new_lot.id,
                'name': new_lot.prime_location_name,
                'total_spots': new_lot.number_of_spots,
                'spots_created': spots_created[:10] + ['...'] if len(spots_created) > 10 else spots_created
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to create parking lot: {str(e)}'
        }), 500

@admin_bp.route('/parking-lots/<int:lot_id>', methods=['GET'])
@admin_required
def get_parking_lot(lot_id):
    try:
        lot = ParkingLot.query.get(lot_id)
        
        if not lot:
            return jsonify({
                'status': 'error',
                'message': 'Parking lot not found'
            }), 404
        
        spots = []
        for spot in lot.parking_spots:
            spot_info = {
                'id': spot.id,
                'spot_number': spot.spot_number,
                'status': spot.status,
                'vehicle_type': spot.vehicle_type
            }
            
            if spot.status == 'O':
                active_reservation = Reservation.query.filter_by(
                    spot_id=spot.id,
                    status='active'
                ).first()
                
                if active_reservation:
                    spot_info['reservation'] = {
                        'user': active_reservation.user.username,
                        'vehicle_number': active_reservation.vehicle_number,
                        'parked_since': active_reservation.parking_timestamp.isoformat(),
                        'duration_hours': active_reservation.get_duration_hours()
                    }
            
            spots.append(spot_info)
        
        return jsonify({
            'status': 'success',
            'parking_lot': {
                'id': lot.id,
                'name': lot.prime_location_name,
                'price': lot.price,
                'address': lot.address,
                'pin_code': lot.pin_code,
                'total_spots': lot.number_of_spots,
                'available_spots': lot.get_available_spots_count(),
                'occupied_spots': lot.get_occupied_spots_count(),
                'description': lot.description,
                'spots': spots
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch parking lot: {str(e)}'
        }), 500

@admin_bp.route('/parking-lots/<int:lot_id>', methods=['PUT'])
@admin_required
def update_parking_lot(lot_id):
    try:
        lot = ParkingLot.query.get(lot_id)
        
        if not lot:
            return jsonify({
                'status': 'error',
                'message': 'Parking lot not found'
            }), 404
        
        data = request.get_json()
        
        if 'name' in data:
            lot.prime_location_name = data['name']
        if 'price' in data:
            lot.price = float(data['price'])
        if 'address' in data:
            lot.address = data['address']
        if 'pin_code' in data:
            lot.pin_code = data['pin_code']
        if 'description' in data:
            lot.description = data['description']
        
        lot.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Parking lot updated successfully',
            'parking_lot': {
                'id': lot.id,
                'name': lot.prime_location_name,
                'price': lot.price
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to update parking lot: {str(e)}'
        }), 500

@admin_bp.route('/parking-lots/<int:lot_id>', methods=['DELETE'])
@admin_required
def delete_parking_lot(lot_id):
    try:
        lot = ParkingLot.query.get(lot_id)
        
        if not lot:
            return jsonify({
                'status': 'error',
                'message': 'Parking lot not found'
            }), 404
        
        occupied_spots = lot.get_occupied_spots_count()
        
        if occupied_spots > 0:
            return jsonify({
                'status': 'error',
                'message': f'Cannot delete parking lot. {occupied_spots} spots are still occupied.',
                'occupied_spots': occupied_spots
            }), 400
        
        lot_name = lot.prime_location_name
        db.session.delete(lot)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Parking lot "{lot_name}" deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to delete parking lot: {str(e)}'
        }), 500

# ============= USER MANAGEMENT =============

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    try:
        users = User.query.filter_by(is_admin=False).all()
        
        users_data = []
        for user in users:
            total_reservations = Reservation.query.filter_by(user_id=user.id).count()
            active_reservations = Reservation.query.filter_by(user_id=user.id, status='active').count()
            
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone_number': user.phone_number,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat(),
                'total_reservations': total_reservations,
                'active_reservations': active_reservations
            })
        
        return jsonify({
            'status': 'success',
            'users': users_data,
            'total': len(users_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch users: {str(e)}'
        }), 500

# ============= CHARTS & STATISTICS =============

@admin_bp.route('/charts/parking-lots', methods=['GET'])
@admin_required
def get_parking_lot_charts():
    try:
        lots = ParkingLot.query.all()
        
        chart_data = []
        for lot in lots:
            total_spots = lot.number_of_spots
            occupied = lot.get_occupied_spots_count()
            occupancy_rate = (occupied / total_spots * 100) if total_spots > 0 else 0
            
            revenue = db.session.query(func.sum(Reservation.parking_cost)).join(
                ParkingSpot
            ).filter(
                ParkingSpot.lot_id == lot.id,
                Reservation.status == 'completed'
            ).scalar() or 0
            
            chart_data.append({
                'name': lot.prime_location_name,
                'total_spots': total_spots,
                'occupied_spots': occupied,
                'available_spots': total_spots - occupied,
                'occupancy_rate': round(occupancy_rate, 2),
                'revenue': round(float(revenue), 2)
            })
        
        return jsonify({
            'status': 'success',
            'charts': chart_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate charts: {str(e)}'
        }), 500

# ============= USER BLUEPRINT =============
user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/dashboard', methods=['GET'])
@login_required
def user_dashboard():
    try:
        active_reservations = Reservation.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).all()
        
        completed_reservations = Reservation.query.filter_by(
            user_id=current_user.id,
            status='completed'
        ).order_by(Reservation.leaving_timestamp.desc()).limit(10).all()
        
        total_spent = db.session.query(func.sum(Reservation.parking_cost)).filter(
            Reservation.user_id == current_user.id,
            Reservation.status == 'completed'
        ).scalar() or 0
        
        active_data = []
        for res in active_reservations:
            active_data.append({
                'id': res.id,
                'parking_lot': res.parking_spot.parking_lot.prime_location_name,
                'spot_number': res.parking_spot.spot_number,
                'vehicle_number': res.vehicle_number,
                'parked_since': res.parking_timestamp.isoformat(),
                'duration_hours': res.get_duration_hours(),
                'current_cost': round(res.get_duration_hours() * res.parking_spot.parking_lot.price, 2)
            })
        
        history_data = []
        for res in completed_reservations:
            history_data.append({
                'id': res.id,
                'parking_lot': res.parking_spot.parking_lot.prime_location_name,
                'spot_number': res.parking_spot.spot_number,
                'parked_at': res.parking_timestamp.isoformat(),
                'left_at': res.leaving_timestamp.isoformat() if res.leaving_timestamp else None,
                'duration_hours': res.get_duration_hours(),
                'cost': res.parking_cost
            })
        
        return jsonify({
            'status': 'success',
            'dashboard': {
                'user': {
                    'username': current_user.username,
                    'email': current_user.email
                },
                'active_reservations': active_data,
                'recent_history': history_data,
                'statistics': {
                    'total_spent': round(float(total_spent), 2),
                    'active_bookings': len(active_data),
                    'total_bookings': Reservation.query.filter_by(user_id=current_user.id).count()
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to load dashboard: {str(e)}'
        }), 500

@user_bp.route('/parking-lots/available', methods=['GET'])
@login_required
def get_available_parking_lots():
    try:
        lots = ParkingLot.query.all()
        
        available_lots = []
        for lot in lots:
            available_spots = lot.get_available_spots_count()
            
            if available_spots > 0:  # Only show lots with available spots
                available_lots.append({
                    'id': lot.id,
                    'name': lot.prime_location_name,
                    'price': lot.price,
                    'price_per_hour': lot.price,
                    'address': lot.address,
                    'pin_code': lot.pin_code,
                    'available_spots': available_spots,
                    'total_spots': lot.number_of_spots,
                    'description': lot.description
                })
        
        response_data = {
            'status': 'success',
            'parking_lots': available_lots,
            'total': len(available_lots)
        }
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch parking lots: {str(e)}'
        }), 500

@user_bp.route('/book-spot', methods=['POST'])
@login_required
def book_parking_spot():
    try:
        data = request.get_json()
        
        if not data or 'lot_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'lot_id is required'
            }), 400
        
        lot_id = data['lot_id']
        vehicle_number = data.get('vehicle_number', '')
        
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return jsonify({
                'status': 'error',
                'message': 'Parking lot not found'
            }), 404
        
        available_spot = ParkingSpot.query.filter_by(
            lot_id=lot_id,
            status='A'
        ).first()
        
        if not available_spot:
            return jsonify({
                'status': 'error',
                'message': 'No available spots in this parking lot'
            }), 400
        
        existing_reservation = Reservation.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()
        
        if existing_reservation:
            return jsonify({
                'status': 'error',
                'message': 'You already have an active reservation. Please release it first.',
                'active_reservation': {
                    'lot': existing_reservation.parking_spot.parking_lot.prime_location_name,
                    'spot': existing_reservation.parking_spot.spot_number
                }
            }), 400
        
        available_spot.mark_occupied()
        
        new_reservation = Reservation(
            spot_id=available_spot.id,
            user_id=current_user.id,
            vehicle_number=vehicle_number,
            status='active'
        )
        
        db.session.add(new_reservation)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Parking spot booked successfully',
            'reservation': {
                'id': new_reservation.id,
                'parking_lot': lot.prime_location_name,
                'spot_number': available_spot.spot_number,
                'vehicle_number': vehicle_number,
                'price_per_hour': lot.price,
                'parked_at': new_reservation.parking_timestamp.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to book parking spot: {str(e)}'
        }), 500

@user_bp.route('/release-spot/<int:reservation_id>', methods=['POST'])
@login_required
def release_parking_spot(reservation_id):
    try:
        reservation = Reservation.query.get(reservation_id)
        
        if not reservation:
            return jsonify({
                'status': 'error',
                'message': 'Reservation not found'
            }), 404
        
        if reservation.user_id != current_user.id:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403
        
        if reservation.status != 'active':
            return jsonify({
                'status': 'error',
                'message': 'Reservation is not active'
            }), 400
        
        reservation.complete_reservation()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Parking spot released successfully',
            'receipt': {
                'reservation_id': reservation.id,
                'parking_lot': reservation.parking_spot.parking_lot.prime_location_name,
                'spot_number': reservation.parking_spot.spot_number,
                'vehicle_number': reservation.vehicle_number,
                'parked_at': reservation.parking_timestamp.isoformat(),
                'left_at': reservation.leaving_timestamp.isoformat(),
                'duration_hours': reservation.get_duration_hours(),
                'price_per_hour': reservation.parking_spot.parking_lot.price,
                'total_cost': reservation.parking_cost
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to release parking spot: {str(e)}'
        }), 500

@user_bp.route('/charts/my-usage', methods=['GET'])
@login_required
def get_user_charts():
    try:
        reservations = Reservation.query.filter_by(
            user_id=current_user.id,
            status='completed'
        ).all()
        
        total_hours = sum(res.get_duration_hours() for res in reservations)
        total_cost = sum(res.parking_cost or 0 for res in reservations)
        
        lot_usage = {}
        for res in reservations:
            lot_name = res.parking_spot.parking_lot.prime_location_name
            if lot_name not in lot_usage:
                lot_usage[lot_name] = {
                    'visits': 0,
                    'total_hours': 0,
                    'total_cost': 0
                }
            lot_usage[lot_name]['visits'] += 1
            lot_usage[lot_name]['total_hours'] += res.get_duration_hours()
            lot_usage[lot_name]['total_cost'] += res.parking_cost or 0
        
        chart_data = []
        for lot_name, stats in lot_usage.items():
            chart_data.append({
                'parking_lot': lot_name,
                'visits': stats['visits'],
                'total_hours': round(stats['total_hours'], 2),
                'total_cost': round(stats['total_cost'], 2)
            })
        
        return jsonify({
            'status': 'success',
            'charts': {
                'summary': {
                    'total_parkings': len(reservations),
                    'total_hours': round(total_hours, 2),
                    'total_spent': round(total_cost, 2),
                    'average_cost_per_visit': round(total_cost / len(reservations), 2) if reservations else 0
                },
                'by_parking_lot': chart_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate charts: {str(e)}'
        }), 500


@user_bp.route('/export-history', methods=['POST'])
@login_required
def export_parking_history():
    try:
        from tasks import export_user_parking_history
        
        # Trigger async Celery task
        task = export_user_parking_history.delay(current_user.id)
        
        return jsonify({
            'status': 'success',
            'message': 'Export request submitted. You will receive an email with your parking history CSV file shortly.',
            'task_id': task.id
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to submit export request: {str(e)}'
        }), 500


@user_bp.route('/export-status/<task_id>', methods=['GET'])
@login_required
def check_export_status(task_id):
    """Check the status of CSV export task"""
    try:
        from celery.result import AsyncResult
        from app import celery
        
        task_result = AsyncResult(task_id, app=celery)
        
        response = {
            'task_id': task_id,
            'state': task_result.state,
            'ready': task_result.ready(),
        }
        
        if task_result.ready():
            if task_result.successful():
                response['result'] = task_result.result
            else:
                response['error'] = str(task_result.info)
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to check status: {str(e)}'
        }), 500
