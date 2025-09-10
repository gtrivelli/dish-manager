from PyQt6.QtWidgets import QWidget, QListWidget, QLineEdit, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QTextEdit
from PyQt6 import QtCore
from utilities import save_dishes

class TagComponent(QWidget):
    def initializeTagComponent(self, layout=None):
        self.tag_name_label = QLabel("Tag Name:")
        layout.addWidget(self.tag_name_label)

        self.tag_name = QLineEdit()
        self.tag_name.setPlaceholderText("Press Enter to add tag")
        self.tag_name.setClearButtonEnabled(True)
        self.tag_name.setFocus()
        self.tag_name.returnPressed.connect(self.add_tag)
        layout.addWidget(self.tag_name)

        self.tag_list = QListWidget()
        self.tag_list.itemDoubleClicked.connect(self.remove_tag)

        if hasattr(self, "dish"):
            for tag in self.dish["tags"]:
                self.tag_list.addItem(tag)
            self.tag_list.sortItems(QtCore.Qt.SortOrder.AscendingOrder)

        layout.addWidget(self.tag_list)

    def add_tag(self):
        new_tag = self.tag_name.text()
        self.tag_list.addItem(new_tag)
        self.tag_name.clear()

    def remove_tag(self):
        selected_items = self.tag_list.selectedItems()
        print(selected_items)
        if not selected_items:
            return
        for item in selected_items:
            index = self.tag_list.row(item)
            self.tag_list.takeItem(index)

class RecipeComponent(QWidget):
    def initializeRecipeComponent(self, layout=None):
        self.recipe_label = QLabel("Recipe:")
        layout.addWidget(self.recipe_label)
        self.recipe_edit = QTextEdit()
        self.recipe_edit.setPlaceholderText("Enter recipe here")

        if hasattr(self, "dish") and "recipe" in self.dish:
            self.recipe_edit.setText(self.dish["recipe"])

        layout.addWidget(self.recipe_edit)  

class EditDishModal(TagComponent, RecipeComponent):
    def __init__(self, manager, dish_index):
        super().__init__()
        self.manager = manager
        self.dish_index = dish_index
        self.dish = self.manager.dishes[dish_index]

        self.setWindowTitle("Edit Dish")
        
        # FORCE ABSOLUTE POSITIONING - CENTER OF SCREEN
        self.setGeometry(300, 150, 800, 600)
        self.setFixedSize(800, 600)
        
        self.layout = QVBoxLayout()
        self.container_layout = QHBoxLayout()

        self.dish_layout = QVBoxLayout()
        self.dish_name_label = QLabel("Dish Name:")
        self.dish_layout.addWidget(self.dish_name_label)
        self.dish_name = QLineEdit()
        self.dish_name.setText(self.dish["name"])
        self.dish_layout.addWidget(self.dish_name)
        self.initializeTagComponent(self.dish_layout)
        self.container_layout.addLayout(self.dish_layout)

        self.recipe_layout = QVBoxLayout()
        self.initializeRecipeComponent(self.recipe_layout)
        self.container_layout.addLayout(self.recipe_layout)

        self.layout.addLayout(self.container_layout)

        self.save_button = QPushButton("Save Dish")
        self.save_button.clicked.connect(self.save_dish)
        self.layout.addWidget(self.save_button)
        
        self.setLayout(self.layout)

    def save_dish(self):
        self.manager.dishes[self.dish_index] = {
            "name": self.dish_name.text(),
            "tags": [self.tag_list.item(i).text() for i in range(self.tag_list.count())],
            "recipe": self.recipe_edit.toPlainText()
        }
        save_dishes(self.manager.dishes)
        self.manager.load_dish_list()        
        self.close()

class AddDishModal(TagComponent, RecipeComponent):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager

        self.setWindowTitle("Add Dish")
        
        # FORCE ABSOLUTE POSITIONING - CENTER OF SCREEN  
        self.setGeometry(300, 150, 800, 600)
        self.setFixedSize(800, 600)
        
        self.layout = QVBoxLayout()
        self.container_layout = QHBoxLayout()

        self.dish_layout = QVBoxLayout()
        self.dish_name_label = QLabel("Dish Name:")
        self.dish_layout.addWidget(self.dish_name_label)
        self.dish_name = QLineEdit()
        self.dish_layout.addWidget(self.dish_name)
        self.initializeTagComponent(self.dish_layout)
        self.container_layout.addLayout(self.dish_layout)

        self.recipe_layout = QVBoxLayout()
        self.initializeRecipeComponent(self.recipe_layout)
        self.container_layout.addLayout(self.recipe_layout)

        self.layout.addLayout(self.container_layout)

        self.add_button = QPushButton("Add Dish")
        self.add_button.clicked.connect(self.add_dish)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def add_dish(self):
        tags = [self.tag_list.item(i).text() for i in range(self.tag_list.count())]
        new_dish = {"name": self.dish_name.text(), "tags": tags, "recipe": self.recipe_edit.toPlainText()}
        self.manager.dish_list.addItem(f"{self.dish_name.text():<50} ({', '.join(tags)})")
        self.manager.dishes.append(new_dish)
        save_dishes(self.manager.dishes)
        self.manager.load_dish_list()
        self.close()
