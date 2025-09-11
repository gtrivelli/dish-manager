from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QGridLayout, QFrame, QStackedWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta
from utilities import load_schedule, save_schedule, cleanup_old_ingredient_data
from meal_planning import MealPlanningView

class SchedulerCell(QFrame):
    """Individual cell in the scheduler grid representing one meal slot"""
    def __init__(self, date, meal_type, parent_scheduler):
        super().__init__()
        self.date = date
        self.meal_type = meal_type
        self.parent_scheduler = parent_scheduler
        self.meal_data = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the cell UI"""
        self.setFixedHeight(80)
        self.setProperty("class", "scheduler-cell")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Meal content label
        self.meal_label = QLabel("No meal planned")
        self.meal_label.setWordWrap(True)
        self.meal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.meal_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 11px;
                background-color: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.meal_label)
        
        self.setLayout(layout)
        
    def mouseDoubleClickEvent(self, event):
        """Handle double-click to edit meal"""
        self.parent_scheduler.edit_meal(self.date, self.meal_type)
        
    def update_meal_display(self, meal_data):
        """Update the cell display based on meal data"""
        self.meal_data = meal_data
        
        if not meal_data or meal_data.get("type") == "none":
            self.meal_label.setText("No meal planned")
            self.setProperty("meal_type", "none")
        elif meal_data.get("type") == "cook":
            dish_name = meal_data.get("dish_name", "Unknown dish")
            leftover_count = meal_data.get("leftover_meals", 0)
            text = f"COOK: {dish_name}"
            if leftover_count > 0:
                text += f"\n({leftover_count} leftovers)"
            self.meal_label.setText(text)
            self.setProperty("meal_type", "cook")
        elif meal_data.get("type") == "leftovers":
            dish_name = meal_data.get("dish_name", "Unknown dish")
            self.meal_label.setText(f"LEFTOVER: {dish_name}")
            self.setProperty("meal_type", "leftovers")
        elif meal_data.get("type") == "bought":
            description = meal_data.get("description", "Bought meal")
            self.meal_label.setText(f"BOUGHT: {description}")
            self.setProperty("meal_type", "bought")
        elif meal_data.get("type") == "frozen":
            description = meal_data.get("description", "Frozen food")
            self.meal_label.setText(f"FROZEN: {description}")
            self.setProperty("meal_type", "frozen")
            
        # Refresh style
        self.style().unpolish(self)
        self.style().polish(self)

class SchedulerMainView(QWidget):
    """Main scheduler view with weekly grid"""
    def __init__(self, scheduler_parent=None):
        super().__init__()
        self.scheduler_parent = scheduler_parent
        self.current_week_start = self.get_week_start(datetime.now())
        self.schedule_data = load_schedule()
        
        self.setup_ui()
        self.load_week_data()
        
        # Cleanup old data on startup
        cleanup_old_ingredient_data()
        
    def setup_ui(self):
        """Setup the scheduler UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with navigation
        header_layout = QHBoxLayout()
        
        # Back to menu button
        back_button = QPushButton("← Back to Menu")
        back_button.setProperty("class", "secondary")
        back_button.clicked.connect(self.back_to_menu)
        header_layout.addWidget(back_button)
        
        header_layout.addStretch()
        
        # Week navigation
        self.prev_week_button = QPushButton("◀ Previous Week")
        self.prev_week_button.clicked.connect(self.previous_week)
        header_layout.addWidget(self.prev_week_button)
        
        self.week_label = QLabel()
        self.week_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.week_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin: 0 20px;")
        header_layout.addWidget(self.week_label)
        
        self.next_week_button = QPushButton("Next Week ▶")
        self.next_week_button.clicked.connect(self.next_week)
        header_layout.addWidget(self.next_week_button)
        
        # Update week label after buttons are created
        self.update_week_label()
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Weekly grid
        self.create_weekly_grid()
        layout.addWidget(self.grid_frame)
        
        layout.addStretch()
        
        self.setLayout(layout)
        
    def create_weekly_grid(self):
        """Create the weekly meal planning grid"""
        self.grid_frame = QFrame()
        self.grid_frame.setProperty("class", "card")
        
        grid_layout = QVBoxLayout()
        grid_layout.setContentsMargins(15, 15, 15, 15)
        grid_layout.setSpacing(10)
        
        # Create grid
        self.grid = QGridLayout()
        self.grid.setSpacing(5)
        
        # Days of week headers
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        today = datetime.now()
        
        for i, day in enumerate(days):
            # Calculate the date for this column
            column_date = self.current_week_start + timedelta(days=i)
            is_today = column_date.date() == today.date()
            
            # Format day with date
            day_with_date = f"{day}\n{column_date.strftime('%m/%d')}"
            
            day_label = QLabel(day_with_date)
            day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            day_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            
            # Different styling for today vs other days
            if is_today:
                day_label.setStyleSheet("""
                    QLabel {
                        font-weight: bold;
                        color: white;
                        background-color: #3498db;
                        border: 2px solid #2980b9;
                        border-radius: 4px;
                        padding: 8px;
                        margin: 2px;
                    }
                """)
            else:
                day_label.setStyleSheet("""
                    QLabel {
                        font-weight: bold;
                        color: #2c3e50;
                        background-color: #e9ecef;
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                        padding: 8px;
                        margin: 2px;
                    }
                """)
            self.grid.addWidget(day_label, 0, i + 1)
        
        # Meal type labels
        meal_types = ["Lunch", "Dinner"]
        self.cells = {}
        
        for row, meal_type in enumerate(meal_types, 1):
            # Meal type label
            meal_label = QLabel(meal_type)
            meal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            meal_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            meal_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    color: #2c3e50;
                    background-color: #e9ecef;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 8px;
                    margin: 2px;
                }
            """)
            self.grid.addWidget(meal_label, row, 0)
            
            # Create cells for each day
            for col in range(7):
                date = self.current_week_start + timedelta(days=col)
                date_str = date.strftime("%Y-%m-%d")
                
                cell = SchedulerCell(date_str, meal_type.lower(), self)
                self.grid.addWidget(cell, row, col + 1)
                
                # Store cell reference
                self.cells[(date_str, meal_type.lower())] = cell
        
        grid_layout.addLayout(self.grid)
        self.grid_frame.setLayout(grid_layout)
        
    def get_week_start(self, date):
        """Get the Monday of the week containing the given date"""
        days_since_monday = date.weekday()
        week_start = date - timedelta(days=days_since_monday)
        return week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
    def update_week_label(self):
        """Update the week display label"""
        week_end = self.current_week_start + timedelta(days=6)
        start_str = self.current_week_start.strftime("%B %d")
        end_str = week_end.strftime("%B %d, %Y")
        self.week_label.setText(f"{start_str} - {end_str}")
        
        # Limit navigation to 2 weeks ahead
        today = datetime.now()
        max_week = self.get_week_start(today + timedelta(weeks=2))
        self.next_week_button.setEnabled(self.current_week_start < max_week)
        
    def previous_week(self):
        """Navigate to previous week"""
        self.current_week_start -= timedelta(weeks=1)
        self.update_week_label()
        self.refresh_grid()
        
    def next_week(self):
        """Navigate to next week"""
        self.current_week_start += timedelta(weeks=1)
        self.update_week_label()
        self.refresh_grid()
        
    def refresh_grid(self):
        """Refresh the grid with new week data"""
        # Clear all widgets from grid
        for i in reversed(range(self.grid.count())):
            child = self.grid.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Recreate day headers
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        today = datetime.now()
        
        for i, day in enumerate(days):
            # Calculate the date for this column
            column_date = self.current_week_start + timedelta(days=i)
            is_today = column_date.date() == today.date()
            
            # Format day with date
            day_with_date = f"{day}\n{column_date.strftime('%m/%d')}"
            
            day_label = QLabel(day_with_date)
            day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            day_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            
            # Different styling for today vs other days
            if is_today:
                day_label.setStyleSheet("""
                    QLabel {
                        font-weight: bold;
                        color: white;
                        background-color: #3498db;
                        border: 2px solid #2980b9;
                        border-radius: 4px;
                        padding: 8px;
                        margin: 2px;
                    }
                """)
            else:
                day_label.setStyleSheet("""
                    QLabel {
                        font-weight: bold;
                        color: #2c3e50;
                        background-color: #e9ecef;
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                        padding: 8px;
                        margin: 2px;
                    }
                """)
            self.grid.addWidget(day_label, 0, i + 1)
        
        # Recreate meal type labels and cells
        self.cells.clear()
        meal_types = ["Lunch", "Dinner"]
        
        for row, meal_type in enumerate(meal_types, 1):
            # Meal type label
            meal_label = QLabel(meal_type)
            meal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            meal_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            meal_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    color: #2c3e50;
                    background-color: #e9ecef;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 8px;
                    margin: 2px;
                }
            """)
            self.grid.addWidget(meal_label, row, 0)
            
            # Create cells for each day
            for col in range(7):
                date = self.current_week_start + timedelta(days=col)
                date_str = date.strftime("%Y-%m-%d")
                
                cell = SchedulerCell(date_str, meal_type.lower(), self)
                self.grid.addWidget(cell, row, col + 1)
                self.cells[(date_str, meal_type.lower())] = cell
        
        self.load_week_data()
        
    def load_week_data(self):
        """Load and display schedule data for current week"""
        schedule = self.schedule_data.get("schedule", {})
        
        for (date_str, meal_type), cell in self.cells.items():
            if date_str in schedule and meal_type in schedule[date_str]:
                meal_data = schedule[date_str][meal_type]
                cell.update_meal_display(meal_data)
            else:
                cell.update_meal_display(None)
                
    def edit_meal(self, date, meal_type):
        """Edit a meal slot"""
        # Get existing meal data
        schedule = self.schedule_data.get("schedule", {})
        existing_meal = None
        if date in schedule and meal_type in schedule[date]:
            existing_meal = schedule[date][meal_type]
            
        # Find the main Scheduler parent
        if self.scheduler_parent and hasattr(self.scheduler_parent, 'show_meal_planning_view'):
            self.scheduler_parent.show_meal_planning_view(date, meal_type, existing_meal)
        else:
            # Fallback: find it through parent hierarchy
            current_widget = self
            while current_widget and not hasattr(current_widget, 'show_meal_planning_view'):
                current_widget = current_widget.parent()
            
            if current_widget:
                current_widget.show_meal_planning_view(date, meal_type, existing_meal)
        
    def back_to_menu(self):
        """Return to main menu"""
        # Find the parent MainMenu window
        parent = self.parent()
        while parent and not hasattr(parent, 'show_menu'):
            parent = parent.parent()
        
        if parent:
            parent.show_menu()

