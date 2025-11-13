from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
import os
from constants import API_HOST, API_PORT, API_DEBUG, LOG_FILE, LOG_MAX_SIZE, LOG_BACKUP_COUNT
from db_utils import (
    get_users_from_db, get_staff_from_db, get_ticket_statuses_from_db,
    get_problem_categories_from_db, get_tickets_from_db, get_comments_from_db, get_logs_from_db
)
from api_endpoints import create_endpoints

# --- Logging Setup ---
# REMOVED: logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) # Get the root logger or create a new one named __main__
logger.setLevel(logging.INFO) # Set level for the root logger

# Create logs directory if it doesn't exist
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
logger.addHandler(console_handler) # Add handler to the root logger

app = Flask(__name__)

# --- Load Data from Database at Startup ---
logger.info("Loading data from the database...")
TEST_USERS = get_users_from_db()
TEST_STAFF = get_staff_from_db() # Now includes 'department'
TICKET_STATUSES = get_ticket_statuses_from_db()
PROBLEM_CATEGORIES = get_problem_categories_from_db()
TEST_TICKETS = get_tickets_from_db()
TEST_COMMENTS = get_comments_from_db()
TEST_LOGS = get_logs_from_db()

if not all([TEST_USERS, TEST_STAFF, TICKET_STATUSES, PROBLEM_CATEGORIES, TEST_TICKETS, TEST_COMMENTS, TEST_LOGS]):
    logger.critical("Critical error: Could not load data from the database.")
    exit(1)

logger.info(f"Data loaded: {len(TEST_USERS)} users, {len(TEST_STAFF)} staff, {len(TEST_TICKETS)} tickets.")

# --- Register API Endpoints ---
create_endpoints(app, TEST_USERS, TEST_STAFF, TICKET_STATUSES, PROBLEM_CATEGORIES, TEST_TICKETS, TEST_COMMENTS, TEST_LOGS)

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("HelpDesk API Server Started")
    logger.info("Available users (for authentication): admin, manager_it, manager_hr, analyst")
    logger.info("Password for 'admin': admin123")
    logger.info("Password for 'manager_it': it2024")
    logger.info("Password for 'manager_hr': hr2024")
    logger.info("Password for 'analyst': analyst2024")
    logger.info("Test data loaded from DB:")
    logger.info(f"  Users: {len(TEST_USERS)}")
    logger.info(f"  Staff: {len(TEST_STAFF)}")
    logger.info(f"  Tickets: {len(TEST_TICKETS)}")
    logger.info(f"  Comments: {len(TEST_COMMENTS)}")
    logger.info(f"  Logs: {len(TEST_LOGS)}")
    logger.info("=" * 50)
    logger.info(f"Server running on http://{API_HOST}:{API_PORT}")
    app.run(host=API_HOST, port=API_PORT, debug=API_DEBUG)