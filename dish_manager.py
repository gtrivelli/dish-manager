from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QLineEdit, QLabel, QTextEdit, QStackedWidget, QFrame, QListWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from utilities import load_dishes, save_dishes

DATA_FILE = "dishes.json"

class DishWidget(QWidget):
    def __init__(self, dish_data):
        super().__init__()
        self.dish_data = dish_data
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedHeight(32)  # Fixed height for consistent list appearance
        
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 6, 12, 6)  # More breathing room
        layout.setSpacing(12)
        
        # Dish name - prominent
        name_label = QLabel(self.dish_data['name'])
        name_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-weight: 600;
                font-size: 13px;
                background-color: transparent;
                border: none;
            }
        """)
        name_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Remove focus highlights
        layout.addWidget(name_label, 0, Qt.AlignmentFlag.AlignVCenter)  # Center vertically
        
        # Tags - subtle and gray
        if self.dish_data['tags']:
            tags_text = ", ".join(sorted(self.dish_data['tags']))
            tags_label = QLabel(tags_text)
            tags_label.setStyleSheet("""
                QLabel {
                    color: #6c757d;
                    font-weight: 400;
                    font-size: 12px;
                    font-style: italic;
                    background-color: transparent;
                    border: none;
                }
            """)
            tags_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Remove focus highlights
            layout.addWidget(tags_label, 0, Qt.AlignmentFlag.AlignVCenter)  # Center vertically
        
        layout.addStretch()  # Push everything to the left
        self.setLayout(layout)

class DishManager(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Dish Manager")
        self.setMinimumSize(900, 650)
        self.current_dish_index = None
        
        # Apply modern styling
        self.apply_modern_styling()
        
        # Force application to use system cursor by setting it explicitly
        from PyQt6.QtGui import QCursor
        from PyQt6.QtCore import Qt
        
        # Set the application cursor to default system arrow
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        
        # Create main layout with padding
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(0)
        
        # Create stacked widget to switch between views
        self.stacked_widget = QStackedWidget()
        
        # Create the two views
        self.setup_list_view()
        self.setup_edit_view()
        
        # Add stacked widget to main layout
        self.main_layout.addWidget(self.stacked_widget)
        self.setLayout(self.main_layout)
        
        # Start with list view
        self.show_list_view()
        
    def apply_modern_styling(self):
        """Apply modern, clean styling to the application"""
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
            
            /* Search input styling */
            QLineEdit {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
                background-color: white;
                selection-background-color: #3498db;
            }
            
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }
            
            /* Dish list styling - compact and clean */
            QListWidget {
                border: 2px solid #e9ecef;
                border-radius: 12px;
                background-color: white;
                alternate-background-color: #f8f9fa;
                font-size: 13px;
                padding: 4px;
            }
            
            /* Note: Qt doesn't support partial text styling within list items,
               so we use subtle separators and spacing to distinguish tags */
            
            QListWidget::item {
                border: none;
                padding: 6px 12px;
                margin: 0px;
                border-radius: 4px;
                background-color: transparent;
                border-bottom: 1px solid #f1f3f4;
            }
            
            QListWidget::item:hover {
                background-color: #f1f8ff;
                border: 1px solid #cce7ff;
            }
            
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                border: 1px solid #2196f3;
            }
            
            /* Modern scrollbar styling */
            QListWidget QScrollBar:vertical {
                background-color: #f8f9fa;
                width: 12px;
                border: none;
                border-radius: 6px;
                margin: 0px;
            }
            
            QListWidget QScrollBar::handle:vertical {
                background-color: #dee2e6;
                border: none;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            
            QListWidget QScrollBar::handle:vertical:pressed {
                background-color: #6c757d;
            }
            
            QListWidget QScrollBar::add-line:vertical,
            QListWidget QScrollBar::sub-line:vertical {
                height: 0px;
                border: none;
            }
            
            QListWidget QScrollBar::add-page:vertical,
            QListWidget QScrollBar::sub-page:vertical {
                background: none;
            }
            
            /* Also style scrollbars in text areas */
            QTextEdit QScrollBar:vertical {
                background-color: #f8f9fa;
                width: 12px;
                border: none;
                border-radius: 6px;
                margin: 0px;
            }
            
            QTextEdit QScrollBar::handle:vertical {
                background-color: #dee2e6;
                border: none;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            
            QTextEdit QScrollBar::handle:vertical:pressed {
                background-color: #6c757d;
            }
            
            QTextEdit QScrollBar::add-line:vertical,
            QTextEdit QScrollBar::sub-line:vertical {
                height: 0px;
                border: none;
            }
            
            QTextEdit QScrollBar::add-page:vertical,
            QTextEdit QScrollBar::sub-page:vertical {
                background: none;
            }
            
            /* Button styling */
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
            
            QPushButton[class="danger"] {
                background-color: #e74c3c;
            }
            
            QPushButton[class="danger"]:hover {
                background-color: #c0392b;
            }
            
            QPushButton[class="success"] {
                background-color: #28a745;
            }
            
            QPushButton[class="success"]:hover {
                background-color: #218838;
            }
            
            /* Text area styling */
            QTextEdit {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
                background-color: white;
                line-height: 1.4;
            }
            
            QTextEdit:focus {
                border-color: #3498db;
            }
            
            /* Only style frames that need visual separation */
            QFrame[class="card"] {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
    def setup_list_view(self):
        """Create the dish list view"""
        self.list_widget = QWidget()
        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(15, 15, 15, 15)
        list_layout.setSpacing(15)
        
        # Search input directly in main layout
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search dishes by name or tag...")
        self.filter_input.textChanged.connect(self.filter_dishes)
        list_layout.addWidget(self.filter_input)
        
        # Dish list directly in main layout
        self.dish_list = QListWidget()
        self.dish_list.itemDoubleClicked.connect(self.edit_selected_dish)
        self.dish_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Remove native focus highlight
        list_layout.addWidget(self.dish_list)
        
        # Buttons directly in main layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.add_button = QPushButton("+ Add New Dish")
        self.add_button.setProperty("class", "success")
        self.add_button.clicked.connect(self.show_add_view)
        button_layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.setProperty("class", "danger")
        self.remove_button.clicked.connect(self.remove_dish)
        button_layout.addWidget(self.remove_button)
        
        # Add spacer to push buttons to the left
        button_layout.addStretch()
        
        list_layout.addLayout(button_layout)
        
        self.list_widget.setLayout(list_layout)
        self.stacked_widget.addWidget(self.list_widget)
        
    def setup_edit_view(self):
        """Create the edit/add dish view"""
        self.edit_widget = QWidget()
        edit_layout = QVBoxLayout()
        edit_layout.setContentsMargins(0, 0, 0, 0)
        edit_layout.setSpacing(20)
        
        # Header section - direct layout, no frame
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(15, 15, 15, 10)
        
        back_button = QPushButton("← Back to List")
        back_button.setProperty("class", "secondary")
        back_button.clicked.connect(self.show_list_view)
        header_layout.addWidget(back_button)
        
        header_layout.addStretch()
        
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        
        header_layout.addStretch()
        
        edit_layout.addLayout(header_layout)
        
        # Content layout with proper cards
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(20)
        
        # Left column - Dish info in a card
        left_frame = QFrame()
        left_frame.setProperty("class", "card")
        left_frame.setMinimumWidth(400)  # More width for all inputs
        left_frame.setMinimumHeight(600)  # Ensure adequate height
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(8)  # Tighter spacing to fit everything
        
        # Section header
        info_header = QLabel("Dish Information")
        info_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; background-color: transparent; border: none;")
        info_header.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        left_layout.addWidget(info_header)
        
        # Dish name
        name_label = QLabel("Dish Name:")
        name_label.setStyleSheet("color: #6c757d; font-size: 12px; margin-bottom: 5px; background-color: transparent; border: none;")
        name_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        left_layout.addWidget(name_label)
        
        self.dish_name_input = QLineEdit()
        self.dish_name_input.setPlaceholderText("Enter the name of your dish...")
        left_layout.addWidget(self.dish_name_input)
        
        # Tags section
        tags_label = QLabel("Tags:")
        tags_label.setStyleSheet("color: #6c757d; font-size: 12px; margin-bottom: 5px; margin-top: 10px; background-color: transparent; border: none;")
        tags_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        left_layout.addWidget(tags_label)
        
        # Tag input with modern styling
        tag_input_layout = QHBoxLayout()
        tag_input_layout.setSpacing(10)
        
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Add a tag")
        self.tag_input.returnPressed.connect(self.add_tag)
        tag_input_layout.addWidget(self.tag_input)
        
        add_tag_button = QPushButton("Add")
        add_tag_button.setMaximumWidth(60)
        add_tag_button.clicked.connect(self.add_tag)
        tag_input_layout.addWidget(add_tag_button)
        
        left_layout.addLayout(tag_input_layout)
        
        # Tags list with instruction
        tags_instruction = QLabel("Double-click a tag to remove it")
        tags_instruction.setStyleSheet("color: #6c757d; font-size: 11px; margin-bottom: 5px; background-color: transparent; border: none;")
        tags_instruction.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        left_layout.addWidget(tags_instruction)
        
        self.tags_list = QListWidget()
        self.tags_list.itemDoubleClicked.connect(self.remove_tag)
        self.tags_list.setFixedHeight(80)  # Fixed height to prevent overlap
        self.tags_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Remove focus highlights
        left_layout.addWidget(self.tags_list)
        
        # Ingredients section
        ingredients_label = QLabel("Ingredients:")
        ingredients_label.setStyleSheet("color: #6c757d; font-size: 12px; margin-bottom: 5px; margin-top: 10px; background-color: transparent; border: none;")
        ingredients_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        left_layout.addWidget(ingredients_label)
        
        # Ingredient input with amount
        ingredient_input_layout = QHBoxLayout()
        ingredient_input_layout.setSpacing(5)
        
        self.ingredient_input = QLineEdit()
        self.ingredient_input.setPlaceholderText("Ingredient name")
        self.ingredient_input.returnPressed.connect(self.add_ingredient)
        ingredient_input_layout.addWidget(self.ingredient_input)
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        self.amount_input.setMaximumWidth(80)
        self.amount_input.returnPressed.connect(self.add_ingredient)
        ingredient_input_layout.addWidget(self.amount_input)
        
        add_ingredient_button = QPushButton("Add")
        add_ingredient_button.setMaximumWidth(60)
        add_ingredient_button.clicked.connect(self.add_ingredient)
        ingredient_input_layout.addWidget(add_ingredient_button)
        
        left_layout.addLayout(ingredient_input_layout)
        
        # Ingredients list with instruction
        ingredients_instruction = QLabel("Double-click an ingredient to remove it")
        ingredients_instruction.setStyleSheet("color: #6c757d; font-size: 11px; margin-bottom: 5px; background-color: transparent; border: none;")
        ingredients_instruction.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        left_layout.addWidget(ingredients_instruction)
        
        self.ingredients_list = QListWidget()
        self.ingredients_list.itemDoubleClicked.connect(self.remove_ingredient)
        self.ingredients_list.setFixedHeight(80)  # Fixed height to prevent overlap
        self.ingredients_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Remove focus highlights
        left_layout.addWidget(self.ingredients_list)
        
        # Add stretch to push everything up
        left_layout.addStretch()
        
        left_frame.setLayout(left_layout)
        content_layout.addWidget(left_frame)
        
        # Right column - Recipe in a card
        right_frame = QFrame()
        right_frame.setProperty("class", "card")
        right_frame.setMinimumWidth(350)  # Ensure recipe area has adequate width
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(12)
        
        # Section header
        recipe_header = QLabel("Recipe Instructions")
        recipe_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; background-color: transparent; border: none;")
        recipe_header.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        right_layout.addWidget(recipe_header)
        
        recipe_label = QLabel("Instructions:")
        recipe_label.setStyleSheet("color: #6c757d; font-size: 12px; margin-bottom: 5px; background-color: transparent; border: none;")
        recipe_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        right_layout.addWidget(recipe_label)
        
        self.recipe_input = QTextEdit()
        self.recipe_input.setPlaceholderText("Enter detailed cooking instructions here...")
        right_layout.addWidget(self.recipe_input)
        
        right_frame.setLayout(right_layout)
        content_layout.addWidget(right_frame)
        
        edit_layout.addLayout(content_layout)
        
        # Action buttons directly in layout
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(15, 10, 15, 15)
        action_layout.setSpacing(15)
        
        action_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setProperty("class", "secondary")
        self.cancel_button.clicked.connect(self.show_list_view)
        action_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("Save Dish")
        self.save_button.clicked.connect(self.save_dish)
        action_layout.addWidget(self.save_button)
        
        edit_layout.addLayout(action_layout)
        
        self.edit_widget.setLayout(edit_layout)
        self.stacked_widget.addWidget(self.edit_widget)
        
    def load_dish_list(self):
        """Load and display all dishes"""
        self.dish_list.clear()
        self.dishes = load_dishes()
        self.dishes.sort(key=lambda x: x["name"].lower())
        
        for dish in self.dishes:
            # Create custom widget for this dish
            dish_widget = DishWidget(dish)
            
            # Create list item
            item = QListWidgetItem()
            item.setSizeHint(dish_widget.size())  # Use actual size instead of sizeHint
            item.setData(Qt.ItemDataRole.UserRole, dish)
            
            # Add to list
            self.dish_list.addItem(item)
            self.dish_list.setItemWidget(item, dish_widget)
            
    def filter_dishes(self):
        """Filter dishes based on search input"""
        filter_text = self.filter_input.text().lower()
        
        if not filter_text:
            self.load_dish_list()
            return
            
        self.dish_list.clear()
        
        for dish in self.dishes:
            # Search in dish name OR in any tag
            name_match = filter_text in dish["name"].lower()
            tag_match = any(filter_text in tag.lower() for tag in dish["tags"])
            
            if name_match or tag_match:
                # Create custom widget for this dish
                dish_widget = DishWidget(dish)
                
                # Create list item
                item = QListWidgetItem()
                item.setSizeHint(dish_widget.size())  # Use actual size instead of sizeHint
                item.setData(Qt.ItemDataRole.UserRole, dish)
                
                # Add to list
                self.dish_list.addItem(item)
                self.dish_list.setItemWidget(item, dish_widget)
                
    def show_list_view(self):
        """Switch to list view"""
        self.load_dish_list()
        self.stacked_widget.setCurrentWidget(self.list_widget)
        
    def show_add_view(self):
        """Switch to add dish view"""
        self.current_dish_index = None
        self.save_button.setText("Create Dish")
        
        # Clear all inputs
        self.dish_name_input.clear()
        self.tag_input.clear()
        self.tags_list.clear()
        self.ingredient_input.clear()
        self.amount_input.clear()
        self.ingredients_list.clear()
        self.recipe_input.clear()
        
        self.stacked_widget.setCurrentWidget(self.edit_widget)
        self.dish_name_input.setFocus()
        
    def edit_selected_dish(self, item):
        """Switch to edit view for selected dish"""
        # Get dish data from the item
        dish_data = item.data(Qt.ItemDataRole.UserRole)
        
        # Find dish index
        dish_index = None
        for i, dish in enumerate(self.dishes):
            if dish['name'] == dish_data['name']:
                dish_index = i
                break
                
        if dish_index is not None:
            self.show_edit_view(dish_index)
            
    def show_edit_view(self, dish_index):
        """Switch to edit view for specific dish"""
        self.current_dish_index = dish_index
        dish = self.dishes[dish_index]

        self.save_button.setText("Save Changes")
        
        # Populate inputs
        self.dish_name_input.setText(dish['name'])
        self.tag_input.clear()
        self.tags_list.clear()
        self.ingredient_input.clear()
        self.amount_input.clear()
        self.ingredients_list.clear()
        
        for tag in dish['tags']:
            self.tags_list.addItem(tag)
            
        # Load ingredients (handle legacy dishes without ingredients)
        for ingredient in dish.get('ingredients', []):
            self.ingredients_list.addItem(ingredient)
            
        self.recipe_input.setPlainText(dish.get('recipe', ''))
        
        self.stacked_widget.setCurrentWidget(self.edit_widget)
        self.dish_name_input.setFocus()
        
    def add_tag(self):
        """Add tag to current dish"""
        tag = self.tag_input.text().strip()
        if tag:
            # Check if tag already exists
            existing_tags = [self.tags_list.item(i).text() for i in range(self.tags_list.count())]
            if tag not in existing_tags:
                self.tags_list.addItem(tag)
                self.tag_input.clear()
                
    def remove_tag(self, item):
        """Remove tag from current dish"""
        row = self.tags_list.row(item)
        self.tags_list.takeItem(row)
        
    def add_ingredient(self):
        """Add ingredient to current dish"""
        ingredient_name = self.ingredient_input.text().strip()
        amount = self.amount_input.text().strip()
        
        # Both ingredient name and amount are required
        if ingredient_name and amount:
            display_text = f"{amount} - {ingredient_name}"
            
            # Check if ingredient already exists
            existing_ingredients = [self.ingredients_list.item(i).text() for i in range(self.ingredients_list.count())]
            if display_text not in existing_ingredients:
                self.ingredients_list.addItem(display_text)
                self.ingredient_input.clear()
                self.amount_input.clear()
                
    def remove_ingredient(self, item):
        """Remove ingredient from current dish"""
        row = self.ingredients_list.row(item)
        self.ingredients_list.takeItem(row)
        
    def save_dish(self):
        """Save the current dish (add or edit)"""
        name = self.dish_name_input.text().strip()
        if not name:
            return  # Could add error message here
            
        # Collect tags
        tags = [self.tags_list.item(i).text() for i in range(self.tags_list.count())]
        
        # Collect ingredients
        ingredients = [self.ingredients_list.item(i).text() for i in range(self.ingredients_list.count())]
        
        # Get recipe
        recipe = self.recipe_input.toPlainText().strip()
        
        # Create dish object
        dish_data = {
            "name": name,
            "tags": tags,
            "ingredients": ingredients,
            "recipe": recipe
        }
        
        if self.current_dish_index is None:
            # Adding new dish
            self.dishes.append(dish_data)
        else:
            # Editing existing dish
            self.dishes[self.current_dish_index] = dish_data
            
        # Save to file and return to list view
        save_dishes(self.dishes)
        self.show_list_view()
        
    def remove_dish(self):
        """Remove selected dish from list"""
        selected_items = self.dish_list.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            # Get dish data from the item
            dish_data = item.data(Qt.ItemDataRole.UserRole)
            dish_name = dish_data['name']
            
            # Show confirmation dialog
            reply = QMessageBox.question(
                self, 
                "Confirm Removal", 
                f"Are you sure you want to remove {dish_name}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Find and remove dish
                for i, dish in enumerate(self.dishes):
                    if dish['name'] == dish_name:
                        del self.dishes[i]
                        break
                        
        save_dishes(self.dishes)
        self.load_dish_list()

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = DishManager()
    window.show()
    sys.exit(app.exec())