class Scheduler(QWidget):
    """Main scheduler application window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meal Scheduler")
        self.setMinimumSize(1200, 700)
        
        # Apply styling consistent with dish manager
        self.apply_styling()
        
        # Use stacked widget for different views
        self.stacked_widget = QStackedWidget()
        
        # Create main scheduler view
        self.scheduler_view = SchedulerMainView(self)
        self.stacked_widget.addWidget(self.scheduler_view)
        
        # Meal planning view will be created as needed
        self.meal_planning_view = None
        
        # Set layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)
        
    def apply_styling(self):
        """Apply modern styling consistent with dish manager"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
                font-size: 13px;
                color: #2c3e50;
            }
            
            QLabel {
                color: #2c3e50;
                font-weight: 500;
            }
            
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #21618c;
            }
            
            QPushButton[class="secondary"] {
                background-color: #95a5a6;
            }
            
            QPushButton[class="secondary"]:hover {
                background-color: #7f8c8d;
            }
            
            QPushButton[class="counter-button"] {
                background-color: #f8f9fa;
                color: #2c3e50;
                border: 1px solid #dee2e6;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                min-width: 30px;
                padding: 0px;
            }
            
            QPushButton[class="counter-button"]:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            
            QPushButton[class="counter-button"]:pressed {
                background-color: #dee2e6;
            }
            
            QPushButton[class="danger"] {
                background-color: #dc3545;
            }
            
            QPushButton[class="danger"]:hover {
                background-color: #c82333;
            }
            
            QPushButton[class="danger"]:pressed {
                background-color: #bd2130;
            }
            
            QFrame[class="card"] {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 12px;
                padding: 15px;
            }
            
            QFrame[class="scheduler-cell"] {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                margin: 2px;
            }
            
            QFrame[class="scheduler-cell"]:hover {
                background-color: #f1f8ff;
                border-color: #cce7ff;
            }
            
            QFrame[class="scheduler-cell"][meal_type="cook"] {
                background-color: #e8f5e8;
                border-color: #28a745;
            }
            
            QFrame[class="scheduler-cell"][meal_type="leftovers"] {
                background-color: #fff3cd;
                border-color: #ffc107;
            }
            
            QFrame[class="scheduler-cell"][meal_type="bought"] {
                background-color: #e2e3e5;
                border-color: #6c757d;
            }
            
            QFrame[class="scheduler-cell"][meal_type="frozen"] {
                background-color: #d1ecf1;
                border-color: #17a2b8;
            }
        """)
        
    def show_meal_planning_view(self, date, meal_type, existing_meal=None):
        """Switch to meal planning view"""
        # Remove existing meal planning view if it exists
        if self.meal_planning_view:
            self.stacked_widget.removeWidget(self.meal_planning_view)
            self.meal_planning_view = None
            
        # Create new meal planning view
        self.meal_planning_view = MealPlanningView(self, date, meal_type, existing_meal)
        self.stacked_widget.addWidget(self.meal_planning_view)
        self.stacked_widget.setCurrentWidget(self.meal_planning_view)
        
    def show_scheduler_view(self):
        """Switch back to scheduler view"""
        # Refresh the scheduler data
        self.scheduler_view.schedule_data = load_schedule()
        self.scheduler_view.load_week_data()
        
        # Switch to scheduler view
        self.stacked_widget.setCurrentWidget(self.scheduler_view)
        
        # Clean up meal planning view
        if self.meal_planning_view:
            self.stacked_widget.removeWidget(self.meal_planning_view)
            self.meal_planning_view = None