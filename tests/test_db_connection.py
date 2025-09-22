import sys
import os
import logging
from dotenv import load_dotenv

# Projenin kök dizinini sys.path'e ekle
PACKAGE_PARENT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PACKAGE_PARENT not in sys.path:
    sys.path.insert(0, PACKAGE_PARENT)

# .env dosyasını yükle
# Test dosyasının bulunduğu dizinden bir üst dizindeki .env dosyasını hedefle
DOTENV_PATH = os.path.join(PACKAGE_PARENT, '.env')
load_dotenv(DOTENV_PATH)

# Configure logging for the test
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info(".env file loaded.")
logging.info(f"DB_HOST={os.getenv('DB_HOST')}")
logging.info(f"DB_NAME={os.getenv('DB_NAME')}")

from app.database.db_connection import test_connection

def run_db_test():
    """
    Tests the database connection and prints the result.
    """
    logging.info("Starting database connection test...")
    
    is_connected = test_connection()
    
    if is_connected:
        logging.info("\033[92mSUCCESS: Database connection established successfully!\033[0m")
    else:
        logging.error("\033[91mERROR: Could not establish database connection. Please check your .env settings.\033[0m")

if __name__ == "__main__":
    run_db_test()
