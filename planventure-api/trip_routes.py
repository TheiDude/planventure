"""
Trip routes for PlanVenture API.

This module provides CRUD operations for trip management with proper
authentication, validation, and user authorization.
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_
from models import db, Trip, User
from auth_middleware import require_auth, get_current_user, get_current_user_id

# Create trips blueprint
trips_bp = Blueprint('trips', __name__, url_prefix='/api/trips')

def validate_trip_data(data, is_update=False):
    """
    Validate trip data for creation or update.
    
    Args:
        data (dict): Trip data to validate
        is_update (bool): Whether this is an update operation
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not data:
        return False, "Request must contain JSON data"
    
    # Required fields for creation
    if not is_update:
        required_fields = ['destination', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"{field} is required"
    
    # Validate dates if provided
    date_fields = ['start_date', 'end_date']
    parsed_dates = {}
    
    for field in date_fields:
        if field in data and data[field]:
            try:
                parsed_dates[field] = datetime.strptime(data[field], '%Y-%m-%d').date()
            except ValueError:
                return False, f"Invalid {field} format. Use YYYY-MM-DD"
    
    # Check date logic if both dates provided
    if 'start_date' in parsed_dates and 'end_date' in parsed_dates:
        if parsed_dates['start_date'] > parsed_dates['end_date']:
            return False, "Start date must be before end date"
    
    # Validate budget if provided
    if 'budget' in data and data['budget'] is not None:
        try:
            budget = float(data['budget'])
            if budget < 0:
                return False, "Budget must be a positive number"
        except (ValueError, TypeError):
            return False, "Budget must be a valid number"
    
    # Validate coordinates if provided
    if 'latitude' in data or 'longitude' in data:
        try:
            if 'latitude' in data:
                lat = float(data['latitude'])
                if not -90 <= lat <= 90:
                    return False, "Latitude must be between -90 and 90"
            
            if 'longitude' in data:
                lng = float(data['longitude'])
                if not -180 <= lng <= 180:
                    return False, "Longitude must be between -180 and 180"
        except (ValueError, TypeError):
            return False, "Coordinates must be valid numbers"
    
    # Validate itinerary if provided
    if 'itinerary' in data and data['itinerary'] is not None:
        if not isinstance(data['itinerary'], list):
            return False, "Itinerary must be a list"
        
        for i, item in enumerate(data['itinerary']):
            if not isinstance(item, dict):
                return False, f"Itinerary item {i+1} must be an object"
    
    return True, None

def check_trip_ownership(trip_id, user_id):
    """
    Check if the current user owns the specified trip.
    
    Args:
        trip_id (int): ID of the trip
        user_id (int): ID of the current user
    
    Returns:
        Trip or None: Trip object if owned by user, None otherwise
    """
    return Trip.query.filter_by(id=trip_id, user_id=user_id).first()

@trips_bp.route('', methods=['GET'])
@require_auth
def list_trips():
    """
    Get all trips for the authenticated user with optional filtering and pagination.
    
    Query Parameters:
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: 10, max: 100)
        - destination (str): Filter by destination (partial match)
        - status (str): Filter by status (planned, ongoing, completed, cancelled)
        - start_date_from (str): Filter trips starting from this date (YYYY-MM-DD)
        - start_date_to (str): Filter trips starting before this date (YYYY-MM-DD)
        - budget_min (float): Minimum budget filter
        - budget_max (float): Maximum budget filter
        - sort (str): Sort field (destination, start_date, end_date, budget, created_at)
        - order (str): Sort order (asc, desc)
    """
    user_id = get_current_user_id()
    user = get_current_user()
    
    try:
        # Parse query parameters
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(100, max(1, int(request.args.get('per_page', 10))))
        
        # Build base query
        query = Trip.query.filter_by(user_id=user_id)
        
        # Apply filters
        filters = []
        
        # Destination filter
        destination = request.args.get('destination', '').strip()
        if destination:
            filters.append(Trip.destination.ilike(f'%{destination}%'))
        
        # Status filter
        status = request.args.get('status', '').strip().lower()
        if status in ['planned', 'ongoing', 'completed', 'cancelled']:
            filters.append(Trip.status == status)
        
        # Date range filters
        start_date_from = request.args.get('start_date_from')
        if start_date_from:
            try:
                date_from = datetime.strptime(start_date_from, '%Y-%m-%d').date()
                filters.append(Trip.start_date >= date_from)
            except ValueError:
                return jsonify({
                    'error': 'Validation error',
                    'message': 'Invalid start_date_from format. Use YYYY-MM-DD'
                }), 400
        
        start_date_to = request.args.get('start_date_to')
        if start_date_to:
            try:
                date_to = datetime.strptime(start_date_to, '%Y-%m-%d').date()
                filters.append(Trip.start_date <= date_to)
            except ValueError:
                return jsonify({
                    'error': 'Validation error',
                    'message': 'Invalid start_date_to format. Use YYYY-MM-DD'
                }), 400
        
        # Budget filters
        budget_min = request.args.get('budget_min')
        if budget_min:
            try:
                min_budget = float(budget_min)
                filters.append(Trip.budget >= min_budget)
            except ValueError:
                return jsonify({
                    'error': 'Validation error',
                    'message': 'Invalid budget_min value'
                }), 400
        
        budget_max = request.args.get('budget_max')
        if budget_max:
            try:
                max_budget = float(budget_max)
                filters.append(Trip.budget <= max_budget)
            except ValueError:
                return jsonify({
                    'error': 'Validation error',
                    'message': 'Invalid budget_max value'
                }), 400
        
        # Apply all filters
        if filters:
            query = query.filter(and_(*filters))
        
        # Sorting
        sort_field = request.args.get('sort', 'created_at').strip().lower()
        sort_order = request.args.get('order', 'desc').strip().lower()
        
        valid_sort_fields = ['destination', 'start_date', 'end_date', 'budget', 'created_at', 'updated_at']
        if sort_field not in valid_sort_fields:
            sort_field = 'created_at'
        
        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'
        
        # Apply sorting
        sort_column = getattr(Trip, sort_field)
        if sort_order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Paginate results
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        trips = pagination.items
        
        # Build response
        return jsonify({
            'message': 'Trips retrieved successfully',
            'user_id': user_id,
            'trips': [trip.to_dict() for trip in trips],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters_applied': {
                'destination': destination or None,
                'status': status or None,
                'start_date_from': start_date_from,
                'start_date_to': start_date_to,
                'budget_min': budget_min,
                'budget_max': budget_max
            },
            'sorting': {
                'field': sort_field,
                'order': sort_order
            }
        })
        
    except Exception as e:
        logging.error(f"Error listing trips for user {user_id}: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to retrieve trips'
        }), 500

