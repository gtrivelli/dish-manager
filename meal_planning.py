from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QSpinBox, QFrame, QRadioButton, QButtonGroup, QStackedWidget, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta
from utilities import load_dishes, load_schedule, save_schedule, find_leftover_chain, remove_leftover_chain, find_next_available_slots

class MealPlanningView(QWidget):
    """View for planning/editing a meal"""
    def __init__(self, scheduler_parent, date, meal_type, existing_meal=None):
        super().__init__()
        self.scheduler_parent = scheduler_parent
        self.date = date
        self.meal_type = meal_type
        self.existing_meal = existing_meal
        
        self.dishes = load_dishes()
        self.schedule_data = load_schedule()
        
        self.setup_ui()
        self.load_existing_data()
        
    def setup_ui(self):
        """Setup the meal planning UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with back button
        header_layout = QHBoxLayout()
        
        back_button = QPushButton("← Back to Scheduler")
        back_button.setProperty("class", "secondary")
        back_button.clicked.connect(self.back_to_scheduler)
        header_layout.addWidget(back_button)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Centered title
        date_obj = datetime.strptime(self.date, "%Y-%m-%d")
        day_name = date_obj.strftime("%A")
        date_display = date_obj.strftime("%B %d, %Y")
        
        title = QLabel(f"Plan {self.meal_type.title()} for {day_name}, {date_display}")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            color: #2c3e50;
            margin: 10px 0px;
            background-color: transparent;
            border: none;
            selection-background-color: transparent;
        """)
        title.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        layout.addWidget(title)
        
        # Main content with proper layouts
        content_frame = QFrame()
        content_frame.setProperty("class", "card")
        content_frame.setMinimumSize(600, 500)
        from PyQt6.QtWidgets import QSizePolicy
        content_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Main content layout
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(40, 30, 40, 30)
        content_layout.setSpacing(20)
        
        # Meal type selection section
        type_section = QWidget()
        type_layout = QVBoxLayout(type_section)
        type_layout.setSpacing(10)
        
        type_label = QLabel("Meal Type:")
        type_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: #2c3e50; 
            background-color: transparent;
            border: none;
            selection-background-color: transparent;
        """)
        type_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        type_layout.addWidget(type_label)
        
        # Radio buttons for meal types with proper layout
        self.meal_type_group = QButtonGroup()
        radio_style = """
            QRadioButton {
                background-color: transparent;
                border: none;
                selection-background-color: transparent;
                color: #2c3e50;
                font-size: 13px;
                spacing: 8px;
                padding: 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
            }
            QRadioButton::indicator:checked {
                background-color: #3498db;
                border-color: #2980b9;
            }
            QRadioButton:hover {
                background-color: #f8f9fa;
                border-radius: 4px;
            }
        """
        
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(30)
        
        self.cook_radio = QRadioButton("Cook a dish")
        self.cook_radio.setChecked(True)
        self.cook_radio.toggled.connect(self.on_meal_type_changed)
        self.cook_radio.setStyleSheet(radio_style)
        self.meal_type_group.addButton(self.cook_radio, 0)
        radio_layout.addWidget(self.cook_radio)
        
        self.bought_radio = QRadioButton("Buy a meal")
        self.bought_radio.toggled.connect(self.on_meal_type_changed)
        self.bought_radio.setStyleSheet(radio_style)
        self.meal_type_group.addButton(self.bought_radio, 1)
        radio_layout.addWidget(self.bought_radio)
        
        self.frozen_radio = QRadioButton("Frozen food")
        self.frozen_radio.toggled.connect(self.on_meal_type_changed)
        self.frozen_radio.setStyleSheet(radio_style)
        self.meal_type_group.addButton(self.frozen_radio, 2)
        radio_layout.addWidget(self.frozen_radio)
        
        self.leftovers_radio = QRadioButton("Eat leftovers")
        self.leftovers_radio.toggled.connect(self.on_meal_type_changed)
        self.leftovers_radio.setStyleSheet(radio_style)
        self.meal_type_group.addButton(self.leftovers_radio, 3)
        radio_layout.addWidget(self.leftovers_radio)
        
        self.none_radio = QRadioButton("No meal planned")
        self.none_radio.setStyleSheet(radio_style)
        self.meal_type_group.addButton(self.none_radio, 4)
        radio_layout.addWidget(self.none_radio)
        
        radio_layout.addStretch()
        type_layout.addLayout(radio_layout)
        content_layout.addWidget(type_section)
        
        # Stacked widget for different meal type sections
        self.content_stack = QStackedWidget()
        
        # COOK SECTION with proper layout
        self.dish_section = QWidget()
        dish_layout = QVBoxLayout(self.dish_section)
        dish_layout.setSpacing(15)
        
        dish_label = QLabel("Select Dish:")
        dish_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        dish_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        dish_layout.addWidget(dish_label)
        
        # Create inline expandable list - no popup focus issues
        from PyQt6.QtWidgets import QListWidget, QScrollArea
        
        class InlineDropdown(QWidget):
            def __init__(self, dishes):
                super().__init__()
                self.dishes = dishes
                self.selected_dish = None
                self.expanded = False
                
                layout = QVBoxLayout(self)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                
                # Dropdown display using QLabel with click handling
                self.button = QLabel("-- Select a dish --")
                self.button.setMinimumHeight(40)
                self.button.setStyleSheet("""
                    QLabel {
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                        padding: 8px 12px;
                        background-color: white;
                        font-size: 13px;
                        color: #2c3e50;
                    }
                    QLabel:hover { border-color: #3498db; }
                """)
                # Make it clickable
                self.button.mousePressEvent = lambda event: self.toggle_list()
                layout.addWidget(self.button)
                
                # Scrollable list
                self.scroll_area = QScrollArea()
                self.scroll_area.setMaximumHeight(150)
                self.scroll_area.setWidgetResizable(True)
                self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                
                self.list_widget = QListWidget()
                self.list_widget.addItem("-- Select a dish --")
                for dish in dishes:
                    self.list_widget.addItem(dish['name'])
                    
                self.list_widget.itemClicked.connect(self.item_selected)
                self.scroll_area.setWidget(self.list_widget)
                layout.addWidget(self.scroll_area)
                
                # Start collapsed
                self.scroll_area.hide()
                
            def toggle_list(self):
                if self.expanded:
                    self.scroll_area.hide()
                    self.expanded = False
                else:
                    self.scroll_area.show()
                    self.expanded = True
                    
            def item_selected(self, item):
                text = item.text()
                self.button.setText(text)
                if text == "-- Select a dish --":
                    self.selected_dish = None
                else:
                    self.selected_dish = text
                self.scroll_area.hide()
                self.expanded = False
                
            def currentData(self):
                return self.selected_dish
                
            def findData(self, dish_name):
                for i in range(self.list_widget.count()):
                    if self.list_widget.item(i).text() == dish_name:
                        return i
                return -1
                
            def setCurrentIndex(self, index):
                if 0 <= index < self.list_widget.count():
                    item = self.list_widget.item(index)
                    self.button.setText(item.text())
                    if item.text() == "-- Select a dish --":
                        self.selected_dish = None
                    else:
                        self.selected_dish = item.text()
        
        self.dish_combo = InlineDropdown(self.dishes)
        dish_layout.addWidget(self.dish_combo)
        
        # Leftover section
        leftover_label = QLabel("Expected leftover meals:")
        leftover_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        leftover_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        dish_layout.addWidget(leftover_label)
        
        leftover_help = QLabel("How many additional meals do you expect from leftovers?")
        leftover_help.setStyleSheet("font-size: 12px; color: #6c757d;")
        leftover_help.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        dish_layout.addWidget(leftover_help)
        
        # Counter controls with proper layout
        counter_layout = QHBoxLayout()
        counter_layout.addStretch()
        
        self.minus_button = QPushButton("−")
        self.minus_button.setFixedSize(30, 30)
        self.minus_button.setProperty("class", "counter-button")
        self.minus_button.clicked.connect(self.decrease_leftover_count)
        counter_layout.addWidget(self.minus_button)
        
        self.leftover_display = QLabel("0")
        self.leftover_display.setFixedSize(50, 30)
        self.leftover_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.leftover_display.setStyleSheet("""
            QLabel {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        self.leftover_display.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        counter_layout.addWidget(self.leftover_display)
        
        self.plus_button = QPushButton("+")
        self.plus_button.setFixedSize(30, 30)
        self.plus_button.setProperty("class", "counter-button")
        self.plus_button.clicked.connect(self.increase_leftover_count)
        counter_layout.addWidget(self.plus_button)
        
        counter_layout.addStretch()
        dish_layout.addLayout(counter_layout)
        dish_layout.addStretch()
        
        self.leftover_count = 0
        self.content_stack.addWidget(self.dish_section)
        
        # BOUGHT SECTION with proper layout
        self.bought_section = QWidget()
        bought_layout = QVBoxLayout(self.bought_section)
        bought_layout.setSpacing(15)
        
        bought_label = QLabel("Meal Description:")
        bought_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        bought_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        bought_layout.addWidget(bought_label)
        
        bought_help = QLabel("Enter a description of the meal you're planning to buy:")
        bought_help.setStyleSheet("font-size: 12px; color: #6c757d;")
        bought_help.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        bought_layout.addWidget(bought_help)
        
        from PyQt6.QtWidgets import QLineEdit
        self.bought_input = QLineEdit()
        self.bought_input.setPlaceholderText("e.g., Pizza from Tony's, Chinese takeout...")
        self.bought_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px 12px;
                background-color: white;
                font-size: 13px;
                min-height: 20px;
            }
            QLineEdit:hover { border-color: #3498db; }
            QLineEdit:focus { border-color: #3498db; }
        """)
        bought_layout.addWidget(self.bought_input)
        bought_layout.addStretch()
        self.content_stack.addWidget(self.bought_section)
        
        # FROZEN SECTION with proper layout  
        self.frozen_section = QWidget()
        frozen_layout = QVBoxLayout(self.frozen_section)
        frozen_layout.setSpacing(15)
        
        frozen_label = QLabel("Frozen Food Description:")
        frozen_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        frozen_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        frozen_layout.addWidget(frozen_label)
        
        frozen_help = QLabel("Enter a description of the frozen food:")
        frozen_help.setStyleSheet("font-size: 12px; color: #6c757d;")
        frozen_help.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        frozen_layout.addWidget(frozen_help)
        
        self.frozen_input = QLineEdit()
        self.frozen_input.setPlaceholderText("e.g., Frozen pizza, Lean Cuisine meal, frozen stir-fry...")
        self.frozen_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px 12px;
                background-color: white;
                font-size: 13px;
                min-height: 20px;
            }
            QLineEdit:hover { border-color: #3498db; }
            QLineEdit:focus { border-color: #3498db; }
        """)
        frozen_layout.addWidget(self.frozen_input)
        frozen_layout.addStretch()
        self.content_stack.addWidget(self.frozen_section)
        
        # LEFTOVERS SECTION with proper layout
        self.leftovers_section = QWidget()
        leftovers_layout = QVBoxLayout(self.leftovers_section)
        leftovers_layout.setSpacing(15)
        
        leftovers_label = QLabel("Select Leftover Dish:")
        leftovers_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        leftovers_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        leftovers_layout.addWidget(leftovers_label)
        
        leftovers_help = QLabel("Choose from dishes that were recently cooked:")
        leftovers_help.setStyleSheet("font-size: 12px; color: #6c757d;")
        leftovers_help.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        leftovers_layout.addWidget(leftovers_help)
        
        # Create leftover selection dropdown
        class LeftoverDropdown(QWidget):
            def __init__(self, schedule_data, current_date):
                super().__init__()
                self.schedule_data = schedule_data
                self.current_date = current_date
                self.selected_leftover = None
                
                layout = QVBoxLayout(self)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                
                # Dropdown display using QLabel with click handling
                self.button = QLabel("-- Select leftover dish --")
                self.button.setMinimumHeight(40)
                self.button.setStyleSheet("""
                    QLabel {
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                        padding: 8px 12px;
                        background-color: white;
                        font-size: 13px;
                        color: #2c3e50;
                    }
                    QLabel:hover { border-color: #3498db; }
                """)
                # Make it clickable
                self.button.mousePressEvent = lambda event: self.toggle_list()
                layout.addWidget(self.button)
                
                # Scrollable list
                self.scroll_area = QScrollArea()
                self.scroll_area.setMaximumHeight(150)
                self.scroll_area.setWidgetResizable(True)
                self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                
                self.list_widget = QListWidget()
                self.populate_leftover_options()
                    
                self.list_widget.itemClicked.connect(self.item_selected)
                self.scroll_area.setWidget(self.list_widget)
                layout.addWidget(self.scroll_area)
                
                # Start collapsed
                self.scroll_area.hide()
                self.expanded = False
                
            def populate_leftover_options(self):
                """Find available leftover dishes from recent cook meals"""
                self.list_widget.clear()
                self.list_widget.addItem("-- Select leftover dish --")
                
                # Look for cook meals in the past 7 days that have leftovers
                current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
                leftover_options = []
                
                if "schedule" in self.schedule_data:
                    for date_str, meals in self.schedule_data["schedule"].items():
                        try:
                            meal_date = datetime.strptime(date_str, "%Y-%m-%d")
                            days_ago = (current_date_obj - meal_date).days
                            
                            # Include meals from past 7 days
                            if 0 <= days_ago <= 7:
                                for meal_type, meal_data in meals.items():
                                    if meal_data.get("type") == "cook":
                                        dish_name = meal_data.get("dish_name")
                                        leftover_id = meal_data.get("leftover_id")
                                        if dish_name and leftover_id:
                                            display_text = f"{dish_name} (cooked {date_str})"
                                            leftover_options.append({
                                                "display": display_text,
                                                "dish_name": dish_name,
                                                "leftover_id": leftover_id,
                                                "cooked_date": date_str
                                            })
                        except ValueError:
                            continue
                
                # Sort by date (most recent first)
                leftover_options.sort(key=lambda x: x["cooked_date"], reverse=True)
                
                for option in leftover_options:
                    self.list_widget.addItem(option["display"])
                    
            def toggle_list(self):
                if self.expanded:
                    self.scroll_area.hide()
                    self.expanded = False
                else:
                    self.scroll_area.show()
                    self.expanded = True
                    
            def item_selected(self, item):
                text = item.text()
                self.button.setText(text)
                if text == "-- Select leftover dish --":
                    self.selected_leftover = None
                else:
                    # Parse the selected leftover
                    for i in range(self.list_widget.count()):
                        if self.list_widget.item(i).text() == text:
                            # Find the corresponding leftover data
                            current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
                            if "schedule" in self.schedule_data:
                                for date_str, meals in self.schedule_data["schedule"].items():
                                    try:
                                        meal_date = datetime.strptime(date_str, "%Y-%m-%d")
                                        days_ago = (current_date_obj - meal_date).days
                                        
                                        if 0 <= days_ago <= 7:
                                            for meal_type, meal_data in meals.items():
                                                if (meal_data.get("type") == "cook" and 
                                                    f"{meal_data.get('dish_name')} (cooked {date_str})" == text):
                                                    self.selected_leftover = {
                                                        "dish_name": meal_data.get("dish_name"),
                                                        "leftover_id": meal_data.get("leftover_id"),
                                                        "cooked_date": date_str
                                                    }
                                                    break
                                    except ValueError:
                                        continue
                            break
                            
                self.scroll_area.hide()
                self.expanded = False
                
            def get_selected_leftover(self):
                return self.selected_leftover
        
        self.leftover_combo = LeftoverDropdown(self.schedule_data, self.date)
        leftovers_layout.addWidget(self.leftover_combo)
        leftovers_layout.addStretch()
        self.content_stack.addWidget(self.leftovers_section)
        
        # NONE SECTION with proper layout
        self.none_section = QWidget()
        none_layout = QVBoxLayout(self.none_section)
        none_layout.addStretch()
        
        none_label = QLabel("No meal planned")
        none_label.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: #6c757d;
            background-color: transparent;
            border: none;
            selection-background-color: transparent;
        """)
        none_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        none_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        none_layout.addWidget(none_label)
        
        none_help = QLabel("This meal slot will remain empty.")
        none_help.setStyleSheet("""
            font-size: 12px; 
            color: #adb5bd;
            background-color: transparent;
            border: none;
            selection-background-color: transparent;
        """)
        none_help.setAlignment(Qt.AlignmentFlag.AlignCenter)
        none_help.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        none_layout.addWidget(none_help)
        none_layout.addStretch()
        self.content_stack.addWidget(self.none_section)
        
        # Add the content stack to main layout
        content_layout.addWidget(self.content_stack, 1)
        
        # Button section with proper layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumSize(120, 40)
        cancel_button.setProperty("class", "secondary")
        cancel_button.clicked.connect(self.back_to_scheduler)
        button_layout.addWidget(cancel_button)
        
        button_layout.addSpacing(20)  # 20px gap between buttons
        
        # Add delete button if editing existing meal
        if self.existing_meal:
            delete_button = QPushButton("Delete Meal")
            delete_button.setMinimumSize(120, 40)
            delete_button.setProperty("class", "danger")
            delete_button.clicked.connect(self.delete_meal)
            button_layout.addWidget(delete_button)
            button_layout.addSpacing(20)
        
        self.save_button = QPushButton("Save Meal")
        self.save_button.setMinimumSize(120, 40)
        self.save_button.clicked.connect(self.save_meal)
        button_layout.addWidget(self.save_button)
        
        button_layout.addStretch()
        content_layout.addLayout(button_layout)
        
        # Center the content frame
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(content_frame)
        center_layout.addStretch()
        
        layout.addLayout(center_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def on_meal_type_changed(self):
        """Handle meal type radio button changes"""
        if self.cook_radio.isChecked():
            self.content_stack.setCurrentWidget(self.dish_section)
        elif self.bought_radio.isChecked():
            self.content_stack.setCurrentWidget(self.bought_section)
        elif self.frozen_radio.isChecked():
            self.content_stack.setCurrentWidget(self.frozen_section)
        elif self.leftovers_radio.isChecked():
            self.content_stack.setCurrentWidget(self.leftovers_section)
        else:  # No meal planned
            self.content_stack.setCurrentWidget(self.none_section)
            
    def load_existing_data(self):
        """Load existing meal data if editing"""
        if self.existing_meal:
            meal_type = self.existing_meal.get("type", "none")
            
            if meal_type == "cook":
                self.cook_radio.setChecked(True)
                dish_name = self.existing_meal.get("dish_name")
                if dish_name:
                    # Find and set the dish in standard combo box
                    index = self.dish_combo.findData(dish_name)
                    if index >= 0:
                        self.dish_combo.setCurrentIndex(index)
                        
                leftover_meals = self.existing_meal.get("leftover_meals", 0)
                self.set_leftover_count(leftover_meals)
            elif meal_type == "bought":
                self.bought_radio.setChecked(True)
                description = self.existing_meal.get("description", "")
                self.bought_input.setText(description)
            elif meal_type == "frozen":
                self.frozen_radio.setChecked(True)
                description = self.existing_meal.get("description", "")
                self.frozen_input.setText(description)
            elif meal_type == "leftovers":
                self.leftovers_radio.setChecked(True)
                # Set the leftover selection if available
                dish_name = self.existing_meal.get("dish_name")
                cooked_date = self.existing_meal.get("cooked_date")
                if dish_name and cooked_date:
                    # Update the leftover combo display
                    display_text = f"{dish_name} (cooked {cooked_date})"
                    self.leftover_combo.button.setText(display_text)
                    self.leftover_combo.selected_leftover = {
                        "dish_name": dish_name,
                        "leftover_id": self.existing_meal.get("leftover_id"),
                        "cooked_date": cooked_date
                    }
            else:
                self.none_radio.setChecked(True)
                
            self.on_meal_type_changed()
            
    def save_meal(self):
        """Save the planned meal"""
        # Check if we're editing an existing meal that has leftovers
        old_leftover_id = None
        if self.existing_meal and self.existing_meal.get("type") == "cook":
            old_leftover_id = self.existing_meal.get("leftover_id")
        
        # Determine meal type
        if self.cook_radio.isChecked():
            dish_name = self.dish_combo.currentData()
            if not dish_name:
                # TODO: Show error message
                return
                
            leftover_meals = self.leftover_count
            
            # Create meal data
            meal_data = {
                "type": "cook",
                "dish_name": dish_name,
                "leftover_meals": leftover_meals,
                "leftover_id": f"{dish_name.lower().replace(' ', '-')}-{self.date}"
            }
        elif self.bought_radio.isChecked():
            description = self.bought_input.text().strip()
            if not description:
                # TODO: Show error message
                return
                
            meal_data = {
                "type": "bought",
                "description": description
            }
        elif self.frozen_radio.isChecked():
            description = self.frozen_input.text().strip()
            if not description:
                # TODO: Show error message
                return
                
            meal_data = {
                "type": "frozen",
                "description": description
            }
        elif self.leftovers_radio.isChecked():
            selected_leftover = self.leftover_combo.get_selected_leftover()
            if not selected_leftover:
                # TODO: Show error message
                return
                
            meal_data = {
                "type": "leftovers",
                "dish_name": selected_leftover["dish_name"],
                "leftover_id": selected_leftover["leftover_id"],
                "cooked_date": selected_leftover["cooked_date"]
            }
        else:
            meal_data = {
                "type": "none"
            }
        
        # Handle schedule interruption - remove old leftovers if changing from cook meal
        if old_leftover_id and old_leftover_id != meal_data.get("leftover_id"):
            removed_count = remove_leftover_chain(self.schedule_data, old_leftover_id)
            if removed_count > 0:
                # Could show user notification here: f"Removed {removed_count} leftover meals"
                pass
        
        # Save to schedule
        if "schedule" not in self.schedule_data:
            self.schedule_data["schedule"] = {}
            
        if self.date not in self.schedule_data["schedule"]:
            self.schedule_data["schedule"][self.date] = {}
            
        self.schedule_data["schedule"][self.date][self.meal_type] = meal_data
        
        # Handle leftover placement for cook meals
        if meal_data.get("type") == "cook" and meal_data.get("leftover_meals", 0) > 0:
            self.place_leftovers(meal_data)
        
        save_schedule(self.schedule_data)
        self.back_to_scheduler()
        
    def place_leftovers(self, cooked_meal):
        """Place leftover meals in subsequent slots (Phase 2 preview)"""
        leftover_count = cooked_meal.get("leftover_meals", 0)
        dish_name = cooked_meal.get("dish_name")
        leftover_id = cooked_meal.get("leftover_id")
        
        if leftover_count <= 0:
            return
            
        # Find next available slots
        start_date = datetime.strptime(self.date, "%Y-%m-%d")
        placed_count = 0
        
        # Start from the next meal (if current is lunch, try dinner same day, then next day)
        current_date = start_date
        current_meal_types = ["lunch", "dinner"]
        current_meal_index = current_meal_types.index(self.meal_type)
        
        # Start from next meal slot
        if current_meal_index < len(current_meal_types) - 1:
            next_meal_type = current_meal_types[current_meal_index + 1]
        else:
            current_date += timedelta(days=1)
            next_meal_type = current_meal_types[0]
            
        while placed_count < leftover_count and current_date <= start_date + timedelta(days=14):
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Check if slot is available
            if (date_str not in self.schedule_data["schedule"] or 
                next_meal_type not in self.schedule_data["schedule"][date_str]):
                
                # Place leftover
                if date_str not in self.schedule_data["schedule"]:
                    self.schedule_data["schedule"][date_str] = {}
                    
                self.schedule_data["schedule"][date_str][next_meal_type] = {
                    "type": "leftovers",
                    "dish_name": dish_name,
                    "cooked_date": self.date,
                    "leftover_id": leftover_id
                }
                
                placed_count += 1
            
            # Move to next slot
            if next_meal_type == "lunch":
                next_meal_type = "dinner"
            else:
                next_meal_type = "lunch"
                current_date += timedelta(days=1)
                
    def increase_leftover_count(self):
        """Increase leftover count"""
        if self.leftover_count < 10:
            self.leftover_count += 1
            self.leftover_display.setText(str(self.leftover_count))
            
    def decrease_leftover_count(self):
        """Decrease leftover count"""
        if self.leftover_count > 0:
            self.leftover_count -= 1
            self.leftover_display.setText(str(self.leftover_count))
            
    def set_leftover_count(self, count):
        """Set leftover count to specific value"""
        self.leftover_count = max(0, min(10, count))
        self.leftover_display.setText(str(self.leftover_count))
    
    def delete_meal(self):
        """Delete the current meal with impact warnings"""
        if not self.existing_meal:
            return
            
        # Check if this is a cook meal with leftovers
        leftover_id = self.existing_meal.get("leftover_id")
        impact_message = ""
        
        if leftover_id and self.existing_meal.get("type") == "cook":
            # Find associated leftovers
            leftover_chain = find_leftover_chain(self.schedule_data, leftover_id)
            if leftover_chain:
                impact_message = f"\nThis will also remove {len(leftover_chain)} scheduled leftover meal(s)."
        
        # Show in-window confirmation dialog
        self.show_delete_confirmation(impact_message)
    
    def show_delete_confirmation(self, impact_message):
        """Show confirmation dialog within the window"""
        # Create overlay widget
        overlay = QWidget(self)
        overlay.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 100);
            }
        """)
        overlay.setGeometry(0, 0, self.width(), self.height())
        
        # Create confirmation dialog
        dialog_frame = QFrame(overlay)
        dialog_frame.setFixedSize(400, 200)
        dialog_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        # Center the dialog
        dialog_frame.move(
            (overlay.width() - dialog_frame.width()) // 2,
            (overlay.height() - dialog_frame.height()) // 2
        )
        
        dialog_layout = QVBoxLayout(dialog_frame)
        dialog_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Delete Meal")
        title_label.setStyleSheet("""
            color: black; 
            font-size: 16px; 
            font-weight: bold;
            background: none;
            border: none;
            padding: 0px;
            margin: 0px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        dialog_layout.addWidget(title_label)
        
        # Message
        message_label = QLabel(f"Are you sure you want to delete this meal?{impact_message}")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("""
            color: black; 
            font-size: 14px;
            background: none;
            border: none;
            padding: 0px;
            margin: 0px;
        """)
        message_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        message_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        dialog_layout.addWidget(message_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.setMinimumSize(100, 40)
        cancel_btn.clicked.connect(lambda: overlay.deleteLater())
        button_layout.addWidget(cancel_btn)
        
        button_layout.addSpacing(10)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("class", "danger")
        delete_btn.setMinimumSize(100, 40)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        delete_btn.clicked.connect(lambda: self.confirm_delete(overlay))
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        dialog_layout.addLayout(button_layout)
        
        overlay.show()
        
    def confirm_delete(self, overlay):
        """Execute the deletion after confirmation"""
        overlay.deleteLater()
        
        # Get leftover_id before deletion
        leftover_id = self.existing_meal.get("leftover_id") if self.existing_meal else None
        
        # Remove the meal
        if (self.date in self.schedule_data.get("schedule", {}) and 
            self.meal_type in self.schedule_data["schedule"][self.date]):
            del self.schedule_data["schedule"][self.date][self.meal_type]
            
            # Clean up empty date entry
            if not self.schedule_data["schedule"][self.date]:
                del self.schedule_data["schedule"][self.date]
        
        # Remove associated leftovers if any
        if leftover_id:
            remove_leftover_chain(self.schedule_data, leftover_id)
        
        save_schedule(self.schedule_data)
        self.back_to_scheduler()
    
    def back_to_scheduler(self):
        """Return to scheduler view"""
        self.scheduler_parent.show_scheduler_view()