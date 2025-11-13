# --- Database Connection Settings ---
DB_NAME = 'support_system'
DB_USER = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'
# Replace 'new_secure_password' with the actual password for the 'postgres' user
# This password must match the one set by the create_support_db.sh script
DB_PASSWORD = 'new_secure_password' 

# --- API Default Users (Hardcoded for demonstration) ---
# In a real application, these should be stored securely in the database.
import hashlib
DEFAULT_USERS = {
    'admin': {
        'code_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
        'role': 'admin',
        'name': 'System Administrator',
        'staff_id': 1,
        'departments': ['Technical Support Department', 'System Administration Department'] # Example from DB
    },
    'manager_it': {
        'code_hash': hashlib.sha256('it2024'.encode()).hexdigest(),
        'role': 'manager',
        'name': 'Ivan Petrov',
        'staff_id': 2,
        'departments': ['Technical Support Department']
    },
    'manager_hr': {
        'code_hash': hashlib.sha256('hr2024'.encode()).hexdigest(),
        'role': 'manager',
        'name': 'Maria Kozlova',
        'staff_id': 3,
        'departments': ['Development and Implementation Department']
    },
    'analyst': {
        'code_hash': hashlib.sha256('analyst2024'.encode()).hexdigest(),
        'role': 'analyst',
        'name': 'Petr Sidrov',
        'staff_id': 4,
        'departments': ['Technical Support Department', 'System Administration Department']
    }
}

# --- API Configuration ---
API_HOST = '0.0.0.0'
API_PORT = 5000
API_DEBUG = True
LOG_FILE = 'logs/api.log'
LOG_MAX_SIZE = 10240 # in bytes
LOG_BACKUP_COUNT = 10