@trips_bp.route('', methods=['POST'])
@require_auth
def create_trip():
    """
    Create a new trip for the authenticated user.
    
    Required fields:
        - destination (str): Trip destination
        - start_date (str): Start date in YYYY-MM-DD format
        - end_date (str): End date in YYYY-MM-DD format
    
    Optional fields:
        - description (str): Trip description
        - budget (float): Trip budget
        - latitude (float): Destination latitude
        - longitude (float): Destination longitude
        - itinerary (list): List of itinerary items
        - status (str): Trip status (default: 'planned')
    """
    user_id = get_current_user_id()
    data = request.get_json()
    
    # Validate input data
    is_valid, error_message = validate_trip_data(data)
    if not is_valid:
        return jsonify({
            'error': 'Validation error',
            'message': error_message
        }), 400
    
    try:
        # Parse dates
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        # Create trip
        trip = Trip(
            user_id=user_id,
            destination=data['destination'],
            start_date=start_date,
            end_date=end_date,
            description=data.get('description'),
            budget=data.get('budget'),
            status=data.get('status', 'planned')
        )
        
        # Set coordinates if provided
        if 'latitude' in data and 'longitude' in data:
            trip.set_coordinates(float(data['latitude']), float(data['longitude']))
        
        # Set itinerary if provided
        if 'itinerary' in data and data['itinerary']:
            trip.set_itinerary(data['itinerary'])
        
        db.session.add(trip)
        db.session.commit()
        
        return jsonify({
            'message': 'Trip created successfully',
            'trip': trip.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating trip for user {user_id}: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to create trip'
        }), 500

