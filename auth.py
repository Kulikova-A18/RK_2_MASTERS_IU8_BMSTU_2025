import hashlib
import secrets
import logging
from constants import DEFAULT_USERS
from db_utils import get_db_connection, get_staff_by_id
from psycopg2.extras import RealDictCursor
import re

logger = logging.getLogger(__name__)

def validate_username(username):
    """
    Validates the username format to prevent SQL injection and other attacks.
    Allows only alphanumeric characters, underscores, and hyphens. Length 1-50.
    
    @param username: The username string to validate. Expected to be a string.
    @return: Boolean indicating if the username is valid (True) or invalid (False).
    """
    if not isinstance(username, str):
        return False
    # Regex pattern: alphanumeric, underscore, hyphen, length 1-50
    pattern = r'^[a-zA-Z0-9_-]{1,50}$'
    return bool(re.match(pattern, username))

def get_user_credentials_from_db(username):
    """
    Fetches the password hash and user data from the DEFAULT_USERS dictionary.
    This function currently uses a static dictionary for demonstration.
    In a real application, it would query the database for user credentials.
    
    @param username: The username to look up. Must be validated to prevent injection.
                     Should be a string matching the validation pattern.
    @return: Dictionary containing user data (e.g., code_hash, role, name, staff_id, departments, code)
             or None if the username is not found or invalid.
    """
    # Validate username to prevent injection
    if not validate_username(username):
        logger.warning(f"Invalid username format: {username}")
        return None
        
    # This is a placeholder. In a real app, you would query the DB here.
    # For now, we use the static dictionary as the source of truth for authentication.
    # The DB is used for other data like staff info, tickets, etc.
    # This function mimics a DB lookup for the static data.
    return DEFAULT_USERS.get(username)

def authenticate_user(login, code):
    """
    Authenticates a user based on login and code. Implements input validation
    and secure comparison to prevent timing attacks and injection.
    
    @param login: The username provided by the client. Must be validated.
                  Should be a string matching the validation pattern.
    @param code: The code provided by the client. Expected to be a string.
                 This will be hashed using SHA-256 for comparison.
    @return: Tuple containing:
             - success (bool): True if authentication is successful, False otherwise.
             - user_data (dict or None): User data dictionary if successful, None otherwise.
    """
    # Validate inputs
    if not isinstance(login, str) or not isinstance(code, str):
        logger.warning("Invalid input types for authentication")
        return False, None

    # Validate username format
    if not validate_username(login):
        logger.warning(f"Invalid username format during authentication: {login}")
        return False, None

    # Check code length to prevent DoS attacks (e.g., very long strings)
    if len(code) > 100:  # Arbitrary limit, adjust as needed
        logger.warning(f"Code too long for user: {login}")
        return False, None

    user_data = get_user_credentials_from_db(login)
    if not user_data:
        logger.warning(f"Login attempt with non-existent username: {login}")
        # Perform a dummy hash comparison to maintain constant time and prevent timing attacks
        # Even if user doesn't exist, we still do the comparison to avoid leaking info
        dummy_hash = hashlib.sha256(b"dummy").hexdigest()
        secrets.compare_digest(dummy_hash, dummy_hash)
        return False, None

    # Hash the provided code
    try:
        code_hash = hashlib.sha256(code.encode('utf-8')).hexdigest()
    except UnicodeEncodeError:
        logger.warning(f"Invalid encoding for code from user: {login}")
        return False, None

    # Use secrets.compare_digest for constant-time comparison to prevent timing attacks
    if secrets.compare_digest(user_data['code_hash'], code_hash):
        logger.info(f"Successful authentication for user: {login}")
        return True, user_data
    logger.warning(f"Invalid code for user: {login}")
    return False, None