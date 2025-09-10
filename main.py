import sys
import os
from PyQt6.QtWidgets import QApplication
from dish_manager import DishManager
from dotenv import load_dotenv

if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load .env file from the script directory
    load_dotenv(os.path.join(script_dir, '.env'))
    
    app = QApplication(sys.argv)
    
    window = DishManager()
    window.show()
    sys.exit(app.exec())