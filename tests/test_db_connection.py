import sys
import os
from dotenv import load_dotenv

# Projenin kök dizinini sys.path'e ekle
PACKAGE_PARENT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PACKAGE_PARENT not in sys.path:
    sys.path.insert(0, PACKAGE_PARENT)

# .env dosyasını yükle
# Test dosyasının bulunduğu dizinden bir üst dizindeki .env dosyasını hedefle
DOTENV_PATH = os.path.join(PACKAGE_PARENT, '.env')
load_dotenv(DOTENV_PATH)

print("DEBUG: .env file loaded.")
print(f"DEBUG: DB_HOST={os.getenv('DB_HOST')}")
print(f"DEBUG: DB_NAME={os.getenv('DB_NAME')}")

from app.database.db_connection import test_connection

def run_db_test():
    """
    Tests the database connection and prints the result.
    """
    print("\nStarting database connection test...")
    
    is_connected = test_connection()
    
    if is_connected:
        print("\033[92mSUCCESS: Database connection established successfully!\033[0m")
    else:
        print("\033[91mERROR: Could not establish database connection. Please check your .env settings.\033[0m")

if __name__ == "__main__":
    run_db_test()
