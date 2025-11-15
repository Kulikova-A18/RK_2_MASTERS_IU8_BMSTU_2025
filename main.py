from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
import os
from constants import API_HOST, API_PORT, API_DEBUG, LOG_FILE, LOG_MAX_SIZE, LOG_BACKUP_COUNT, DEFAULT_USERS
from db_utils import (
    get_users_from_db, get_staff_from_db, get_ticket_statuses_from_db,
    get_problem_categories_from_db, get_tickets_from_db, get_comments_from_db, get_logs_from_db
)
from api_endpoints import create_endpoints

def setup_logging():
    """
    Configures the logging system for the application.
    
    @return: Configured logger instance
    """
    # REMOVED: logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Rotating file handler
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=LOG_MAX_SIZE, backupCount=LOG_BACKUP_COUNT)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler) # Add handler to the root logger

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(console_handler) 
    
    return logger

def load_database_data(logger):
    """
    Loads all necessary data from the database at application startup.
    
    @param logger: Logger instance for logging operations
    @return: Tuple containing all loaded data: (TEST_USERS, TEST_STAFF, TICKET_STATUSES, PROBLEM_CATEGORIES, TEST_TICKETS, TEST_COMMENTS, TEST_LOGS)
    """
    logger.info("Loading data from the database...")
    TEST_USERS = get_users_from_db()
    TEST_STAFF = get_staff_from_db() 
    TICKET_STATUSES = get_ticket_statuses_from_db()
    PROBLEM_CATEGORIES = get_problem_categories_from_db()
    TEST_TICKETS = get_tickets_from_db()
    TEST_COMMENTS = get_comments_from_db()
    TEST_LOGS = get_logs_from_db()

    if not all([TEST_USERS, TEST_STAFF, TICKET_STATUSES, PROBLEM_CATEGORIES, TEST_TICKETS, TEST_COMMENTS, TEST_LOGS]):
        logger.critical("Critical error: Could not load data from the database.")
        exit(1)

    logger.info(f"Data loaded: {len(TEST_USERS)} users, {len(TEST_STAFF)} staff, {len(TEST_TICKETS)} tickets.")
    return TEST_USERS, TEST_STAFF, TICKET_STATUSES, PROBLEM_CATEGORIES, TEST_TICKETS, TEST_COMMENTS, TEST_LOGS

def print_user_credentials(logger):
    """
    Prints all available user credentials from the DEFAULT_USERS dictionary.
    
    @param logger: Logger instance for logging operations
    @return: None
    """
    logger.info("Available users (for authentication):")
    
    # Dynamically print all available users and their credentials from DEFAULT_USERS
    for username, user_info in DEFAULT_USERS.items():
        logger.info(f"  Login: {username}")
        logger.info(f"    Role: {user_info['role']}")
        logger.info(f"    Name: {user_info['name']}")
        logger.info(f"    Staff ID: {user_info['staff_id']}")
        logger.info(f"    Departments: {', '.join(user_info['departments'])}")
        logger.info(f"    Password: {user_info['code']}")
        logger.info("    ---")

def main():
    """
    Main function to initialize the Flask application, configure logging, load data,
    register endpoints, and start the server.
    
    @return: None (runs the Flask application)
    """
    logger = setup_logging()
    
    app = Flask(__name__)

    # --- Load Data from Database at Startup ---
    TEST_USERS, TEST_STAFF, TICKET_STATUSES, PROBLEM_CATEGORIES, TEST_TICKETS, TEST_COMMENTS, TEST_LOGS = load_database_data(logger)

    # --- Register API Endpoints ---
    create_endpoints(app, TEST_USERS, TEST_STAFF, TICKET_STATUSES, PROBLEM_CATEGORIES, TEST_TICKETS, TEST_COMMENTS, TEST_LOGS)

    if __name__ == '__main__':
        logger.info("=" * 50)
        logger.info("HelpDesk API Server Started")
        
        print_user_credentials(logger)
        
        logger.info("Test data loaded from DB:")
        logger.info(f"  Users: {len(TEST_USERS)}")
        logger.info(f"  Staff: {len(TEST_STAFF)}")
        logger.info(f"  Tickets: {len(TEST_TICKETS)}")
        logger.info(f"  Comments: {len(TEST_COMMENTS)}")
        logger.info(f"  Logs: {len(TEST_LOGS)}")

        logger.info(f"Server running on http://{API_HOST}:{API_PORT}")
        app.run(host=API_HOST, port=API_PORT, debug=API_DEBUG)

if __name__ == '__main__':
    main()
