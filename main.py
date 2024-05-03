from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, \
    QLineEdit, QGridLayout, QPushButton, QMainWindow, QTableWidget, \
    QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, \
    QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import mysql.connector


class DatabaseConnection:
    def __init__(self,
                 host='localhost',
                 user='root',
                 password='pythoncourse',
                 database='school'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host,
                                             user=self.user,
                                             password=self.password,
                                             database=self.database)
        return connection


class MainWindow(QMainWindow):
    # Child init
    def __init__(self):
        # Parent init
        super().__init__()
        # Set title
        self.setWindowTitle("Student Management System MySQL")
        self.setMinimumSize(800, 600)
        
        # Add menu
        file_menu = self.menuBar().addMenu("&File")
        edit_menu = self.menuBar().addMenu("&Edit")
        help_menu = self.menuBar().addMenu("&Help")
        
        # Add actions to file menu
        add_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_action.triggered.connect(self.insert)
        file_menu.addAction(add_action)
        
        # Add actions to edit menu
        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        edit_menu.addAction(search_action)
        search_action.triggered.connect(self.search)
        
        # Add actions to help menu
        about_action = QAction("About", self)
        help_menu.addAction(about_action)
        # for MAC about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)
        
        # Add data table
        self.table = QTableWidget()
        # Add columns
        self.table.setColumnCount(4)
        # Set column names
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        # Hide table indexing
        self.table.verticalHeader().setVisible(False)
        # Set table as central widget
        self.setCentralWidget(self.table)
        
        # Create toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_action)
        toolbar.addAction(search_action)
        
        # Create status bar and add status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)
        
        
    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)
        
        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)
        
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)
        
        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)
        
        
    def load_data(self):
        # Connect to MySQL database
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        # Store data in variable
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
        # To not overwrite rows
        self.table.setRowCount(0)
        # Add data to table
        for row_number, row_data in enumerate(result):
            #print(row_number)
            #print(row_data)
            # Add data to table
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                #print(column_number)
                #print(data)
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()
        
    def insert(self):
        dialog = InsertDialog()
        dialog.exec()
        
    def search(self):
        dialog = SearchDialog()
        dialog.exec()
    
    def edit(self):
        dialog = EditDialog()
        dialog.exec()
        
    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()
        
    def about(self):
        dialog = AboutDialog()
        dialog.exec()
    
 
class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        
        content = """
        This application, titled "Student Management System"
        is a desktop application built using the PyQt6 library in Python.
        It is designed to manage student records, allowing users
        to perform various operations such as adding, searching, editing, and
        deleting student data. This version uses MySQL databases.
        """
        self.setText(content)

        
class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        
        layout = QVBoxLayout()
        
        # Get student name from selected row
        index = window.table.currentRow()
        student_name = window.table.item(index, 1).text()
        
        # Get student ID from selected row
        self.student_id = window.table.item(index, 0).text()
        
        # Add student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Student Name")
        layout.addWidget(self.student_name)
        
        # Add combo box of courses
        course_name = window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)
        
        # Add mobile
        student_mobile = window.table.item(index, 3).text()
        self.mobile = QLineEdit(student_mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)
        
        # Add submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)
        
        self.setLayout(layout)
        
    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name =%s, course =%s, mobile =%s WHERE id =%s",
                       (self.student_name.text(),
                        self.course_name.currentText(),
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        window.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")
        
        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")
        
        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)
        
        
        
        yes.clicked.connect(self.delete_student)
        
        
    def delete_student(self):
        # Get selected row index and student id
        index = window.table.currentRow()
        student_id = window.table.item(index, 0).text()
        
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        window.load_data()
        
        self.close()
        
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The Record was deleted successfully!")
        confirmation_widget.exec()
       

class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        
        layout = QVBoxLayout()
        
        self.student_to_search = QLineEdit()
        self.student_to_search.setPlaceholderText("Student Name")
        layout.addWidget(self.student_to_search)
        
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search)
        layout.addWidget(search_button)

        
        self.setLayout(layout)
        
        
    def search(self):
        name = self.student_to_search.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (name,))
        result = cursor.fetchone()
        row = list(result)
        #print(row)
        window.table.clearSelection()
        items = window.table.findItems(row[1], Qt.MatchFlag.MatchExactly)
        for item in items:
            row_index = item.row()
            for column in range(window.table.columnCount()):
                window.table.item(row_index, column).setSelected(True)
                    
        
        cursor.close()
        connection.close()
        self.close()
       
        
class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        
        layout = QVBoxLayout()
        
        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Student Name")
        layout.addWidget(self.student_name)
        
        # Add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)
        
        # Add mobile
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)
        
        # Add submit button
        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)
        
        self.setLayout(layout)
        
    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        window.load_data()
        

app = QApplication(sys.argv)
window = MainWindow()
window.show()
window.load_data()
sys.exit(app.exec())
