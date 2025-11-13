import hashlib
import secrets
import logging
from constants import DEFAULT_USERS
from db_utils import get_db_connection, get_staff_by_id
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

def get_user_credentials_from_db(username):
    """
    Fetches the password hash and user data from the database by username.
    This function currently uses a static dictionary for demonstration.
    In a real application, it would query the database for user credentials.
    
    @param username: The username to look up
    @return: Dictionary containing user data or None if not found
    """
    # This is a placeholder. In a real app, you would query the DB here.
    # For now, we use the static dictionary as the source of truth for authentication.
    # The DB is used for other data like staff info, tickets, etc.
    # This function mimics a DB lookup for the static data.
    return DEFAULT_USERS.get(username)

def authenticate_user(login, code):
    """
    Authenticates a user based on login and code.
    
    @param login: The username provided by the client
    @param code: The code provided by the client
    @return: Tuple (success: bool, user_data dict or None)
    """
    user_data = get_user_credentials_from_db(login)
    if not user_data:
        logger.warning(f"Login attempt with non-existent username: {login}")
        return False, None
    code_hash = hashlib.sha256(code.encode()).hexdigest()
    if secrets.compare_digest(user_data['code_hash'], code_hash):
        logger.info(f"Successful authentication for user: {login}")
        return True, user_data
    logger.warning(f"Invalid code for user: {login}")
    return False, None