import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import json
import re
import os

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Folder structure validator")
        self.setGeometry(100, 100, 600, 400)
        self.setMinimumWidth(650)
        self.setMinimumHeight(700)
        
        
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.populate_tree(folder_structure, self.tree_widget.invisibleRootItem())
        self.tree_widget.expandAll()

        # Combo Box with quick search functionality
        self.combo_box = QComboBox()
        self.combo_box.setEditable(True)
        self.combo_box.setInsertPolicy(QComboBox.NoInsert)
        self.combo_box.setCompleter(QCompleter(self.combo_box.model()))
        self.combo_box.currentTextChanged.connect(self.activatePushButton)
        
        
        self.validateButton = QPushButton("Validate")
        self.validateButton.clicked.connect(self.validateFiles)
        self.validateButton.setFixedWidth(200)
        self.populate_combo_box(base_folder)

        comboBtnLay = QHBoxLayout()
        comboBtnLay.addWidget(self.combo_box)
        comboBtnLay.addWidget(self.validateButton)
        
        
        layout = QVBoxLayout()
        layout.addLayout(comboBtnLay)
        layout.addWidget(self.tree_widget)
        
        container = QWidget()
        container.setLayout(layout)
        
        self.setCentralWidget(container)
    
    def validateFiles(self):
        self.check_files(base_folder, self.data, self.tree_widget.invisibleRootItem())
        self.tree_widget.expandAll()

    def check_files(self, base_path, structure, parent_item):
        for i in range(parent_item.childCount()):
            item = parent_item.child(i)
            key = item.text(0)
            if key in structure:
                path = os.path.join(base_path, key)
                if os.path.exists(path):
                    item.setForeground(0, QBrush(QColor('green')))
                if isinstance(structure[key], dict):
                    if os.path.exists(path):
                        self.check_files(path, structure[key], item)
                    else:
                        item.setForeground(0, QBrush(QColor('red')))
                elif isinstance(structure[key], list):
                    for sub_item in structure[key]:
                        allFiles = os.listdir(path)
                        for eachFile in allFiles:
                            if re.match(sub_item, eachFile):
                                sub_path = os.path.join(path, eachFile)
                                if os.path.exists(sub_path):
                                    if "\\d" in item.child(0).text(0):
                                        new_item = QTreeWidgetItem([eachFile])
                                        item.addChild(new_item)
                                        new_item.setForeground(0, QBrush(QColor('green')))
                                    else:
                                        new_item = QTreeWidgetItem([eachFile])
                                        item.addChild(new_item)
                                        new_item.setForeground(0, QBrush(QColor('green')))
                            else:
                                if "\\d" in item.child(0).text(0):
                                        new_item = QTreeWidgetItem([eachFile])
                                        item.addChild(new_item)
                                        new_item.setForeground(0, QBrush(QColor('red')))
                                else:
                                    new_item = QTreeWidgetItem([eachFile])
                                    item.addChild(new_item)
                                    new_item.setForeground(0, QBrush(QColor('red')))
        self.validateButton.setStyleSheet("background-color : green") 
        if self.has_red_items():
            self.validateButton.setStyleSheet("background-color : red")
        
    def has_red_items(self, item=None):
        if item is None:
            item = self.tree_widget.invisibleRootItem()

        child_count = item.childCount()
        for i in range(child_count):
            child = item.child(i)
            if child.foreground(0).color() == QColor('red'):
                return True
            if self.has_red_items(child):
                return True
        return False
    
    def populate_combo_box(self, base_folder):
        folder_list = []
        self.combo_box.addItem("Select Shot")
        for dirs in os.listdir(base_folder):
            folder_list.append(dirs)
        self.combo_box.addItems(folder_list)
        self.combo_box.setCurrentText("Select Shot")
    
    def populate_tree(self, structure, parent_item):
        for key, value in structure.items():
            if isinstance(value, dict):
                item = QTreeWidgetItem([key])
                parent_item.addChild(item)
                self.populate_tree(value, item)
            elif isinstance(value, list):
                item = QTreeWidgetItem([key])
                parent_item.addChild(item)
                for elem in value:
                    sub_item = QTreeWidgetItem([elem])
                    item.addChild(sub_item)

    def replace_placeholders(self, structure, shotName, plate, version, vendorName):
        def recursive_replace(value):
            if isinstance(value, dict):
                return {k: recursive_replace(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [recursive_replace(v) for v in value]
            elif isinstance(value, str):
                return value.replace("<shotName>", shotName)\
                            .replace("<plate>", plate)\
                            .replace("<version>", version)\
                            .replace("<vendorName>", vendorName)
            return value
        
        return {recursive_replace(k): recursive_replace(v) for k, v in structure.items()}
    
    def extract_components(self, selString):
        pattern = r'(WB_\d+_\d+)_(plate-\w+)_(v\d+)_(Rad)'
        match = re.match(pattern, selString)
        if match:
            group1 = match.group(1)  # WB_\d+_\d+
            group2 = match.group(2)  # plate-\w+
            group3 = match.group(3)  # v\d+
            group4 = match.group(4)  # Rad
            return group1, group2, group3, group4
        else:
            return None
    
    def add_subfolders(self, parent_item, subfolders):
        for subfolder, contents in subfolders.items():
            subfolder_item = QTreeWidgetItem([subfolder])
            parent_item.addChild(subfolder_item)
            
            if isinstance(contents, list):
                for file in contents:
                    file_item = QTreeWidgetItem([file])
                    subfolder_item.addChild(file_item)
            elif isinstance(contents, dict):
                self.add_subfolders(subfolder_item, contents)
    
    def activatePushButton(self):
        self.validateButton.setDisabled(True)
        currentShot = self.combo_box.currentText()
        if currentShot == "Select Shot":
            self.tree_widget.clear()
            self.populate_tree(folder_structure, self.tree_widget.invisibleRootItem())
            self.tree_widget.expandAll()
            self.validateButton.setStyleSheet("background-color : white") 
            return
        self.validateButton.setDisabled(False)
        shotName, plate, version, vendorName = self.extract_components(currentShot)
        self.data = self.replace_placeholders(folder_structure, shotName, plate, version, vendorName)
        # Add the root item
        self.tree_widget.clear()
        self.populate_tree(self.data, self.tree_widget.invisibleRootItem())
        self.tree_widget.expandAll()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    base_folder = r'D:\someFolder'
    json_path = r'C:\Users\Sanjay D\Desktop\validatorTool\Config.json'
    folder_structure = load_json(json_path)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