@trips_bp.route('/<int:trip_id>', methods=['GET'])
@require_auth
def get_trip(trip_id):
    """
    Get a specific trip by ID.
    Only the trip owner can access their trip.
    """
    user_id = get_current_user_id()
    
    try:
        trip = check_trip_ownership(trip_id, user_id)
        if not trip:
            return jsonify({
                'error': 'Trip not found',
                'message': f'Trip with ID {trip_id} not found or you do not have permission to access it'
            }), 404
        
        return jsonify({
            'message': 'Trip retrieved successfully',
            'trip': trip.to_dict()
        })
        
    except Exception as e:
        logging.error(f"Error retrieving trip {trip_id} for user {user_id}: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to retrieve trip'
        }), 500

@trips_bp.route('/<int:trip_id>', methods=['PUT'])
@require_auth
def update_trip(trip_id):
    """
    Update a trip completely (replace all fields).
    Only the trip owner can update their trip.
    
    All fields from POST /trips are supported.
    """
    user_id = get_current_user_id()
    data = request.get_json()
    
    # Validate input data (for complete update, require essential fields)
    is_valid, error_message = validate_trip_data(data, is_update=False)
    if not is_valid:
        return jsonify({
            'error': 'Validation error',
            'message': error_message
        }), 400
    
    try:
        trip = check_trip_ownership(trip_id, user_id)
        if not trip:
            return jsonify({
                'error': 'Trip not found',
                'message': f'Trip with ID {trip_id} not found or you do not have permission to update it'
            }), 404
        
        # Parse dates
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        # Update all fields
        trip.destination = data['destination']
        trip.start_date = start_date
        trip.end_date = end_date
        trip.description = data.get('description')
        trip.budget = data.get('budget')
        trip.status = data.get('status', 'planned')
        
        # Update coordinates
        if 'latitude' in data and 'longitude' in data:
            trip.set_coordinates(float(data['latitude']), float(data['longitude']))
        else:
            # Clear coordinates if not provided
            trip.latitude = None
            trip.longitude = None
        
        # Update itinerary
        if 'itinerary' in data:
            trip.set_itinerary(data['itinerary'])
        else:
            # Clear itinerary if not provided
            trip.itinerary_json = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Trip updated successfully',
            'trip': trip.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating trip {trip_id} for user {user_id}: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to update trip'
        }), 500

@trips_bp.route('/<int:trip_id>', methods=['PATCH'])
@require_auth
def patch_trip(trip_id):
    """
    Partially update a trip (update only provided fields).
    Only the trip owner can update their trip.
    """
    user_id = get_current_user_id()
    data = request.get_json()
    
    # Validate input data (for partial update, no required fields)
    is_valid, error_message = validate_trip_data(data, is_update=True)
    if not is_valid:
        return jsonify({
            'error': 'Validation error',
            'message': error_message
        }), 400
    
    try:
        trip = check_trip_ownership(trip_id, user_id)
        if not trip:
            return jsonify({
                'error': 'Trip not found',
                'message': f'Trip with ID {trip_id} not found or you do not have permission to update it'
            }), 404
        
        # Update provided fields only
        if 'destination' in data:
            trip.destination = data['destination']
        
        if 'start_date' in data:
            trip.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        
        if 'end_date' in data:
            trip.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        if 'description' in data:
            trip.description = data['description']
        
        if 'budget' in data:
            trip.budget = data['budget']
        
        if 'status' in data:
            trip.status = data['status']
        
        # Update coordinates if both provided
        if 'latitude' in data and 'longitude' in data:
            trip.set_coordinates(float(data['latitude']), float(data['longitude']))
        
        # Update itinerary if provided
        if 'itinerary' in data:
            trip.set_itinerary(data['itinerary'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Trip updated successfully',
            'trip': trip.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error patching trip {trip_id} for user {user_id}: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to update trip'
        }), 500

