from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class MainMenuView(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        
        # Apply modern styling consistent with existing app
        self.apply_styling()
        
        # Create main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(30)
        
        # Title
        title_label = QLabel("Welcome to Dish Manager")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: #2c3e50; 
            margin-bottom: 20px;
            background-color: transparent;
            border: none;
            selection-background-color: transparent;
        """)
        title_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.main_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Choose what you'd like to do:")
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            color: #6c757d; 
            margin-bottom: 30px;
            background-color: transparent;
            border: none;
            selection-background-color: transparent;
        """)
        subtitle_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        subtitle_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.main_layout.addWidget(subtitle_label)
        
        # Button container
        button_container = QHBoxLayout()
        button_container.setSpacing(30)
        button_container.addStretch()
        
        # Meal Scheduler button (on the left)
        self.scheduler_button = QPushButton("Meal Scheduler")
        self.scheduler_button.setFixedSize(250, 150)
        self.scheduler_button.clicked.connect(self.open_scheduler)
        self.scheduler_button.setProperty("class", "menu-secondary")
        button_container.addWidget(self.scheduler_button)
        
        # Dish Manager button (on the right)
        self.dish_manager_button = QPushButton("Dish Collection")
        self.dish_manager_button.setFixedSize(250, 150)
        self.dish_manager_button.clicked.connect(self.open_dish_manager)
        self.dish_manager_button.setProperty("class", "menu-primary")
        button_container.addWidget(self.dish_manager_button)
        
        button_container.addStretch()
        self.main_layout.addLayout(button_container)
        
        # Add stretch to center everything
        self.main_layout.addStretch()
        
        self.setLayout(self.main_layout)
        
    def apply_styling(self):
        """Apply modern styling consistent with existing dish manager"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
                font-size: 13px;
                color: #2c3e50;
            }
            
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 20px;
                font-size: 16px;
                font-weight: 600;
                text-align: center;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #21618c;
            }
            
            QPushButton[class="menu-primary"] {
                background-color: #28a745;
            }
            
            QPushButton[class="menu-primary"]:hover {
                background-color: #218838;
            }
            
            QPushButton[class="menu-secondary"] {
                background-color: #17a2b8;
            }
            
            QPushButton[class="menu-secondary"]:hover {
                background-color: #138496;
            }
        """)
    
    def open_dish_manager(self):
        """Open the existing dish manager"""
        self.main_app.show_dish_manager()
        
    def open_scheduler(self):
        """Open the meal scheduler"""
        self.main_app.show_scheduler()

class MainMenu(QWidget):
    """Main application window with stacked views"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dish Manager")
        self.setMinimumSize(1200, 700)
        
        # Create stacked widget for different views
        self.stacked_widget = QStackedWidget()
        
        # Create views
        self.menu_view = MainMenuView(self)
        self.dish_manager_view = None
        self.scheduler_view = None
        
        # Add menu view to stack
        self.stacked_widget.addWidget(self.menu_view)
        
        # Set layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)
        
    def show_menu(self):
        """Show the main menu"""
        self.stacked_widget.setCurrentWidget(self.menu_view)
        
    def show_dish_manager(self):
        """Show the dish manager"""
        if self.dish_manager_view is None:
            from dish_manager import DishManager
            self.dish_manager_view = DishManager()
            # Remove the dish manager's own window setup
            self.dish_manager_view.setWindowTitle("")
            self.stacked_widget.addWidget(self.dish_manager_view)
        
        self.stacked_widget.setCurrentWidget(self.dish_manager_view)
        
    def show_scheduler(self):
        """Show the scheduler"""
        if self.scheduler_view is None:
            from scheduler import Scheduler
            self.scheduler_view = Scheduler()
            # Remove the scheduler's own window setup
            self.scheduler_view.setWindowTitle("")
            self.stacked_widget.addWidget(self.scheduler_view)
        
        self.stacked_widget.setCurrentWidget(self.scheduler_view)