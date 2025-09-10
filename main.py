import sys
from PyQt6.QtWidgets import QApplication
from dish_manager import DishManager
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    
    app = QApplication(sys.argv)
    
    window = DishManager()
    window.show()
    sys.exit(app.exec())