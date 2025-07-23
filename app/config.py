# Configuration file for the Zekai application

# IMPORTANT: Update these with your actual MySQL connection details
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': '',  # Replace with your MySQL password
    'database': 'zekai'  # Replace with your database name
}

# Add other configurations here as needed, for example:
# API_KEYS = {
#     'GEMINI_API_KEY': 'YOUR_GEMINI_API_KEY_HERE'
# }
# DEBUG = True


# AI Service Cache Configuration
AI_SERVICE_CACHE = {
    'max_size': 50,
    'ttl_hours': 24
}

# Database Pool Configuration
DB_CONFIG.update({
    'pool_size': 10,
    'pool_reset_session': True
})


