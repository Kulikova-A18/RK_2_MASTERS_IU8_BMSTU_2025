from flask import request, jsonify
from datetime import datetime, timedelta
import random
import logging
from functools import wraps
from auth import authenticate_user
from db_utils import (
    get_user_by_id, get_staff_by_id, get_status_by_id, get_category_by_id,
    get_tickets_by_staff, get_comments_by_ticket, get_logs_by_ticket, get_departments_from_db
)

logger = logging.getLogger(__name__)

def require_auth(f):
    """
    Decorator to require authentication for API endpoints.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
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
    return decorated_function

def create_endpoints(app, TEST_USERS, TEST_STAFF, TICKET_STATUSES, PROBLEM_CATEGORIES, TEST_TICKETS, TEST_COMMENTS, TEST_LOGS):
    """
    Defines and registers all API endpoints with the Flask app.
    
    @param app: The Flask application instance
    @param TEST_USERS: List of users loaded from the database
    @param TEST_STAFF: List of staff members loaded from the database
    @param TICKET_STATUSES: List of ticket statuses loaded from the database
    @param PROBLEM_CATEGORIES: List of problem categories loaded from the database
    @param TEST_TICKETS: List of tickets loaded from the database
    @param TEST_COMMENTS: List of comments loaded from the database
    @param TEST_LOGS: List of logs loaded from the database
    """

    @app.route('/api/v1/profile', methods=['GET'])
    @require_auth
    def get_profile():
        user = request.user
        staff_tickets = get_tickets_by_staff(user['staff_id'], TEST_TICKETS)
        profile_data = {
            'staff_id': user['staff_id'],
            'name': user['name'],
            'role': user['role'],
            'departments_access': user['departments'],
            'assigned_tickets_count': len(staff_tickets),
            'active_tickets_count': len([t for t in staff_tickets if t['status_id'] in [1, 2, 3]])
        }
        logger.info(f"Profile for user {user['name']} sent successfully")
        return jsonify(profile_data)

    @app.route('/api/v1/departments', methods=['GET'])
    @require_auth
    def get_departments():
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
            dept_staff_ids = [s['staff_id'] for s in TEST_STAFF if s['department'] == dept]
            dept_tickets = [t for t in TEST_TICKETS if t['assigned_staff_id'] in dept_staff_ids]
            active_dept_tickets = [t for t in dept_tickets if t['status_id'] in [1, 2, 3]]
            active_staff_count = len([s for s in TEST_STAFF if s['department'] == dept and s['is_active']])

            departments_data.append({
                'name': dept,
                'ticket_count': len(dept_tickets),
                'active_tickets': len(active_dept_tickets),
                'staff_count': active_staff_count
            })

        logger.info(f"Data for {len(departments_data)} departments sent for user {user['name']}")
        return jsonify(departments_data)

    @app.route('/api/v1/tickets', methods=['GET'])
    @require_auth
    def get_tickets():
        user = request.user
        staff_id = user['staff_id']
        # Get tickets assigned to the staff member
        staff_tickets = get_tickets_by_staff(staff_id, TEST_TICKETS)
        # Enrich data
        enriched_tickets = []
        for ticket in staff_tickets:
            enriched_ticket = ticket.copy()
            status_name = get_status_by_id(ticket['status_id'], TICKET_STATUSES)
            category_name = get_category_by_id(ticket['category_id'], PROBLEM_CATEGORIES)
            user_name = get_user_by_id(ticket['user_id'], TEST_USERS)
            enriched_ticket['status_name'] = status_name['status_name'] if status_name else 'Unknown'
            enriched_ticket['category_name'] = category_name['category_name'] if category_name else 'Unknown'
            enriched_ticket['user_name'] = user_name['full_name'] if user_name else 'Unknown'
            enriched_ticket['comments_count'] = len(get_comments_by_ticket(ticket['ticket_id'], TEST_COMMENTS))
            enriched_tickets.append(enriched_ticket)

        logger.info(f"Sent {len(enriched_tickets)} tickets for user {user['name']}")
        return jsonify(enriched_tickets)

    @app.route('/api/v1/tickets/<int:ticket_id>', methods=['GET'])
    @require_auth
    def get_ticket_detail(ticket_id):
        user = request.user
        ticket = next((t for t in TEST_TICKETS if t['ticket_id'] == ticket_id), None)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        # Check access to the ticket
        if ticket['assigned_staff_id'] != user['staff_id']:
            return jsonify({'error': 'Access to ticket forbidden'}), 403
        # Enrich ticket data
        enriched_ticket = ticket.copy()
        status_info = get_status_by_id(ticket['status_id'], TICKET_STATUSES)
        category_info = get_category_by_id(ticket['category_id'], PROBLEM_CATEGORIES)
        user_info = get_user_by_id(ticket['user_id'], TEST_USERS)
        staff_info = get_staff_by_id(ticket['assigned_staff_id'], TEST_STAFF)

        enriched_ticket['status_name'] = status_info['status_name'] if status_info else 'Unknown'
        enriched_ticket['category_name'] = category_info['category_name'] if category_info else 'Unknown'
        enriched_ticket['user_name'] = user_info['full_name'] if user_info else 'Unknown'
        enriched_ticket['assigned_staff_name'] = staff_info['full_name'] if staff_info else 'Unknown'

        # Add comments
        enriched_ticket['comments'] = get_comments_by_ticket(ticket_id, TEST_COMMENTS)
        for comment in enriched_ticket['comments']:
            if comment['author_type'] == 'user':
                author_info = get_user_by_id(comment['author_id'], TEST_USERS)
                comment['author_name'] = author_info['full_name'] if author_info else 'Unknown'
            else:
                author_info = get_staff_by_id(comment['author_id'], TEST_STAFF)
                comment['author_name'] = author_info['full_name'] if author_info else 'Unknown'

        # Add logs
        enriched_ticket['logs'] = get_logs_by_ticket(ticket_id, TEST_LOGS)

        logger.info(f"Detail information for ticket {ticket_id} sent to user {user['name']}")
        return jsonify(enriched_ticket)

    @app.route('/api/v1/staff', methods=['GET'])
    @require_auth
    def get_staff():
        user = request.user
        # Get only active staff from departments the user has access to
        accessible_departments = user['departments']
        active_staff = [s for s in TEST_STAFF if s['is_active'] and any(dept in accessible_departments for dept in [s.get('department', '')])]
        # Add ticket statistics for each staff member
        for staff in active_staff:
            staff_tickets = get_tickets_by_staff(staff['staff_id'], TEST_TICKETS)
            staff['assigned_tickets'] = len(staff_tickets)
            staff['active_tickets'] = len([t for t in staff_tickets if t['status_id'] in [1, 2, 3]])
            staff['resolved_tickets'] = len([t for t in staff_tickets if t['status_id'] in [4, 5]])

        logger.info(f"Data for {len(active_staff)} staff members sent for user {user['name']}")
        return jsonify(active_staff)

    @app.route('/api/v1/metrics', methods=['GET'])
    @require_auth
    def get_metrics():
        user = request.user
        staff_id = user['staff_id']
        staff_tickets = get_tickets_by_staff(staff_id, TEST_TICKETS)
        all_tickets = TEST_TICKETS
        # Calculate metrics
        total_tickets = len(staff_tickets)
        resolved_tickets = len([t for t in staff_tickets if t['status_id'] in [4, 5]])
        active_tickets = len([t for t in staff_tickets if t['status_id'] in [1, 2, 3]])
        # Calculate average resolution time
        resolved_times = []
        for ticket in staff_tickets:
            if ticket['closed_at']:
                resolution_time = (ticket['closed_at'] - ticket['created_at']).total_seconds() / 3600  # in hours
                resolved_times.append(resolution_time)
        avg_resolution_time = sum(resolved_times) / len(resolved_times) if resolved_times else 0

        # Department category statistics
        dept_staff_ids = [s['staff_id'] for s in TEST_STAFF if s['department'] in user['departments']]
        dept_tickets = [t for t in TEST_TICKETS if t['assigned_staff_id'] in dept_staff_ids]
        category_counts = {}
        for ticket in dept_tickets:
            cat_id = ticket['category_id']
            category_counts[cat_id] = category_counts.get(cat_id, 0) + 1
        most_common_category_id = max(category_counts, key=category_counts.get, default=None)
        most_common_category_name = get_category_by_id(most_common_category_id, PROBLEM_CATEGORIES)['category_name'] if most_common_category_id else 'No data'

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
                'resolved_tickets': len([t for t in dept_tickets if t['status_id'] in [4, 5]]),
                'avg_first_response_time': '2.1 hours', # Placeholder
                'most_common_category': most_common_category_name
            }
        }
        logger.info(f"Metrics sent for user {user['name']}")
        return jsonify(metrics)

    @app.route('/api/v1/timeline', methods=['GET'])
    @require_auth
    def get_timeline():
        user = request.user
        days = request.args.get('days', 30, type=int)
        if days > 365:
            days = 365
        if days < 1:
            days = 1
        staff_tickets = get_tickets_by_staff(user['staff_id'], TEST_TICKETS)
        base_date = datetime.now()
        timeline_data = []
        for i in range(days):
            date = base_date - timedelta(days=days - i - 1)
            date_str = date.strftime('%Y-%m-%d')
            day_tickets = [t for t in staff_tickets if t['created_at'].date() == date.date()]
            day_resolved = [t for t in staff_tickets if t['closed_at'] and t['closed_at'].date() == date.date()]
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

    @app.route('/api/v1/comparison', methods=['GET'])
    @require_auth
    def get_comparison():
        user = request.user
        staff_tickets = get_tickets_by_staff(user['staff_id'], TEST_TICKETS)
        # Compare with the user's department
        dept_staff_ids = [s['staff_id'] for s in TEST_STAFF if s['department'] in user['departments']]
        dept_tickets = [t for t in TEST_TICKETS if t['assigned_staff_id'] in dept_staff_ids]

        user_resolution_rate = len([t for t in staff_tickets if t['status_id'] in [4, 5]]) / len(
            staff_tickets) * 100 if staff_tickets else 0
        avg_resolution_rate = len([t for t in dept_tickets if t['status_id'] in [4, 5]]) / len(
            dept_tickets) * 100 if dept_tickets else 0

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

    @app.route('/api/v1/forecast', methods=['GET'])
    @require_auth
    def get_forecast():
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

    @app.route('/api/v1/categories', methods=['GET'])
    @require_auth
    def get_categories():
        user = request.user
        # Category statistics for the current staff member
        staff_tickets = get_tickets_by_staff(user['staff_id'], TEST_TICKETS)
        category_stats = []
        for category in PROBLEM_CATEGORIES:
            category_tickets = [t for t in staff_tickets if t['category_id'] == category['category_id']]
            category_stats.append({
                'category_id': category['category_id'],
                'category_name': category['category_name'],
                'ticket_count': len(category_tickets),
                'resolution_rate': f"{(len([t for t in category_tickets if t['status_id'] in [4, 5]]) / len(category_tickets) * 100) if category_tickets else 0:.1f}%"
            })

        return jsonify(category_stats)

    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        logger.debug("Health check request")
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'data_counts': {
                'users': len(TEST_USERS),
                'staff': len(TEST_STAFF),
                'tickets': len(TEST_TICKETS),
                'comments': len(TEST_COMMENTS),
                'logs': len(TEST_LOGS)
            }
        })

    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"Requested non-existent endpoint: {request.path}")
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal server error: {error}')
        return jsonify({'error': 'Internal server error'}), 500