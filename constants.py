# --- Database Connection Settings ---
# @param DB_NAME: Name of the PostgreSQL database to connect to. Must match the database created by the script.
# @param DB_USER: Database user account name for authentication.
# @param DB_HOST: Host address of the PostgreSQL server. Use 'localhost' for local connections.
# @param DB_PORT: Port number on which the PostgreSQL server is listening. Default is 5432.
# @param DB_PASSWORD: Password for the database user. Must be identical to the password set in create_support_db.sh.
DB_NAME = 'support_system'
DB_USER = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_PASSWORD = 'new_secure_password'

# --- API Default Users (Hardcoded for demonstration) ---
# @param ADMIN_CODE: Secure access code for the admin user. Must be at least 10 characters, containing uppercase, lowercase, and digits.
# @param TS_MANAGER_CODE: Secure access code for the Technical Support manager user.
# @param SA_MANAGER_CODE: Secure access code for the System Administration manager user.
# @param NI_MANAGER_CODE: Secure access code for the Network Infrastructure manager user.
# @param IS_MANAGER_CODE: Secure access code for the Information Security manager user.
# @param DI_MANAGER_CODE: Secure access code for the Development and Implementation manager user.
# @param DB_MANAGER_CODE: Secure access code for the Database manager user.
# @param CT_MANAGER_CODE: Secure access code for the Cloud Technologies manager user.
# @param MA_MANAGER_CODE: Secure access code for the Monitoring and Analytics manager user.
# @param L1_MANAGER_CODE: Secure access code for the Level 1 Service Desk manager user.
# @param L2_MANAGER_CODE: Secure access code for the Level 2 Service Desk manager user.
# @param TS_ANALYST_CODE: Secure access code for the Technical Support analyst user.
# @param SA_ANALYST_CODE: Secure access code for the System Administration analyst user.
# @param NI_ANALYST_CODE: Secure access code for the Network Infrastructure analyst user.
# @param IS_ANALYST_CODE: Secure access code for the Information Security analyst user.
# @param DI_ANALYST_CODE: Secure access code for the Development and Implementation analyst user.
# @param DB_ANALYST_CODE: Secure access code for the Database analyst user.
# @param CT_ANALYST_CODE: Secure access code for the Cloud Technologies analyst user.
# @param MA_ANALYST_CODE: Secure access code for the Monitoring and Analytics analyst user.
# @param L1_ANALYST_CODE: Secure access code for the Level 1 Service Desk analyst user.
# @param L2_ANALYST_CODE: Secure access code for the Level 2 Service Desk analyst user.
import hashlib

ADMIN_CODE = "AbC12xYz90Kl"
TS_MANAGER_CODE = "DeF34mNo56Pq"
SA_MANAGER_CODE = "GhI78wXy12Rt"
NI_MANAGER_CODE = "JkL56vBn78St"
IS_MANAGER_CODE = "MnO90pQr34Uv"
DI_MANAGER_CODE = "EfG23aSd56Wx"
DB_MANAGER_CODE = "HiJ67fGh89Yz"
CT_MANAGER_CODE = "KlM01jKl23Ab"
MA_MANAGER_CODE = "OpQ45hJk67Cd"
L1_MANAGER_CODE = "RsT89gFg01Ef"
L2_MANAGER_CODE = "UvW23eDc45Gh"
TS_ANALYST_CODE = "XyZ67iOp89Ij"
SA_ANALYST_CODE = "BcD01oLm23Kl"
NI_ANALYST_CODE = "EfG45pQr67Mn"
IS_ANALYST_CODE = "HjK89sTu01Op"
DI_ANALYST_CODE = "LmN23vWx45Qr"
DB_ANALYST_CODE = "PqR67zAb89St"
CT_ANALYST_CODE = "TuV01cDe23Uv"
MA_ANALYST_CODE = "WxY45fGh67Vw"
L1_ANALYST_CODE = "AbC89jKl01Xy"
L2_ANALYST_CODE = "DeF23mNo45Za"

