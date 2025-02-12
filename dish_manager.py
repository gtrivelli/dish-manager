from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QLineEdit, QLabel
from components import TagComponent, EditDishModal, AddDishModal
from utilities import load_dishes, save_dishes

DATA_FILE = "dishes.json"

class DishManager(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Dish Manager")
        self.setMinimumSize(800, 400)
        self.layout = QVBoxLayout()
        self.modal = None

        self.label = QLabel("Filter by tag:")
        self.layout.addWidget(self.label)
        
        self.filter_input = QLineEdit()
        self.filter_input.textChanged.connect(self.filter_dishes)
        self.layout.addWidget(self.filter_input)
        
        self.dish_list = QListWidget()
        self.dish_list.itemDoubleClicked.connect(self.open_edit_dish_modal)
        self.layout.addWidget(self.dish_list)
        
        self.add_button = QPushButton("New Dish")
        self.add_button.clicked.connect(self.open_add_dish_modal)
        self.layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_dish)
        self.layout.addWidget(self.remove_button)
        
        self.setLayout(self.layout)
        self.load_dish_list()

    def load_dish_list(self):
        self.dish_list.clear()
        self.dishes = load_dishes()
        self.dishes.sort(key=lambda x: x["name"].lower())
        for dish in self.dishes:
            sorted_tags = sorted(dish['tags'])
            self.dish_list.addItem(f"{dish['name']:<50} ({', '.join(sorted_tags)})")

    def open_add_dish_modal(self):
        self.modal = AddDishModal(self)
        self.modal.show()

    def open_edit_dish_modal(self, item):
        self.modal = EditDishModal(self, item)
        self.modal.show()

    def remove_dish(self):
        selected_items = self.dish_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            index = self.dish_list.row(item)
            self.dish_list.takeItem(index)
            del self.dishes[index]
        save_dishes(self.dishes)

    def filter_dishes(self):
        filter_text = self.filter_input.text().lower()
        self.dish_list.clear()
        for dish in self.dishes:
            if any(filter_text in tag.lower() for tag in dish["tags"]):
                self.dish_list.addItem(f"{dish['name']} ({', '.join(dish['tags'])})")
