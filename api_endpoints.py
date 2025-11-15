from flask import request, jsonify
from datetime import datetime, timedelta
import random
import logging
from functools import wraps
from auth import authenticate_user
from db_utils import (
    get_user_by_id,
    get_staff_by_id,
    get_status_by_id,
    get_category_by_id,
    get_tickets_by_staff,
    get_comments_by_ticket,
    get_logs_by_ticket,
    get_departments_from_db
)

logger = logging.getLogger(__name__)

def require_auth(f):
    """
    Decorator to require authentication for API endpoints.
    
    @param f: The Flask route function to be decorated
    @return: Decorated function with authentication logic
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            client_ip = request.remote_addr
            user_agent = request.headers.get('User-Agent', 'Unknown')
            logger.info(f"Request {request.path} from {client_ip} - {user_agent}")
            
            if request.method != 'GET':
                logger.warning(f"Attempted non-GET request from {client_ip}")
                return jsonify({'error': 'Only GET requests are allowed'}), 405
            
            login = request.args.get('login')
            code = request.args.get('code')
            
            if not login or not code:
                logger.warning(f"Missing credentials from {client_ip}")
                return jsonify({'error': 'Login and code parameters required'}), 401
            
            if len(login) > 50 or len(code) > 100:
                logger.warning(f"Parameters too long from {client_ip}")
                return jsonify({'error': 'Invalid authentication parameters'}), 400
            
            auth_success, user = authenticate_user(login, code)
            if not auth_success:
                logger.warning(f"Failed authentication for user {login} from {client_ip}")
                return jsonify({'error': 'Invalid credentials'}), 401
            
            request.user = user
            logger.debug(f"User {login} authenticated for access to {request.path}")
            return f(*args, **kwargs)
        
        except Exception as e:
            logger.error(f"Error in authentication decorator: {e}")
            return jsonify({'error': 'Internal server error during authentication'}), 500
    
    return decorated_function

def create_endpoints(app, TEST_USERS, TEST_STAFF, TICKET_STATUSES, PROBLEM_CATEGORIES, TEST_TICKETS, TEST_COMMENTS, TEST_LOGS):
    """
    Defines and registers all API endpoints with the Flask app.
    
    @param app: The Flask application instance to register endpoints with
    @param TEST_USERS: List of users loaded from the database
    @param TEST_STAFF: List of staff members loaded from the database
    @param TICKET_STATUSES: List of ticket statuses loaded from the database
    @param PROBLEM_CATEGORIES: List of problem categories loaded from the database
    @param TEST_TICKETS: List of tickets loaded from the database
    @param TEST_COMMENTS: List of comments loaded from the database
    @param TEST_LOGS: List of logs loaded from the database
    @return: None (registers endpoints directly to the app)
    """
    
    @app.route('/api/v1/profile', methods=['GET'])
    @require_auth
    def get_profile():
        """
        API endpoint to retrieve the authenticated user's profile information.
        
        @return: JSON response containing user profile data
        """
        try:
            user = request.user
            staff_tickets = get_tickets_by_staff(user['staff_id'], TEST_TICKETS) if TEST_TICKETS else []
            profile_data = {
                'staff_id': user['staff_id'],
                'name': user['name'],
                'role': user['role'],
                'departments_access': user['departments'],
                'assigned_tickets_count': len(staff_tickets),
                'active_tickets_count': len([t for t in staff_tickets if t.get('status_id') in [1, 2, 3]])
            }
            logger.info(f"Profile for user {user['name']} sent successfully")
            return jsonify(profile_data)
        except Exception as e:
            logger.error(f"Error retrieving profile: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/v1/departments', methods=['GET'])
    @require_auth
    def get_departments():
        """
        API endpoint to retrieve department data accessible to the authenticated user.
        
        @return: JSON response containing department statistics
        """
        try:
            user = request.user
            all_departments = get_departments_from_db()
            if not all_departments:
                logger.error("Could not fetch departments from DB")
                return jsonify({'error': 'Error fetching data from database'}), 500
            
            # Filter departments the user has access to
            accessible_departments = [dept for dept in all_departments if dept in user['departments']]
            departments_data = []
            for dept in accessible_departments:
                # Count tickets associated with staff from this department
                dept_staff_ids = [s['staff_id'] for s in TEST_STAFF if s.get('department') == dept]
                dept_tickets = [t for t in TEST_TICKETS if t.get('assigned_staff_id') in dept_staff_ids]
                active_dept_tickets = [t for t in dept_tickets if t.get('status_id') in [1, 2, 3]]
                active_staff_count = len([s for s in TEST_STAFF if s.get('department') == dept and s.get('is_active')])
                departments_data.append({
                    'name': dept,
                    'ticket_count': len(dept_tickets),
                    'active_tickets': len(active_dept_tickets),
                    'staff_count': active_staff_count
                })
            logger.info(f"Data for {len(departments_data)} departments sent for user {user['name']}")
            return jsonify(departments_data)
        except Exception as e:
            logger.error(f"Error retrieving departments: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/v1/tickets', methods=['GET'])
    @require_auth
    def get_tickets():
        """
        API endpoint to retrieve tickets assigned to the authenticated user.
        
        @return: JSON response containing enriched ticket data
        """
        try:
            user = request.user
            staff_id = user['staff_id']
            # Get tickets assigned to the staff member
            staff_tickets = get_tickets_by_staff(staff_id, TEST_TICKETS) if TEST_TICKETS else []
            # Enrich data
            enriched_tickets = []
            for ticket in staff_tickets:
                enriched_ticket = ticket.copy()
                status_name = get_status_by_id(ticket['status_id'], TICKET_STATUSES) if TICKET_STATUSES else None
                category_name = get_category_by_id(ticket['category_id'], PROBLEM_CATEGORIES) if PROBLEM_CATEGORIES else None
                user_name = get_user_by_id(ticket['user_id'], TEST_USERS) if TEST_USERS else None
                enriched_ticket['status_name'] = status_name['status_name'] if status_name else 'Unknown'
                enriched_ticket['category_name'] = category_name['category_name'] if category_name else 'Unknown'
                enriched_ticket['user_name'] = user_name['full_name'] if user_name else 'Unknown'
                enriched_ticket['comments_count'] = len(get_comments_by_ticket(ticket['ticket_id'], TEST_COMMENTS)) if TEST_COMMENTS else 0
                enriched_tickets.append(enriched_ticket)
            logger.info(f"Sent {len(enriched_tickets)} tickets for user {user['name']}")
            return jsonify(enriched_tickets)
        except Exception as e:
            logger.error(f"Error retrieving tickets: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/v1/tickets/<int:ticket_id>', methods=['GET'])
    @require_auth
    def get_ticket_detail(ticket_id):
        """
        API endpoint to retrieve detailed information for a specific ticket.
        
        @param ticket_id: Integer ID of the ticket to retrieve
        @return: JSON response containing detailed ticket information
        """
        try:
            user = request.user
            ticket = next((t for t in TEST_TICKETS if t.get('ticket_id') == ticket_id), None)
            if not ticket:
                return jsonify({'error': 'Ticket not found'}), 404
            
            # Check access to the ticket
            if ticket.get('assigned_staff_id') != user['staff_id']:
                return jsonify({'error': 'Access to ticket forbidden'}), 403
            
            # Enrich ticket data
            enriched_ticket = ticket.copy()
            status_info = get_status_by_id(ticket['status_id'], TICKET_STATUSES) if TICKET_STATUSES else None
            category_info = get_category_by_id(ticket['category_id'], PROBLEM_CATEGORIES) if PROBLEM_CATEGORIES else None
            user_info = get_user_by_id(ticket['user_id'], TEST_USERS) if TEST_USERS else None
            staff_info = get_staff_by_id(ticket['assigned_staff_id'], TEST_STAFF) if TEST_STAFF else None
            enriched_ticket['status_name'] = status_info['status_name'] if status_info else 'Unknown'
            enriched_ticket['category_name'] = category_info['category_name'] if category_info else 'Unknown'
            enriched_ticket['user_name'] = user_info['full_name'] if user_info else 'Unknown'
            enriched_ticket['assigned_staff_name'] = staff_info['full_name'] if staff_info else 'Unknown'
            
            # Add comments
            enriched_ticket['comments'] = get_comments_by_ticket(ticket_id, TEST_COMMENTS) if TEST_COMMENTS else []
            for comment in enriched_ticket['comments']:
                if comment.get('author_type') == 'user':
                    author_info = get_user_by_id(comment['author_id'], TEST_USERS) if TEST_USERS else None
                    comment['author_name'] = author_info['full_name'] if author_info else 'Unknown'
                else:
                    author_info = get_staff_by_id(comment['author_id'], TEST_STAFF) if TEST_STAFF else None
                    comment['author_name'] = author_info['full_name'] if author_info else 'Unknown'
            
            # Add logs
            enriched_ticket['logs'] = get_logs_by_ticket(ticket_id, TEST_LOGS) if TEST_LOGS else []
            logger.info(f"Detail information for ticket {ticket_id} sent to user {user['name']}")
            return jsonify(enriched_ticket)
        except Exception as e:
            logger.error(f"Error retrieving ticket detail: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/v1/staff', methods=['GET'])
    @require_auth
    def get_staff():
        """
        API endpoint to retrieve staff members accessible to the authenticated user.
        
        @return: JSON response containing staff member data with statistics
        """
        try:
            user = request.user
            # Get only active staff from departments the user has access to
            accessible_departments = user['departments']
            active_staff = [s for s in TEST_STAFF if s.get('is_active') and any(dept in accessible_departments for dept in [s.get('department', '')])]
            # Add ticket statistics for each staff member
            for staff_member in active_staff:
                staff_tickets = get_tickets_by_staff(staff_member['staff_id'], TEST_TICKETS) if TEST_TICKETS else []
                staff_member['assigned_tickets'] = len(staff_tickets)
                staff_member['active_tickets'] = len([t for t in staff_tickets if t.get('status_id') in [1, 2, 3]])
                staff_member['resolved_tickets'] = len([t for t in staff_tickets if t.get('status_id') in [4, 5]])
            logger.info(f"Data for {len(active_staff)} staff members sent for user {user['name']}")
            return jsonify(active_staff)
        except Exception as e:
            logger.error(f"Error retrieving staff data: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/v1/metrics', methods=['GET'])
    @require_auth
    def get_metrics():
        """
        API endpoint to retrieve performance metrics for the authenticated user.
        
        @return: JSON response containing personal and department metrics
        """
        try:
            user = request.user
            staff_id = user['staff_id']
            staff_tickets = get_tickets_by_staff(staff_id, TEST_TICKETS) if TEST_TICKETS else []
            all_tickets = TEST_TICKETS or []
            
            # Calculate metrics
            total_tickets = len(staff_tickets)
            resolved_tickets = len([t for t in staff_tickets if t.get('status_id') in [4, 5]])
            active_tickets = len([t for t in staff_tickets if t.get('status_id') in [1, 2, 3]])
            
            # Calculate average resolution time
            resolved_times = []
            for ticket in staff_tickets:
                if ticket.get('closed_at') and ticket.get('created_at'):
                    try:
                        resolution_time = (ticket['closed_at'] - ticket['created_at']).total_seconds() / 3600 # in hours
                        resolved_times.append(resolution_time)
                    except TypeError:
                        continue  # Skip if datetime calculation fails
            
            avg_resolution_time = sum(resolved_times) / len(resolved_times) if resolved_times else 0
            
            # Department category statistics
            dept_staff_ids = [s['staff_id'] for s in TEST_STAFF if s.get('department') in user['departments']]
            dept_tickets = [t for t in all_tickets if t.get('assigned_staff_id') in dept_staff_ids]
            category_counts = {}
            for ticket in dept_tickets:
                cat_id = ticket.get('category_id')
                if cat_id is not None:
                    category_counts[cat_id] = category_counts.get(cat_id, 0) + 1
            
            most_common_category_id = max(category_counts, key=category_counts.get, default=None)
            most_common_category_name = 'No data'
            if most_common_category_id is not None:
                category_info = get_category_by_id(most_common_category_id, PROBLEM_CATEGORIES) if PROBLEM_CATEGORIES else None
                if category_info:
                    most_common_category_name = category_info.get('category_name', 'No data')
            
            metrics = {
                'personal_metrics': {
                    'total_tickets': total_tickets,
                    'resolved_tickets': resolved_tickets,
                    'active_tickets': active_tickets,
                    'resolution_rate': f"{(resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0:.1f}%",
                    'avg_resolution_time': f"{avg_resolution_time:.1f} hours",
                    'satisfaction_rate': f"{random.randint(85, 98)}%"
                },
                'department_metrics': {
                    'total_tickets': len(dept_tickets),
                    'resolved_tickets': len([t for t in dept_tickets if t.get('status_id') in [4, 5]]),
                    'avg_first_response_time': '2.1 hours', # Placeholder
                    'most_common_category': most_common_category_name
                }
            }
            logger.info(f"Metrics sent for user {user['name']}")
            return jsonify(metrics)
        except Exception as e:
            logger.error(f"Error retrieving metrics: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/v1/timeline', methods=['GET'])
    @require_auth
    def get_timeline():
        """
        API endpoint to retrieve ticket timeline data for the authenticated user.
        
        @return: JSON response containing timeline data for the specified period
        """
        try:
            user = request.user
            days = request.args.get('days', 30, type=int)
            if days > 365:
                days = 365
            if days < 1:
                days = 1
            
            staff_tickets = get_tickets_by_staff(user['staff_id'], TEST_TICKETS) if TEST_TICKETS else []
            base_date = datetime.now()
            timeline_data = []
            for i in range(days):
                date = base_date - timedelta(days=days - i - 1)
                date_str = date.strftime('%Y-%m-%d')
                day_tickets = [t for t in staff_tickets if t.get('created_at') and t['created_at'].date() == date.date()]
                day_resolved = [t for t in staff_tickets if t.get('closed_at') and t['closed_at'].date() == date.date()]
                timeline_data.append({
                    'date': date_str,
                    'tickets_created': len(day_tickets),
                    'tickets_resolved': len(day_resolved),
                    'satisfaction_rate': random.randint(85, 98)
                })
            logger.info(f"Timeline data for {days} days sent for user {user['name']}")
            return jsonify({
                'period_days': days,
                'data': timeline_data
            })
        except Exception as e:
            logger.error(f"Error retrieving timeline: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/v1/comparison', methods=['GET'])
    @require_auth
    def get_comparison():
        """
        API endpoint to retrieve performance comparison data for the authenticated user.
        
        @return: JSON response containing comparison with department averages and top performers
        """
        try:
            user = request.user
            staff_tickets = get_tickets_by_staff(user['staff_id'], TEST_TICKETS) if TEST_TICKETS else []
            # Compare with the user's department
            dept_staff_ids = [s['staff_id'] for s in TEST_STAFF if s.get('department') in user['departments']]
            dept_tickets = [t for t in (TEST_TICKETS or []) if t.get('assigned_staff_id') in dept_staff_ids]
            user_resolution_rate = len([t for t in staff_tickets if t.get('status_id') in [4, 5]]) / len(staff_tickets) * 100 if staff_tickets else 0
            avg_resolution_rate = len([t for t in dept_tickets if t.get('status_id') in [4, 5]]) / len(dept_tickets) * 100 if dept_tickets else 0
            return jsonify({
                'your_performance': {
                    'resolution_rate': f"{user_resolution_rate:.1f}%",
                    'avg_response_time': '1.8 hours', # Placeholder
                    'satisfaction_rate': f"{random.randint(88, 98)}%"
                },
                'department_average': {
                    'resolution_rate': f"{avg_resolution_rate:.1f}%",
                    'avg_response_time': '2.5 hours', # Placeholder
                    'satisfaction_rate': '89%' # Placeholder
                },
                'top_performer': {
                    'staff_name': 'Ivan Petrov', # Placeholder
                    'resolution_rate': '95.2%', # Placeholder
                    'avg_response_time': '1.2 hours' # Placeholder
                }
            })
        except Exception as e:
            logger.error(f"Error retrieving comparison: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/v1/forecast', methods=['GET'])
    @require_auth
    def get_forecast():
        """
        API endpoint to retrieve forecast and trend analysis for the authenticated user.
        
        @return: JSON response containing forecast data and trend analysis
        """
        try:
            user = request.user
            return jsonify({
                'next_week_forecast': {
                    'expected_tickets': random.randint(15, 25), # Placeholder
                    'expected_resolution_rate': f"{random.randint(75, 90)}%", # Placeholder
                    'busiest_day': random.choice(['Monday', 'Tuesday']) # Placeholder
                },
                'trend_analysis': {
                    'ticket_growth': f"+{random.randint(5, 15)}%", # Placeholder
                    'resolution_trend': 'improvement', # Placeholder
                    'risk_factors': ['Seasonal load', 'System updates'] # Placeholder
                }
            })
        except Exception as e:
            logger.error(f"Error retrieving forecast: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/v1/categories', methods=['GET'])
    @require_auth
    def get_categories():
        """
        API endpoint to retrieve category statistics for the authenticated user.
        
        @return: JSON response containing category-wise ticket statistics
        """
        try:
            user = request.user
            # Category statistics for the current staff member
            staff_tickets = get_tickets_by_staff(user['staff_id'], TEST_TICKETS) if TEST_TICKETS else []
            category_stats = []
            for category in (PROBLEM_CATEGORIES or []):
                category_tickets = [t for t in staff_tickets if t.get('category_id') == category.get('category_id')]
                category_stats.append({
                    'category_id': category['category_id'],
                    'category_name': category['category_name'],
                    'ticket_count': len(category_tickets),
                    'resolution_rate': f"{(len([t for t in category_tickets if t.get('status_id') in [4, 5]]) / len(category_tickets) * 100) if category_tickets else 0:.1f}%"
                })
            return jsonify(category_stats)
        except Exception as e:
            logger.error(f"Error retrieving categories: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        """
        API endpoint to check the health status of the application.
        
        @return: JSON response containing health status and data counts
        """
        try:
            logger.debug("Health check request")
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'data_counts': {
                    'users': len(TEST_USERS) if TEST_USERS else 0,
                    'staff': len(TEST_STAFF) if TEST_STAFF else 0,
                    'tickets': len(TEST_TICKETS) if TEST_TICKETS else 0,
                    'comments': len(TEST_COMMENTS) if TEST_COMMENTS else 0,
                    'logs': len(TEST_LOGS) if TEST_LOGS else 0
                }
            })
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return jsonify({'error': 'Health check failed'}), 500

    @app.errorhandler(404)
    def not_found(error):
        """
        Error handler for 404 Not Found errors.
        
        @param error: The error object
        @return: JSON response indicating the error
        """
        logger.warning(f"Requested non-existent endpoint: {request.path}")
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """
        Error handler for 500 Internal Server Error.
        
        @param error: The error object
        @return: JSON response indicating the error
        """
        logger.error(f'Internal server error: {error}')
        return jsonify({'error': 'Internal server error'}), 500