# @param DEFAULT_USERS: Dictionary containing predefined users for the system.
# Each user has the following properties:
# - code_hash: SHA-256 hash of the user's access code.
# - role: Role of the user (e.g., 'admin', 'manager', 'analyst').
# - name: Full name of the user.
# - staff_id: Unique identifier for the staff member in the database.
# - departments: List of departments the user is associated with.
# - code: Plain text access code for reference or debugging (should not be exposed in production).
DEFAULT_USERS = {
    'admin': {
        'code_hash': hashlib.sha256(ADMIN_CODE.encode()).hexdigest(),
        'role': 'admin',
        'name': 'System Administrator',
        'staff_id': 1,
        'departments': [
            'Отдел технической поддержки',
            'Отдел системного администрирования',
            'Отдел сетевой инфраструктуры',
            'Отдел информационной безопасности',
            'Отдел разработки и внедрения',
            'Отдел баз данных',
            'Отдел облачных технологий',
            'Отдел мониторинга и аналитики',
            'Сервисный деск Level 1',
            'Сервисный деск Level 2'
        ],
        'code': ADMIN_CODE
    },
    'manager_ts': {
        'code_hash': hashlib.sha256(TS_MANAGER_CODE.encode()).hexdigest(),
        'role': 'manager',
        'name': 'Alexey Smirnov',
        'staff_id': 2,
        'departments': ['Отдел технической поддержки'],
        'code': TS_MANAGER_CODE
    },
    'manager_sa': {
        'code_hash': hashlib.sha256(SA_MANAGER_CODE.encode()).hexdigest(),
        'role': 'manager',
        'name': 'Irina Kozlova',
        'staff_id': 3,
        'departments': ['Отдел системного администрирования'],
        'code': SA_MANAGER_CODE
    },
    'manager_ni': {
        'code_hash': hashlib.sha256(NI_MANAGER_CODE.encode()).hexdigest(),
        'role': 'manager',
        'name': 'Denis Novikov',
        'staff_id': 4,
        'departments': ['Отдел сетевой инфраструктуры'],
        'code': NI_MANAGER_CODE
    },
    'manager_is': {
        'code_hash': hashlib.sha256(IS_MANAGER_CODE.encode()).hexdigest(),
        'role': 'manager',
        'name': 'Olga Makarova',
        'staff_id': 5,
        'departments': ['Отдел информационной безопасности'],
        'code': IS_MANAGER_CODE
    },
    'manager_di': {
        'code_hash': hashlib.sha256(DI_MANAGER_CODE.encode()).hexdigest(),
        'role': 'manager',
        'name': 'Artem Zaitsev',
        'staff_id': 6,
        'departments': ['Отдел разработки и внедрения'],
        'code': DI_MANAGER_CODE
    },
    'manager_db': {
        'code_hash': hashlib.sha256(DB_MANAGER_CODE.encode()).hexdigest(),
        'role': 'manager',
        'name': 'Natalia Popova',
        'staff_id': 7,
        'departments': ['Отдел баз данных'],
        'code': DB_MANAGER_CODE
    },
    'manager_ct': {
        'code_hash': hashlib.sha256(CT_MANAGER_CODE.encode()).hexdigest(),
        'role': 'manager',
        'name': 'Maksim Solovev',
        'staff_id': 8,
        'departments': ['Отдел облачных технологий'],
        'code': CT_MANAGER_CODE
    },
    'manager_ma': {
        'code_hash': hashlib.sha256(MA_MANAGER_CODE.encode()).hexdigest(),
        'role': 'manager',
        'name': 'Elena Vorobeva',
        'staff_id': 9,
        'departments': ['Отдел мониторинга и аналитики'],
        'code': MA_MANAGER_CODE
    },
    'manager_l1': {
        'code_hash': hashlib.sha256(L1_MANAGER_CODE.encode()).hexdigest(),
        'role': 'manager',
        'name': 'Ivan Frolov',
        'staff_id': 10,
        'departments': ['Сервисный деск Level 1'],
        'code': L1_MANAGER_CODE
    },
    'manager_l2': {
        'code_hash': hashlib.sha256(L2_MANAGER_CODE.encode()).hexdigest(),
        'role': 'manager',
        'name': 'Svetlana Alekseeva',
        'staff_id': 11,
        'departments': ['Сервисный деск Level 2'],
        'code': L2_MANAGER_CODE
    },
    'analyst_ts': {
        'code_hash': hashlib.sha256(TS_ANALYST_CODE.encode()).hexdigest(),
        'role': 'analyst',
        'name': 'Petr Sidrov',
        'staff_id': 12,
        'departments': ['Отдел технической поддержки'],
        'code': TS_ANALYST_CODE
    },
    'analyst_sa': {
        'code_hash': hashlib.sha256(SA_ANALYST_CODE.encode()).hexdigest(),
        'role': 'analyst',
        'name': 'Anna Orlova',
        'staff_id': 13,
        'departments': ['Отдел системного администрирования'],
        'code': SA_ANALYST_CODE
    },
    'analyst_ni': {
        'code_hash': hashlib.sha256(NI_ANALYST_CODE.encode()).hexdigest(),
        'role': 'analyst',
        'name': 'Mikhail Lebedev',
        'staff_id': 14,
        'departments': ['Отдел сетевой инфраструктуры'],
        'code': NI_ANALYST_CODE
    },
    'analyst_is': {
        'code_hash': hashlib.sha256(IS_ANALYST_CODE.encode()).hexdigest(),
        'role': 'analyst',
        'name': 'Irina Semenova',
        'staff_id': 15,
        'departments': ['Отдел информационной безопасности'],
        'code': IS_ANALYST_CODE
    },
    'analyst_di': {
        'code_hash': hashlib.sha256(DI_ANALYST_CODE.encode()).hexdigest(),
        'role': 'analyst',
        'name': 'Artem Fedorov',
        'staff_id': 16,
        'departments': ['Отдел разработки и внедрения'],
        'code': DI_ANALYST_CODE
    },
    'analyst_db': {
        'code_hash': hashlib.sha256(DB_ANALYST_CODE.encode()).hexdigest(),
        'role': 'analyst',
        'name': 'Tatyana Zhukova',
        'staff_id': 17,
        'departments': ['Отдел баз данных'],
        'code': DB_ANALYST_CODE
    },
    'analyst_ct': {
        'code_hash': hashlib.sha256(CT_ANALYST_CODE.encode()).hexdigest(),
        'role': 'analyst',
        'name': 'Sergey Gromov',
        'staff_id': 18,
        'departments': ['Отдел облачных технологий'],
        'code': CT_ANALYST_CODE
    },
    'analyst_ma': {
        'code_hash': hashlib.sha256(MA_ANALYST_CODE.encode()).hexdigest(),
        'role': 'analyst',
        'name': 'Nadezhda Volkova',
        'staff_id': 19,
        'departments': ['Отдел мониторинга и аналитики'],
        'code': MA_ANALYST_CODE
    },
    'analyst_l1': {
        'code_hash': hashlib.sha256(L1_ANALYST_CODE.encode()).hexdigest(),
        'role': 'analyst',
        'name': 'Alexei Tikhonov',
        'staff_id': 20,
        'departments': ['Сервисный деск Level 1'],
        'code': L1_ANALYST_CODE
    },
    'analyst_l2': {
        'code_hash': hashlib.sha256(L2_ANALYST_CODE.encode()).hexdigest(),
        'role': 'analyst',
        'name': 'Yulia Andreeva',
        'staff_id': 21,
        'departments': ['Сервисный деск Level 2'],
        'code': L2_ANALYST_CODE
    }
}

# --- API Configuration ---
# @param API_HOST: Host address for the Flask API server. Use '0.0.0.0' to bind to all available interfaces.
# @param API_PORT: Port number on which the Flask API server will listen for requests.
# @param API_DEBUG: Enables or disables Flask debug mode. Set to True for development, False for production.
# @param LOG_FILE: Path to the file where API logs will be written.
# @param LOG_MAX_SIZE: Maximum size of a single log file in bytes before rotation occurs.
# @param LOG_BACKUP_COUNT: Number of backup log files to keep during rotation.
API_HOST = '0.0.0.0'
API_PORT = 5000
API_DEBUG = True
LOG_FILE = 'logs/api.log'
LOG_MAX_SIZE = 10240  # in bytes
LOG_BACKUP_COUNT = 10