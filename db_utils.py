import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from constants import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Establishes and returns a connection to the PostgreSQL database.
    
    @return: psycopg2 connection object or None if connection fails
    """
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        logger.debug("Successfully connected to the database.")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        return None

def get_users_from_db():
    """
    Fetches all users from the database.
    
    @return: List of user dictionaries
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT user_id, email, full_name, registration_date FROM Users;")
        users = [dict(row) for row in cur.fetchall()]
        cur.close()
        return users
    except psycopg2.Error as e:
        logger.error(f"Error fetching users from DB: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_staff_from_db():
    """
    Fetches all staff members from the database.
    
    @return: List of staff dictionaries
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT staff_id, username, full_name, email, department, is_active FROM Staff;")
        staff = [dict(row) for row in cur.fetchall()]
        cur.close()
        return staff
    except psycopg2.Error as e:
        logger.error(f"Error fetching staff from DB: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_ticket_statuses_from_db():
    """
    Fetches all ticket statuses from the database.
    
    @return: List of status dictionaries
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT status_id, status_name FROM TicketStatuses;")
        statuses = [dict(row) for row in cur.fetchall()]
        cur.close()
        return statuses
    except psycopg2.Error as e:
        logger.error(f"Error fetching ticket statuses from DB: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_problem_categories_from_db():
    """
    Fetches all problem categories from the database.
    
    @return: List of category dictionaries
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT category_id, category_name FROM ProblemCategories;")
        categories = [dict(row) for row in cur.fetchall()]
        cur.close()
        return categories
    except psycopg2.Error as e:
        logger.error(f"Error fetching problem categories from DB: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_tickets_from_db():
    """
    Fetches all tickets from the database.
    
    @return: List of ticket dictionaries
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT ticket_id, subject, description, created_at, updated_at, closed_at, user_id, assigned_staff_id, status_id, category_id FROM Tickets;")
        tickets = [dict(row) for row in cur.fetchall()]
        cur.close()
        return tickets
    except psycopg2.Error as e:
        logger.error(f"Error fetching tickets from DB: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_comments_from_db():
    """
    Fetches all comments from the database.
    
    @return: List of comment dictionaries
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT comment_id, ticket_id, author_id, author_type, comment_text, created_at FROM TicketComments;")
        comments = [dict(row) for row in cur.fetchall()]
        cur.close()
        return comments
    except psycopg2.Error as e:
        logger.error(f"Error fetching comments from DB: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_logs_from_db():
    """
    Fetches all logs from the database.
    
    @return: List of log dictionaries
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT log_id, ticket_id, action, performed_by_staff_id, performed_at FROM TicketLogs;")
        logs = [dict(row) for row in cur.fetchall()]
        cur.close()
        return logs
    except psycopg2.Error as e:
        logger.error(f"Error fetching logs from DB: {e}")
        return []
    finally:
        if conn:
            conn.close()

# --- Functions to get data by ID ---
# These now search within the lists loaded from the DB
def get_user_by_id(user_id, users_list):
    """
    Finds a user by ID in the provided list.
    
    @param user_id: The ID of the user to find
    @param users_list: The list of users to search in
    @return: User dictionary or None if not found
    """
    return next((u for u in users_list if u['user_id'] == user_id), None)

def get_staff_by_id(staff_id, staff_list):
    """
    Finds a staff member by ID in the provided list.
    
    @param staff_id: The ID of the staff member to find
    @param staff_list: The list of staff to search in
    @return: Staff dictionary or None if not found
    """
    return next((s for s in staff_list if s['staff_id'] == staff_id), None)

def get_status_by_id(status_id, statuses_list):
    """
    Finds a status by ID in the provided list.
    
    @param status_id: The ID of the status to find
    @param statuses_list: The list of statuses to search in
    @return: Status dictionary or None if not found
    """
    return next((s for s in statuses_list if s['status_id'] == status_id), None)

def get_category_by_id(category_id, categories_list):
    """
    Finds a category by ID in the provided list.
    
    @param category_id: The ID of the category to find
    @param categories_list: The list of categories to search in
    @return: Category dictionary or None if not found
    """
    return next((c for c in categories_list if c['category_id'] == category_id), None)

def get_tickets_by_staff(staff_id, tickets_list):
    """
    Filters tickets assigned to a specific staff member.
    
    @param staff_id: The ID of the staff member
    @param tickets_list: The list of tickets to filter
    @return: List of ticket dictionaries assigned to the staff member
    """
    return [t for t in tickets_list if t['assigned_staff_id'] == staff_id]

def get_comments_by_ticket(ticket_id, comments_list):
    """
    Filters comments associated with a specific ticket.
    
    @param ticket_id: The ID of the ticket
    @param comments_list: The list of comments to filter
    @return: List of comment dictionaries for the ticket
    """
    return [c for c in comments_list if c['ticket_id'] == ticket_id]

def get_logs_by_ticket(ticket_id, logs_list):
    """
    Filters logs associated with a specific ticket.
    
    @param ticket_id: The ID of the ticket
    @param logs_list: The list of logs to filter
    @return: List of log dictionaries for the ticket
    """
    return [l for l in logs_list if l['ticket_id'] == ticket_id]

def get_departments_from_db():
    """
    Fetches distinct department names from the Staff table.
    
    @return: List of department names
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT DISTINCT department FROM Staff ORDER BY department;")
        all_departments = [row['department'] for row in cur.fetchall()]
        cur.close()
        return all_departments
    except psycopg2.Error as e:
        logger.error(f"Error fetching departments from DB: {e}")
        return []
    finally:
        if conn:
            conn.close()