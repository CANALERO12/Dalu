from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt, Signal
import sqlite3

class InventarioWidget(QWidget):
    producto_agregado = Signal()  # Señal para notificar que se agregó o actualizó un producto

    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Título
        title = QLabel("Gestión de Inventario")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A3C6D; margin-bottom: 10px;")
        layout.addWidget(title)

        # Campos para agregar producto
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre del producto")
        self.input_nombre.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #1A3C6D;
                border: 1px solid #4A90E2;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
        """)
        layout.addWidget(self.input_nombre)

        self.input_costo = QLineEdit()
        self.input_costo.setPlaceholderText("Costo unitario (valor real para ti)")
        self.input_costo.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #1A3C6D;
                border: 1px solid #4A90E2;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
        """)
        layout.addWidget(self.input_costo)

        self.input_precio_venta = QLineEdit()
        self.input_precio_venta.setPlaceholderText("Precio de venta unitario")
        self.input_precio_venta.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #1A3C6D;
                border: 1px solid #4A90E2;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
        """)
        layout.addWidget(self.input_precio_venta)

        self.input_cantidad = QLineEdit()
        self.input_cantidad.setPlaceholderText("Cantidad")
        self.input_cantidad.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #1A3C6D;
                border: 1px solid #4A90E2;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
        """)
        layout.addWidget(self.input_cantidad)

        btn_agregar = QPushButton("Agregar Producto")
        btn_agregar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4A90E2, stop:1 #357ABD);
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6AA8F7, stop:1 #4A90E2);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #357ABD, stop:1 #2A5F9A);
                box-shadow: 0 1px 3px rgba(0,0,0,0.3);
            }
        """)
        btn_agregar.clicked.connect(self.agregar_producto)
        layout.addWidget(btn_agregar, alignment=Qt.AlignCenter)

        # Campo de búsqueda
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar producto...")
        self.input_buscar.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #1A3C6D;
                border: 1px solid #4A90E2;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
        """)
        self.input_buscar.textChanged.connect(self.buscar_producto)
        layout.addWidget(self.input_buscar)

        # Tabla de productos
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setRowCount(0)
        self.tabla_productos.setColumnCount(4)  # Columnas: Nombre, Costo, Precio Venta, Cantidad
        self.tabla_productos.setHorizontalHeaderLabels(["Nombre", "Costo ($)", "Precio Venta ($)", "Cantidad"])
        self.tabla_productos.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #1A3C6D;
                border: 1px solid #D3DCE6;
                border-radius: 5px;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #E6F0FA;
                color: #1A3C6D;
                padding: 5px;
                border: 1px solid #D3DCE6;
                font-weight: bold;
            }
        """)
        # Ajustar el tamaño de las columnas
        self.tabla_productos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_productos.setEditTriggers(QTableWidget.NoEditTriggers)  # Hacer la tabla no editable
        layout.addWidget(self.tabla_productos)

        self.setStyleSheet("background-color: #F5F7FA;")
        self.setLayout(layout)
        self.cargar_productos()

    def agregar_producto(self):
        nombre = self.input_nombre.text().strip()
        costo = self.input_costo.text().strip()
        precio_venta = self.input_precio_venta.text().strip()
        cantidad = self.input_cantidad.text().strip()

        if not nombre or not costo or not precio_venta or not cantidad:
            return

        try:
            costo = float(costo)
            precio_venta = float(precio_venta)
            cantidad = int(cantidad)
            if costo < 0 or precio_venta < 0 or cantidad < 0:
                return  # Evitar valores negativos

            self.cursor.execute("INSERT INTO inventario (nombre, costo, precio_venta, cantidad) VALUES (?, ?, ?, ?)", 
                               (nombre, costo, precio_venta, cantidad))
        except sqlite3.IntegrityError:
            # Producto ya existe, actualiza la cantidad
            self.cursor.execute("UPDATE inventario SET cantidad = cantidad + ?, costo = ?, precio_venta = ? WHERE nombre = ?", 
                               (cantidad, costo, precio_venta, nombre))

        self.conn.commit()
        self.input_nombre.clear()
        self.input_costo.clear()
        self.input_precio_venta.clear()
        self.input_cantidad.clear()
        self.cargar_productos()

        # Emitir señal para notificar que se agregó o actualizó un producto
        self.producto_agregado.emit()

    def buscar_producto(self):
        texto = self.input_buscar.text().lower()
        self.tabla_productos.setRowCount(0)  # Limpiar la tabla
        self.cursor.execute("SELECT nombre, costo, precio_venta, cantidad FROM inventario")
        for nombre, costo, precio_venta, cantidad in self.cursor.fetchall():
            if texto in nombre.lower():  # Filtrar por nombre
                row_position = self.tabla_productos.rowCount()
                self.tabla_productos.insertRow(row_position)
                self.tabla_productos.setItem(row_position, 0, QTableWidgetItem(nombre))
                self.tabla_productos.setItem(row_position, 1, QTableWidgetItem(f"{costo:.2f}"))
                self.tabla_productos.setItem(row_position, 2, QTableWidgetItem(f"{precio_venta:.2f}"))
                self.tabla_productos.setItem(row_position, 3, QTableWidgetItem(str(cantidad)))

    def cargar_productos(self):
        self.tabla_productos.setRowCount(0)  # Limpiar la tabla
        self.cursor.execute("SELECT nombre, costo, precio_venta, cantidad FROM inventario")
        for nombre, costo, precio_venta, cantidad in self.cursor.fetchall():
            row_position = self.tabla_productos.rowCount()
            self.tabla_productos.insertRow(row_position)
            self.tabla_productos.setItem(row_position, 0, QTableWidgetItem(nombre))
            self.tabla_productos.setItem(row_position, 1, QTableWidgetItem(f"{costo:.2f}"))
            self.tabla_productos.setItem(row_position, 2, QTableWidgetItem(f"{precio_venta:.2f}"))
            self.tabla_productos.setItem(row_position, 3, QTableWidgetItem(str(cantidad)))

    def reducir_stock(self, nombre_producto, cantidad):
        self.cursor.execute("SELECT cantidad FROM inventario WHERE nombre = ?", (nombre_producto,))
        resultado = self.cursor.fetchone()
        if resultado:
            stock_actual = resultado[0]
            if stock_actual >= cantidad:
                nueva_cantidad = stock_actual - cantidad
                self.cursor.execute("UPDATE inventario SET cantidad = ? WHERE nombre = ?", (nueva_cantidad, nombre_producto))
                self.conn.commit()
                self.cargar_productos()
                return True
        return False

    def obtener_precio_y_costo(self, nombre_producto):
        self.cursor.execute("SELECT costo, precio_venta FROM inventario WHERE nombre = ?", (nombre_producto,))
        resultado = self.cursor.fetchone()
        if resultado:
            return resultado[0], resultado[1]  # Retorna costo y precio_venta
        return None, None