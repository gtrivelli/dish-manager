import sys
import os
from PyQt6.QtWidgets import QApplication
from dotenv import load_dotenv

if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load .env file from the script directory
    load_dotenv(os.path.join(script_dir, '.env'))
    
    app = QApplication(sys.argv)
    
    # Import here to avoid circular imports
    from main_menu import MainMenu
    
    window = MainMenu()
    window.show()
    sys.exit(app.exec())