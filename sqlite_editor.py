import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import sqlite3

class SQLiteEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("SQLite Editor")
        self.root.geometry("1000x700")

        self.conn = None
        self.cursor = None
        self.current_table = None

        self.create_widgets()

    def create_widgets(self):
        # Menú
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Abrir base de datos", command=self.open_database)
        file_menu.add_command(label="Salir", command=self.root.quit)

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Lista de tablas
        self.table_listbox = tk.Listbox(main_frame, width=30)
        self.table_listbox.grid(row=0, column=0, rowspan=3, padx=(0, 10), sticky=(tk.N, tk.S, tk.E, tk.W))
        self.table_listbox.bind('<<ListboxSelect>>', self.on_table_select)

        # Botones de tabla
        ttk.Button(main_frame, text="Ver contenido", command=self.view_table_content).grid(row=0, column=1, pady=(0, 5), sticky=tk.W)
        ttk.Button(main_frame, text="Crear tabla", command=self.create_table).grid(row=1, column=1, pady=(0, 5), sticky=tk.W)
        ttk.Button(main_frame, text="Eliminar tabla", command=self.delete_table).grid(row=2, column=1, pady=(0, 5), sticky=tk.W)

        # Área de consulta SQL
        self.sql_query = tk.Text(main_frame, height=5)
        self.sql_query.grid(row=3, column=0, columnspan=2, pady=(10, 5), sticky=(tk.W, tk.E))
        ttk.Button(main_frame, text="Ejecutar consulta", command=self.execute_query).grid(row=4, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

        # Tabla de resultados
        self.result_tree = ttk.Treeview(main_frame)
        self.result_tree.grid(row=5, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Botones de edición de registros
        ttk.Button(main_frame, text="Agregar registro", command=self.add_record).grid(row=6, column=0, pady=(5, 0), sticky=tk.W)
        ttk.Button(main_frame, text="Editar registro", command=self.edit_record).grid(row=6, column=1, pady=(5, 0), sticky=tk.W)
        ttk.Button(main_frame, text="Eliminar registro", command=self.delete_record).grid(row=7, column=0, pady=(5, 0), sticky=tk.W)
        ttk.Button(main_frame, text="Modificar campos", command=self.modify_fields).grid(row=7, column=1, pady=(5, 0), sticky=tk.W)

        # Scrollbars
        table_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.table_listbox.yview)
        table_scrollbar.grid(row=0, column=0, rowspan=3, sticky=(tk.N, tk.S, tk.E))
        self.table_listbox.configure(yscrollcommand=table_scrollbar.set)

        result_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        result_scrollbar.grid(row=5, column=2, sticky=(tk.N, tk.S))
        self.result_tree.configure(yscrollcommand=result_scrollbar.set)

        # Configurar el peso de las filas y columnas
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)

    def open_database(self):
        file_path = filedialog.askopenfilename(filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")])
        if file_path:
            try:
                self.conn = sqlite3.connect(file_path)
                self.cursor = self.conn.cursor()
                self.load_tables()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"No se pudo abrir la base de datos: {e}")

    def load_tables(self):
        self.table_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        for table in tables:
            self.table_listbox.insert(tk.END, table[0])

    def on_table_select(self, event):
        selection = self.table_listbox.curselection()
        if selection:
            self.current_table = self.table_listbox.get(selection[0])
            self.view_table_content()

    def view_table_content(self):
        if not self.current_table:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una tabla.")
            return

        try:
            self.cursor.execute(f"SELECT * FROM {self.current_table}")
            rows = self.cursor.fetchall()
            columns = [description[0] for description in self.cursor.description]
            
            self.result_tree.delete(*self.result_tree.get_children())
            self.result_tree["columns"] = columns
            self.result_tree["show"] = "headings"

            for col in columns:
                self.result_tree.heading(col, text=col)
                self.result_tree.column(col, width=100)

            for row in rows:
                self.result_tree.insert("", "end", values=row)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo cargar el contenido de la tabla: {e}")

    def create_table(self):
        table_name = simpledialog.askstring("Crear tabla", "Nombre de la nueva tabla:")
        if table_name:
            fields = []
            while True:
                field = simpledialog.askstring("Agregar campo", "Nombre del campo (o cancelar para terminar):")
                if not field:
                    break
                field_type = simpledialog.askstring("Tipo de campo", "Tipo de campo (TEXT, INTEGER, REAL, etc.):")
                fields.append(f"{field} {field_type}")
            
            if fields:
                query = f"CREATE TABLE {table_name} ({', '.join(fields)})"
                try:
                    self.cursor.execute(query)
                    self.conn.commit()
                    self.load_tables()
                    messagebox.showinfo("Éxito", f"Tabla '{table_name}' creada correctamente.")
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"No se pudo crear la tabla: {e}")
            else:
                messagebox.showwarning("Advertencia", "No se agregaron campos a la tabla.")

    def delete_table(self):
        if not self.current_table:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una tabla para eliminar.")
            return

        confirm = messagebox.askyesno("Confirmar", f"¿Estás seguro de que quieres eliminar la tabla '{self.current_table}'?")
        
        if confirm:
            try:
                self.cursor.execute(f"DROP TABLE {self.current_table}")
                self.conn.commit()
                self.load_tables()
                self.current_table = None
                self.result_tree.delete(*self.result_tree.get_children())
                messagebox.showinfo("Éxito", f"La tabla '{self.current_table}' ha sido eliminada.")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"No se pudo eliminar la tabla: {e}")

    def execute_query(self):
        query = self.sql_query.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Advertencia", "Por favor, ingresa una consulta SQL.")
            return

        try:
            self.cursor.execute(query)
            
            if query.lower().startswith("select"):
                rows = self.cursor.fetchall()
                columns = [description[0] for description in self.cursor.description]
                
                self.result_tree.delete(*self.result_tree.get_children())
                self.result_tree["columns"] = columns
                self.result_tree["show"] = "headings"

                for col in columns:
                    self.result_tree.heading(col, text=col)
                    self.result_tree.column(col, width=100)

                for row in rows:
                    self.result_tree.insert("", "end", values=row)
            else:
                self.conn.commit()
                messagebox.showinfo("Éxito", "La consulta se ejecutó correctamente.")
                self.load_tables()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al ejecutar la consulta: {e}")

    def add_record(self):
        if not self.current_table:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una tabla.")
            return

        self.cursor.execute(f"PRAGMA table_info({self.current_table})")
        columns = self.cursor.fetchall()

        values = []
        for col in columns:
            value = simpledialog.askstring("Agregar registro", f"Valor para {col[1]} ({col[2]}):")
            values.append(value)

        placeholders = ", ".join(["?" for _ in columns])
        query = f"INSERT INTO {self.current_table} VALUES ({placeholders})"

        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            self.view_table_content()
            messagebox.showinfo("Éxito", "Registro agregado correctamente.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo agregar el registro: {e}")

    def edit_record(self):
        if not self.current_table:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una tabla.")
            return

        selected_item = self.result_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un registro para editar.")
            return

        values = self.result_tree.item(selected_item)['values']
        self.cursor.execute(f"PRAGMA table_info({self.current_table})")
        columns = self.cursor.fetchall()

        new_values = []
        for i, col in enumerate(columns):
            new_value = simpledialog.askstring("Editar registro", f"Nuevo valor para {col[1]} ({col[2]}):", initialvalue=values[i])
            new_values.append(new_value)

        set_clause = ", ".join([f"{col[1]} = ?" for col in columns])
        where_clause = " AND ".join([f"{col[1]} = ?" for col in columns])
        query = f"UPDATE {self.current_table} SET {set_clause} WHERE {where_clause}"

        try:
            self.cursor.execute(query, new_values + values)
            self.conn.commit()
            self.view_table_content()
            messagebox.showinfo("Éxito", "Registro actualizado correctamente.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo actualizar el registro: {e}")

    def delete_record(self):
        if not self.current_table:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una tabla.")
            return

        selected_item = self.result_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un registro para eliminar.")
            return

        confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar este registro?")
        if not confirm:
            return

        values = self.result_tree.item(selected_item)['values']
        self.cursor.execute(f"PRAGMA table_info({self.current_table})")
        columns = self.cursor.fetchall()

        where_clause = " AND ".join([f"{col[1]} = ?" for col in columns])
        query = f"DELETE FROM {self.current_table} WHERE {where_clause}"

        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            self.view_table_content()
            messagebox.showinfo("Éxito", "Registro eliminado correctamente.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo eliminar el registro: {e}")

    def modify_fields(self):
        if not self.current_table:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una tabla.")
            return

        self.cursor.execute(f"PRAGMA table_info({self.current_table})")
        columns = self.cursor.fetchall()

        options = ["Agregar campo", "Eliminar campo", "Modificar campo"]
        choice = simpledialog.askstring("Modificar campos", f"Elige una opción:\n" + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)]))

        if choice == "1":
            self.add_field()
        elif choice == "2":
            self.remove_field(columns)
        elif choice == "3":
            self.alter_field(columns)
        else:
            messagebox.showwarning("Advertencia", "Opción no válida.")

    def add_field(self):
        new_field = simpledialog.askstring("Agregar campo", "Nombre del nuevo campo:")
        field_type = simpledialog.askstring("Tipo de campo", "Tipo de campo (TEXT, INTEGER, REAL, etc.):")
        
        
        
        query = f"ALTER TABLE {self.current_table} ADD COLUMN {new_field} {field_type}"
        
        try:
            self.cursor.execute(query)
            self.conn.commit()
            self.view_table_content()
            messagebox.showinfo("Éxito", f"Campo '{new_field}' agregado correctamente.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo agregar el campo: {e}")

    def remove_field(self, columns):
        field_names = [col[1] for col in columns]
        field_to_remove = simpledialog.askstring("Eliminar campo", f"Elige el campo a eliminar:\n" + "\n".join(field_names))
        
        if field_to_remove not in field_names:
            messagebox.showwarning("Advertencia", "Campo no válido.")
            return

        # SQLite doesn't support dropping columns directly, so we need to recreate the table
        new_columns = [col for col in columns if col[1] != field_to_remove]
        new_column_defs = [f"{col[1]} {col[2]}" for col in new_columns]
        new_column_names = [col[1] for col in new_columns]

        queries = [
            f"CREATE TABLE temp_table AS SELECT {', '.join(new_column_names)} FROM {self.current_table}",
            f"DROP TABLE {self.current_table}",
            f"ALTER TABLE temp_table RENAME TO {self.current_table}"
        ]

        try:
            for query in queries:
                self.cursor.execute(query)
            self.conn.commit()
            self.view_table_content()
            messagebox.showinfo("Éxito", f"Campo '{field_to_remove}' eliminado correctamente.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo eliminar el campo: {e}")

    def alter_field(self, columns):
        field_names = [col[1] for col in columns]
        field_to_alter = simpledialog.askstring("Modificar campo", f"Elige el campo a modificar:\n" + "\n".join(field_names))
        
        if field_to_alter not in field_names:
            messagebox.showwarning("Advertencia", "Campo no válido.")
            return

        new_name = simpledialog.askstring("Nuevo nombre", f"Nuevo nombre para el campo '{field_to_alter}':")
        new_type = simpledialog.askstring("Nuevo tipo", f"Nuevo tipo para el campo '{field_to_alter}' (TEXT, INTEGER, REAL, etc.):")

        # SQLite doesn't support altering columns directly, so we need to recreate the table
        new_columns = [
            (col[0], new_name if col[1] == field_to_alter else col[1], new_type if col[1] == field_to_alter else col[2])
            for col in columns
        ]
        new_column_defs = [f"{col[1]} {col[2]}" for col in new_columns]
        old_column_names = [col[1] for col in columns]
        new_column_names = [col[1] for col in new_columns]

        queries = [
            f"CREATE TABLE temp_table ({', '.join(new_column_defs)})",
            f"INSERT INTO temp_table SELECT {', '.join(old_column_names)} FROM {self.current_table}",
            f"DROP TABLE {self.current_table}",
            f"ALTER TABLE temp_table RENAME TO {self.current_table}"
        ]

        try:
            for query in queries:
                self.cursor.execute(query)
            self.conn.commit()
            self.view_table_content()
            messagebox.showinfo("Éxito", f"Campo '{field_to_alter}' modificado correctamente.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo modificar el campo: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SQLiteEditor(root)
    root.mainloop()