@trips_bp.route('/<int:trip_id>', methods=['DELETE'])
@require_auth
def delete_trip(trip_id):
    """
    Delete a specific trip by ID.
    Only the trip owner can delete their trip.
    """
    user_id = get_current_user_id()
    
    try:
        trip = check_trip_ownership(trip_id, user_id)
        if not trip:
            return jsonify({
                'error': 'Trip not found',
                'message': f'Trip with ID {trip_id} not found or you do not have permission to delete it'
            }), 404
        
        # Store trip data for response
        deleted_trip_data = trip.to_dict()
        
        db.session.delete(trip)
        db.session.commit()
        
        return jsonify({
            'message': 'Trip deleted successfully',
            'deleted_trip': deleted_trip_data
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting trip {trip_id} for user {user_id}: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to delete trip'
        }), 500

@trips_bp.route('/stats', methods=['GET'])
@require_auth
def get_trip_stats():
    """
    Get trip statistics for the authenticated user.
    
    Returns:
        - Total trip count
        - Trips by status
        - Total budget across all trips
        - Average trip duration
        - Upcoming trips count
        - Past trips count
    """
    user_id = get_current_user_id()
    
    try:
        from sqlalchemy import func
        from datetime import date
        
        today = date.today()
        
        # Basic counts
        total_trips = Trip.query.filter_by(user_id=user_id).count()
        
        # Status breakdown
        status_stats = db.session.query(
            Trip.status,
            func.count(Trip.id).label('count')
        ).filter_by(user_id=user_id).group_by(Trip.status).all()
        
        status_counts = {status: count for status, count in status_stats}
        
        # Budget statistics
        budget_stats = db.session.query(
            func.sum(Trip.budget).label('total_budget'),
            func.avg(Trip.budget).label('avg_budget'),
            func.min(Trip.budget).label('min_budget'),
            func.max(Trip.budget).label('max_budget')
        ).filter(
            Trip.user_id == user_id,
            Trip.budget.isnot(None)
        ).first()
        
        # Duration statistics
        duration_stats = db.session.query(
            func.avg(func.julianday(Trip.end_date) - func.julianday(Trip.start_date)).label('avg_duration')
        ).filter_by(user_id=user_id).first()
        
        # Upcoming vs past trips
        upcoming_trips = Trip.query.filter(
            Trip.user_id == user_id,
            Trip.start_date > today
        ).count()
        
        past_trips = Trip.query.filter(
            Trip.user_id == user_id,
            Trip.end_date < today
        ).count()
        
        current_trips = Trip.query.filter(
            Trip.user_id == user_id,
            Trip.start_date <= today,
            Trip.end_date >= today
        ).count()
        
        return jsonify({
            'message': 'Trip statistics retrieved successfully',
            'user_id': user_id,
            'statistics': {
                'total_trips': total_trips,
                'status_breakdown': status_counts,
                'budget_statistics': {
                    'total_budget': float(budget_stats.total_budget) if budget_stats.total_budget else 0,
                    'average_budget': float(budget_stats.avg_budget) if budget_stats.avg_budget else 0,
                    'min_budget': float(budget_stats.min_budget) if budget_stats.min_budget else 0,
                    'max_budget': float(budget_stats.max_budget) if budget_stats.max_budget else 0
                },
                'duration_statistics': {
                    'average_duration_days': round(float(duration_stats.avg_duration), 1) if duration_stats.avg_duration else 0
                },
                'timeline_breakdown': {
                    'upcoming_trips': upcoming_trips,
                    'current_trips': current_trips,
                    'past_trips': past_trips
                }
            }
        })
        
    except Exception as e:
        logging.error(f"Error retrieving trip stats for user {user_id}: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to retrieve trip statistics'
        }), 500

# Error handlers for the blueprint
@trips_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors."""
    return jsonify({
        'error': 'Bad request',
        'message': 'The request could not be understood or was missing required parameters'
    }), 400

@trips_bp.errorhandler(404)
def not_found(error):
    """Handle not found errors."""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

@trips_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    db.session.rollback()
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500