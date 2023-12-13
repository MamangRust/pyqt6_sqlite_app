import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QFileDialog, QTableWidgetItem, QTableWidget, QHBoxLayout, QComboBox, QInputDialog, QDialog, QFormLayout, QLineEdit, QHeaderView, QFrame
from PyQt6.QtCore import QDir
import sqlite3

class InsertRowDialog(QDialog):
    def __init__(self, database_path, selected_table, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Insert Row")
        layout = QFormLayout()

        self.input_fields = {}
        self.selected_table = selected_table
        self.uploaded_database = database_path  

        self.column_names = self.fetch_column_names()
        for column in self.column_names:
            line_edit = QLineEdit(self)
            self.input_fields[column] = line_edit
            layout.addRow(column, line_edit)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.submit)
        layout.addRow(self.submit_button)

        self.setLayout(layout)

    def fetch_column_names(self):
        conn = sqlite3.connect(self.uploaded_database)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.selected_table})")
        columns = [column[1] for column in cursor.fetchall()]
        conn.close()
        return columns

    def submit(self):
        if self.selected_table:
            values = [field.text() for field in self.input_fields.values()]

            conn = sqlite3.connect(self.uploaded_database)
            cursor = conn.cursor()

            placeholders = ', '.join(['?' for _ in values])
            insert_query = f"INSERT INTO {self.selected_table} VALUES ({placeholders})"

            cursor.execute(insert_query, values)
            conn.commit()
            conn.close()

            self.accept()



class UpdateRowDialog(QDialog):
    def __init__(self, database_path, selected_table, selected_row, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Row")
        layout = QFormLayout()

        self.input_fields = {}
        self.selected_table = selected_table
        self.uploaded_database = database_path
        self.selected_row = selected_row

        self.column_names = self.fetch_column_names()
        self.row_values = self.fetch_row_values()

        for column, value in zip(self.column_names, self.row_values):
            line_edit = QLineEdit(self)
            line_edit.setText(value)
            self.input_fields[column] = line_edit
            layout.addRow(column, line_edit)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.submit)
        layout.addRow(self.submit_button)

        self.setLayout(layout)

    def fetch_column_names(self):
        conn = sqlite3.connect(self.uploaded_database)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.selected_table})")
        columns = [column[1] for column in cursor.fetchall()]
        conn.close()
        return columns

    def fetch_row_values(self):
        conn = sqlite3.connect(self.uploaded_database)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {self.selected_table} WHERE rowid={self.selected_row + 1}")
        row = cursor.fetchone()
        conn.close()
        return [str(val) for val in row]

    def submit(self):
        if self.selected_table:
            values = [field.text() for field in self.input_fields.values()]

            conn = sqlite3.connect(self.uploaded_database)
            cursor = conn.cursor()

            set_values = ', '.join([f"{column} = ?" for column in self.column_names])
            update_query = f"UPDATE {self.selected_table} SET {set_values} WHERE rowid = ?"

            values.append(self.selected_row + 1)  # Append rowid for WHERE clause

            cursor.execute(update_query, values)
            conn.commit()
            conn.close()

            self.accept()






class DatabaseApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SQLite Database App")
        self.setGeometry(200, 200, 400, 300)
        self.uploaded_database = ""


        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")

        

        new_action = file_menu.addAction("New")
        new_action.triggered.connect(self.create_database)

        open_action = file_menu.addAction("Open")
        open_action.triggered.connect(self.upload_database)
       

        export_sql_action = file_menu.addAction("Export to Sql")
        export_sql_action.triggered.connect(self.export_database_sql)

        self.setWindowTitle("SQLite Database App")
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()

        # Layout untuk tombol-tombol kiri
        left_button_layout = QHBoxLayout()
        
        self.export_sql_button = QPushButton("Export Table", self)
        self.export_sql_button.clicked.connect(self.export_table_sql)

        self.insert_button = QPushButton("Insert Table", self)
        self.insert_button.clicked.connect(self.insert_table)

        self.read_button = QPushButton("Read Table", self)
        self.read_button.clicked.connect(self.read_table)

        self.delete_button = QPushButton("Delete Table", self)
        self.delete_button.clicked.connect(self.delete_table)

        left_button_layout.addWidget(self.export_sql_button)
        left_button_layout.addWidget(self.insert_button)
        left_button_layout.addWidget(self.read_button)
        left_button_layout.addWidget(self.delete_button)

        # Layout untuk tombol-tombol kanan
        right_button_layout = QHBoxLayout()
        self.insert_row_button = QPushButton("Insert Row", self)
        self.insert_row_button.clicked.connect(self.insert_row)

        self.update_row_button = QPushButton("Update Row", self)
        self.update_row_button.clicked.connect(self.update_row)

        self.delete_row_button = QPushButton("Delete Row", self)
        self.delete_row_button.clicked.connect(self.delete_row)

        right_button_layout.addWidget(self.insert_row_button)
        right_button_layout.addWidget(self.update_row_button)
        right_button_layout.addWidget(self.delete_row_button)

        # Gabungkan kumpulan tombol-tombol secara horizontal
        button_layout = QHBoxLayout()
        button_layout.addLayout(left_button_layout)
        button_layout.addStretch()  # Memberikan ruang di antara dua kumpulan tombol
        button_layout.addLayout(right_button_layout)

        layout.addLayout(button_layout)  

        # Tambahkan bagian pencarian di bawah kumpulan tombol
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search: "))  # Label untuk pencarian
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self.search_row)

        search_layout.addWidget(self.search_input)
        search_layout.addStretch()

        layout.addLayout(search_layout)



        # Tabel
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Layout untuk paginasi
        pagination_layout = QHBoxLayout()
        pagination_layout.addWidget(QLabel("Items per Page: ")) 
        self.pagination_combobox = QComboBox(self)
        self.pagination_combobox.addItems(["10", "25", "50", "100"])
        self.pagination_combobox.currentIndexChanged.connect(self.change_pagination)
        pagination_layout.addWidget(self.pagination_combobox)
        pagination_layout.addStretch()
        layout.addLayout(pagination_layout)  # Tambahkan layout paginasi ke dalam layout utama

        # Selector tabel
        self.table_selector = QComboBox(self)
        self.table_selector.currentIndexChanged.connect(self.select_table)
        layout.addWidget(self.table_selector)

        # Status label
        self.status_label = QLabel("", self)
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_database(self):
       
       file_dialog = QFileDialog()
       file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
       file_dialog.setFilter(QDir.Filter.AllDirs)
       file_dialog.setNameFilter("SQLite Database Files (*.db *.sqlite *.sqlite3)")
       filename, _ = file_dialog.getSaveFileName(self, "Create Database", "", "SQLite Database Files (*.db *.sqlite *.sqlite3)")
       
       if filename:
            conn = sqlite3.connect(filename)
            cursor = conn.cursor()

            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nama_tabel (
                    id INTEGER PRIMARY KEY,
                    nama TEXT,
                    usia INTEGER
                )
            ''')

            
            cursor.execute('''
                INSERT INTO nama_tabel (nama, usia) VALUES (?, ?)
            ''', ('John Doe', 30))

            cursor.execute('''
                INSERT INTO nama_tabel (nama, usia) VALUES (?, ?)
            ''', ('Jane Smith', 25))

            cursor.execute('''
                INSERT INTO nama_tabel (nama, usia) VALUES (?, ?)
            ''', ('Bob Johnson', 40))

            conn.commit()
            conn.close()
            self.status_label.setText(f"Database created: {filename}")
    
    

    def upload_database(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("SQLite Database Files (*.db *.sqlite *.sqlite3)")
        filename, _ = file_dialog.getOpenFileName(self, "Select Database File")
        

        if filename:
            self.uploaded_database = filename
            self.status_label.setText(f"Database uploaded: {filename}")

            conn = sqlite3.connect(filename)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            conn.close()

            self.table_selector.clear()

            for table in tables:
                self.table_selector.addItem(table[0])

    def export_database_sql(self):
        if self.uploaded_database:  
            try:
                output_file, _ = QFileDialog.getSaveFileName(self, "Save SQL File", "", "SQL Files (*.sql)")

                if output_file:  
                    conn_sqlite = sqlite3.connect(self.uploaded_database)  
                    cursor_sqlite = conn_sqlite.cursor()

                    cursor_sqlite.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor_sqlite.fetchall()

                    with open(output_file, 'w') as sql_file:
                        for table in tables:
                            table_name = table[0]
                            
                            # Retrieve table schema
                            cursor_sqlite.execute(f"PRAGMA table_info({table_name})")
                            table_info = cursor_sqlite.fetchall()

                            # Create table statement
                            create_table_statement = f"CREATE TABLE IF NOT EXISTS {table_name} ("
                            for column in table_info:
                                column_name = column[1]
                                column_type = column[2]
                                create_table_statement += f"{column_name} {column_type}, "
                            create_table_statement = create_table_statement.rstrip(", ") + ");\n"

                            # Retrieve table data
                            cursor_sqlite.execute(f"SELECT * FROM {table_name}")
                            rows = cursor_sqlite.fetchall()

                            sql_file.write(create_table_statement)  # Write CREATE TABLE statement
                            for row in rows:
                                values = ', '.join([f"'{str(value)}'" for value in row])
                                sql_file.write(f"INSERT INTO {table_name} VALUES ({values});\n")

                    conn_sqlite.close()
                    self.status_label.setText(f"Database saved to {output_file} successfully.")
                else:
                    self.status_label.setText("No file name provided.")
            except sqlite3.Error as e:
                self.status_label.setText("Error reading SQLite: " + str(e))
        else:
            self.status_label.setText("No Database to save")
            


    def export_table_sql(self):
        if self.uploaded_database:  
            try:
                output_file, _ = QFileDialog.getSaveFileName(self, "Save SQL File", "", "SQL Files (*.sql)")

                if output_file:  
                    conn_sqlite = sqlite3.connect(self.uploaded_database)  
                    cursor_sqlite = conn_sqlite.cursor()

                    selected_table = self.table_selector.currentText()

                    # Retrieve table schema
                    cursor_sqlite.execute(f"PRAGMA table_info({selected_table})")
                    table_info = cursor_sqlite.fetchall()

                    # Create table statement
                    create_table_statement = f"CREATE TABLE IF NOT EXISTS {selected_table} ("
                    for column in table_info:
                        column_name = column[1]
                        column_type = column[2]
                        create_table_statement += f"{column_name} {column_type}, "
                    create_table_statement = create_table_statement.rstrip(", ") + ");\n"

                    # Retrieve table data
                    cursor_sqlite.execute(f"SELECT * FROM {selected_table}")
                    rows = cursor_sqlite.fetchall()

                    conn_sqlite.close()

                    with open(output_file, 'w') as sql_file:
                        sql_file.write(create_table_statement)  # Write CREATE TABLE statement
                        for row in rows:
                            values = ', '.join([f"'{str(value)}'" for value in row])
                            sql_file.write(f"INSERT INTO {selected_table} VALUES ({values});\n")

                    self.status_label.setText(f"Data saved to {output_file} successfully.")
                else:
                    self.status_label.setText("No file name provided.")
            except sqlite3.Error as e:
                self.status_label.setText("Error reading SQLite: " + str(e))
        else:
            self.status_label.setText("No Database to save")

    def select_table(self):
        selected_table = self.table_selector.currentText()

        self.status_label.setText(f"Selected Table: {selected_table}")
        self.read_table()


    def read_table(self):
        if self.uploaded_database:
            conn = sqlite3.connect(self.uploaded_database)
            cursor = conn.cursor()

            selected_table = self.table_selector.currentText()

            try:
                self.page_size = int(self.pagination_combobox.currentText())  # Jumlah item per halaman
                self.current_page = 1  # Halaman saat ini

                # Mengambil data yang sesuai dengan paginasi
                query = f"SELECT * FROM {selected_table} LIMIT ? OFFSET ?"
                cursor.execute(query, (self.page_size, (self.current_page - 1) * self.page_size))
                rows = cursor.fetchall()

                # Menampilkan data ke dalam tabel
                if rows:
                    self.status_label.setText("Data from the table:")
                    self.table_widget.clear()
                    self.table_widget.setRowCount(len(rows))
                    self.table_widget.setColumnCount(len(rows[0]))

                    column_names = [description[0] for description in cursor.description]
                    self.table_widget.setHorizontalHeaderLabels(column_names)

                    for i, row in enumerate(rows):
                        for j, val in enumerate(row):
                            item = QTableWidgetItem(str(val))
                            self.table_widget.setItem(i, j, item)
                else:
                    self.status_label.setText("No data found in the table.")

                conn.close()
            except sqlite3.Error as e:
                self.status_label.setText("Error reading table: " + str(e))

            # Set tabel menjadi responsif
            header = self.table_widget.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        else:
            self.status_label.setText("Upload a database first.")

    def insert_table(self):
        if not self.uploaded_database:
            self.status_label.setText("Upload a database first.")
            return

        table_name, ok = QInputDialog.getText(self, "Table Name", "Enter table name:")
        if not ok or not table_name:
            self.status_label.setText("Please enter a table name.")
            return

        column_list = []

        while True:
            column_name, ok = QInputDialog.getText(self, "Column Name", f"Enter column name for '{table_name}':")
            if not ok:
                break

            column_type, ok = QInputDialog.getText(self, "Column Type", f"Enter type for column '{column_name}':")
            if not ok:
                break

            column_attributes, ok = QInputDialog.getText(self, "Column Attributes", f"Enter attributes for column '{column_name}' (e.g. PRIMARY KEY):")
            if not ok:
                break

            column_definition = f"{column_name} {column_type} {column_attributes}"
            column_list.append(column_definition)

            add_more_columns, ok = QInputDialog.getItem(self, "Add More Columns", "Add more columns?", ["Yes", "No"])
            if not ok or add_more_columns == "No":
                break

        if column_list:
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_list)})"

            conn = sqlite3.connect(self.uploaded_database)
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            conn.close()

            self.status_label.setText(f"Table '{table_name}' created successfully.")
        else:
            self.status_label.setText("No columns added for the table.")

    def delete_table(self):
        if self.uploaded_database:
            try:
                selected_table = self.table_selector.currentText()

                conn_sqlite = sqlite3.connect(self.uploaded_database)
                cursor_sqlite = conn_sqlite.cursor()

                cursor_sqlite.execute(f"DROP TABLE IF EXISTS {selected_table}")

                conn_sqlite.commit()
                conn_sqlite.close()

                self.status_label.setText(f"Table '{selected_table}' deleted successfully.")
            except sqlite3.Error as e:
                self.status_label.setText("Error deleting table: " + str(e))
        else:
            self.status_label.setText("Upload a database first.")


        

    def change_pagination(self, index):
        self.read_table()


    def insert_row(self):
        if self.uploaded_database:
            selected_table = self.table_selector.currentText()

            # Membuat dan menampilkan dialog untuk input nilai kolom baru
            dialog = InsertRowDialog(self.uploaded_database, selected_table, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.read_table()
        else:
            self.status_label.setText("Upload a database first.")


    def search_row(self):
        search_text = self.search_input.text().lower()

        if not search_text:
            # Jika kotak pencarian kosong, tampilkan semua baris
            self.read_table()
            return

        if self.uploaded_database:
            conn = sqlite3.connect(self.uploaded_database)
            cursor = conn.cursor()

            selected_table = self.table_selector.currentText()

            try:
                cursor.execute(f'SELECT * FROM {selected_table}')
                rows = cursor.fetchall()

                if rows:
                    self.status_label.setText("Data from the table:")

                    self.table_widget.clear()

                    # Filter baris berdasarkan pencarian
                    filtered_rows = [row for row in rows if any(search_text in str(cell).lower() for cell in row)]

                    self.table_widget.setRowCount(len(filtered_rows))
                    self.table_widget.setColumnCount(len(rows[0]))

                    column_names = [description[0] for description in cursor.description]
                    self.table_widget.setHorizontalHeaderLabels(column_names)

                    for i, row in enumerate(filtered_rows):
                        for j, val in enumerate(row):
                            item = QTableWidgetItem(str(val))
                            self.table_widget.setItem(i, j, item)
                else:
                    self.status_label.setText("No data found in the table.")

                conn.close()
            except sqlite3.Error as e:
                self.status_label.setText("Error reading table: " + str(e))
        else:
            self.status_label.setText("Upload a database first.")

    def update_row(self):
        if self.uploaded_database:
            selected_table = self.table_selector.currentText()

            # Ambil indeks baris yang dipilih
            selected_row = self.table_widget.currentRow()

            if selected_row >= 0:  # Pastikan baris dipilih
                dialog = UpdateRowDialog(self.uploaded_database, selected_table, selected_row, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.read_table() 
            else:
                self.status_label.setText("Select a row to update.")
        else:
            self.status_label.setText("Upload a database first.")


    def delete_row(self):
        if self.uploaded_database:
            selected_table = self.table_selector.currentText()

            # Ambil indeks baris yang dipilih
            selected_row = self.table_widget.currentRow()

            if selected_row >= 0:  # Pastikan baris dipilih
                conn = sqlite3.connect(self.uploaded_database)
                cursor = conn.cursor()

                try:
                    # Ambil kolom yang menjadi primary key (misalnya 'id')
                    cursor.execute(f"PRAGMA table_info({selected_table})")
                    columns = cursor.fetchall()
                    primary_key = [col[1] for col in columns if col[5] == 1][0]

                    # Ambil nilai primary key dari baris yang dipilih
                    selected_value = self.table_widget.item(selected_row, 0).text()  # Ganti '0' dengan indeks kolom primary key

                    # Hapus baris yang dipilih dari tabel
                    cursor.execute(f"DELETE FROM {selected_table} WHERE {primary_key} = ?", (selected_value,))
                    conn.commit()
                    conn.close()

                    self.read_table()  # Setelah penghapusan, refresh tampilan tabel
                except sqlite3.Error as e:
                    self.status_label.setText("Error deleting row: " + str(e))
            else:
                self.status_label.setText("Select a row to delete.")
        else:
            self.status_label.setText("Upload a database first.")


    

def run_app():
    app = QApplication(sys.argv)
    window = DatabaseApp()
    window.show()
    sys.exit(app.exec())



if __name__ == "__main__":
    run_app()

