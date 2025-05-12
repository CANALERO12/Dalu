import recursos_rc
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QApplication, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt, Signal
import sqlite3
from datetime import datetime

class VentasWidget(QWidget):
    venta_registrada = Signal()  # Señal para notificar que se registró una venta

    def __init__(self, conn, inventario_widget=None):
        super().__init__()
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.inventario_widget = inventario_widget
        self.productos_lista = []  # Lista para almacenar productos únicos
        self.init_ui()

    def init_ui(self):
        # Forzar estilo Fusion para consistencia en macOS
        app = QApplication.instance()
        if app:
            app.setStyle("Fusion")

        layout = QVBoxLayout()
        layout.setSpacing(15)  # Espaciado uniforme entre widgets
        layout.setContentsMargins(20, 20, 20, 20)  # Márgenes alrededor del widget

        # Título
        title = QLabel("Registro de Ventas")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1A3C6D; margin-bottom: 20px;")
        layout.addWidget(title)

        # Sección de Producto
        producto_label = QLabel("Producto:")
        producto_label.setStyleSheet("color: #1A3C6D; font-size: 16px;")
        layout.addWidget(producto_label)

        self.producto_combobox = QComboBox()
        self.producto_combobox.setEditable(True)
        self.producto_combobox.setInsertPolicy(QComboBox.NoInsert)
        self.producto_combobox.setAttribute(Qt.WA_StyledBackground, True)
        self.producto_combobox.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                color: #1A3C6D;
                border: 1px solid #4A90E2;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                min-height: 40px;
                min-width: 250px;
            }
            QComboBox:focus {
                border: 2px solid #4A90E2;
            }
            QComboBox::drop-down {
                width: 40px;
                border: none;
                background: #FFFFFF;
                border-left: 1px solid #D3DCE6;
            }
            QComboBox::down-arrow {
                image: url(:/imagenes/star.png);
                width: 15px;
                height: 15px;
                margin: 0px 10px;
                padding: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #1A3C6D;
                selection-background-color: #E6F0FA;
                selection-color: #1A3C6D;
                border: 1px solid #D3DCE6;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QComboBox QAbstractItemView::item {
                padding: 10px;
                min-height: 30px;
                color: #1A3C6D;
            }
        """)
        self.producto_combobox.lineEdit().setPlaceholderText("Busque un producto (ej. Pij para Pijama)...")
        self.producto_combobox.lineEdit().setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #1A3C6D;
                border: none;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit[placeholderText] {
                color: #7F9BBF;
            }
        """)
        self.producto_combobox.lineEdit().textEdited.connect(self.filtrar_productos)
        layout.addWidget(self.producto_combobox)

        # Sección de Cantidad
        cantidad_label = QLabel("Cantidad:")
        cantidad_label.setStyleSheet("color: #1A3C6D; font-size: 16px;")
        layout.addWidget(cantidad_label)

        self.input_cantidad = QLineEdit()
        self.input_cantidad.setPlaceholderText("Cantidad")
        self.input_cantidad.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #1A3C6D;
                border: 1px solid #4A90E2;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                min-width: 250px;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
            QLineEdit[placeholderText] {
                color: #7F9BBF;
            }
        """)
        layout.addWidget(self.input_cantidad)

        # Sección de Nombre del Cliente
        cliente_label = QLabel("Nombre del cliente (opcional):")
        cliente_label.setStyleSheet("color: #1A3C6D; font-size: 16px;")
        layout.addWidget(cliente_label)

        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Nombre del cliente (opcional)")
        self.input_cliente.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #1A3C6D;
                border: 1px solid #4A90E2;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                min-width: 250px;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
            QLineEdit[placeholderText] {
                color: #7F9BBF;
            }
        """)
        layout.addWidget(self.input_cliente)

        # Sección de Tipo de Pago
        tipo_pago_label = QLabel("Tipo de pago:")
        tipo_pago_label.setStyleSheet("color: #1A3C6D; font-size: 16px;")
        layout.addWidget(tipo_pago_label)

        self.tipo_pago_combo = QComboBox()
        self.tipo_pago_combo.addItems(["contado", "debe"])
        self.tipo_pago_combo.setAttribute(Qt.WA_StyledBackground, True)
        self.tipo_pago_combo.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                color: #1A3C6D;
                border: 1px solid #4A90E2;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                min-height: 40px;
                min-width: 250px;
            }
            QComboBox:focus {
                border: 2px solid #4A90E2;
            }
            QComboBox::drop-down {
                width: 40px;
                border: none;
                background: #FFFFFF;
                border-left: 1px solid #D3DCE6;
            }
            QComboBox::down-arrow {
                image: url(:/imagenes/star.png);
                width: 15px;
                height: 15px;
                margin: 0px 10px;
                padding: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #1A3C6D;
                selection-background-color: #E6F0FA;
                selection-color: #1A3C6D;
                border: 1px solid #D3DCE6;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QComboBox QAbstractItemView::item {
                padding: 10px;
                min-height: 30px;
                color: #1A3C6D;
            }
        """)
        layout.addWidget(self.tipo_pago_combo)

        # Botón para registrar venta
        btn_registrar = QPushButton("Registrar Venta")
        btn_registrar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4A90E2, stop:1 #357ABD);
                color: white;
                border: none;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                min-width: 200px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6AA8F7, stop:1 #4A90E2);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #357ABD, stop:1 #2A5F9A);
            }
        """)
        btn_registrar.clicked.connect(self.registrar_venta)
        layout.addWidget(btn_registrar, alignment=Qt.AlignCenter)

        # Tabla para mostrar las ventas
        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setRowCount(0)
        self.tabla_ventas.setColumnCount(7)
        self.tabla_ventas.setHorizontalHeaderLabels([
            "Producto", "Cantidad", "Total", "Ganancia", "Fecha", "Cliente", "Tipo de Pago"
        ])
        self.tabla_ventas.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #1A3C6D;
                border: 1px solid #D3DCE6;
                border-radius: 5px;
                font-size: 14px;
                margin-top: 20px;
            }
            QTableWidget::item {
                padding: 10px;
                border: none;
            }
            QHeaderView::section {
                background-color: #E6F0FA;
                color: #1A3C6D;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #D3DCE6;
            }
            QTableWidget::item:selected {
                background-color: #E6F0FA;
                color: #1A3C6D;
            }
        """)
        self.tabla_ventas.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_ventas.setEditTriggers(QTableWidget.NoEditTriggers)  # Hacer la tabla de solo lectura
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Ajustar columnas al ancho
        self.tabla_ventas.setMinimumHeight(150)
        layout.addWidget(self.tabla_ventas)

        self.setStyleSheet("background-color: #F5F7FA;")
        self.setLayout(layout)
        self.cargar_ventas()
        self.actualizar_productos()

        # Conectar la señal del inventario para actualizar productos
        if self.inventario_widget:
            self.inventario_widget.producto_agregado.connect(self.actualizar_productos)

    def actualizar_productos(self):
        self.producto_combobox.clear()
        self.productos_lista = []  # Limpiar lista de productos
        self.cursor.execute("SELECT DISTINCT nombre FROM inventario")
        productos = self.cursor.fetchall()
        if productos:
            for producto in productos:
                nombre = producto[0]
                if nombre and nombre not in self.productos_lista:  # Evitar duplicados
                    self.productos_lista.append(nombre)
                    self.producto_combobox.addItem(nombre, nombre)
        else:
            # Agregar productos de ejemplo si no hay nada en la base de datos
            ejemplo_productos = ["blusa", "pijama", "camiseta", "pantalón"]
            for producto in ejemplo_productos:
                if producto not in self.productos_lista:
                    self.productos_lista.append(producto)
                    self.producto_combobox.addItem(producto, producto)

    def filtrar_productos(self, texto):
        texto = texto.lower().strip()
        current_text = self.producto_combobox.lineEdit().text().lower().strip()

        # Si el texto está vacío o coincide con el texto actual, no hacer nada
        if not texto or texto == current_text:
            return

        # Restaurar lista completa si se borra todo el texto
        if len(texto) < len(current_text):  # Detectar borrado
            self.producto_combobox.clear()
            if self.productos_lista:
                for producto in self.productos_lista:
                    self.producto_combobox.addItem(producto, producto)
            else:
                self.producto_combobox.addItem("No hay productos", None)
            return

        # Filtrar productos solo si hay texto para buscar
        self.producto_combobox.clear()
        if self.productos_lista:
            filtered_productos = [producto for producto in self.productos_lista if texto in producto.lower()]
            if filtered_productos:
                for producto in filtered_productos:
                    self.producto_combobox.addItem(producto, producto)
                self.producto_combobox.showPopup()  # Mostrar el popup con las opciones filtradas
            else:
                self.producto_combobox.addItem("No se encontraron productos", None)
                self.producto_combobox.showPopup()  # Mostrar el popup incluso si no hay coincidencias
        else:
            self.producto_combobox.addItem("No hay productos", None)

    def registrar_venta(self):
        producto_nombre = self.producto_combobox.currentData()
        if not producto_nombre or producto_nombre in ["No hay productos", "No se encontraron productos"]:
            self.tabla_ventas.setRowCount(self.tabla_ventas.rowCount() + 1)
            self.tabla_ventas.setItem(self.tabla_ventas.rowCount() - 1, 0, QTableWidgetItem("Error: Selecciona un producto válido"))
            return

        cantidad = self.input_cantidad.text().strip()
        nombre_cliente = self.input_cliente.text().strip()
        tipo_pago = self.tipo_pago_combo.currentText()

        if not cantidad:
            self.tabla_ventas.setRowCount(self.tabla_ventas.rowCount() + 1)
            self.tabla_ventas.setItem(self.tabla_ventas.rowCount() - 1, 0, QTableWidgetItem("Error: Completa el campo de cantidad"))
            return

        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                self.tabla_ventas.setRowCount(self.tabla_ventas.rowCount() + 1)
                self.tabla_ventas.setItem(self.tabla_ventas.rowCount() - 1, 0, QTableWidgetItem("Error: La cantidad debe ser mayor a 0"))
                return
        except ValueError:
            self.tabla_ventas.setRowCount(self.tabla_ventas.rowCount() + 1)
            self.tabla_ventas.setItem(self.tabla_ventas.rowCount() - 1, 0, QTableWidgetItem("Error: La cantidad debe ser un número entero"))
            return

        # Obtener costo y precio de venta desde el inventario
        if self.inventario_widget:
            costo, precio_venta = self.inventario_widget.obtener_precio_y_costo(producto_nombre)
            if costo is None or precio_venta is None:
                costo = 10.0
                precio_venta = 15.0
                self.tabla_ventas.setRowCount(self.tabla_ventas.rowCount() + 1)
                self.tabla_ventas.setItem(self.tabla_ventas.rowCount() - 1, 0, QTableWidgetItem(f"Usando precios de ejemplo para {producto_nombre}: Costo ${costo:.2f}, Precio Venta ${precio_venta:.2f}"))

            # Verificar y reducir stock
            if not self.inventario_widget.reducir_stock(producto_nombre, cantidad):
                self.tabla_ventas.setRowCount(self.tabla_ventas.rowCount() + 1)
                self.tabla_ventas.setItem(self.tabla_ventas.rowCount() - 1, 0, QTableWidgetItem("Error: No hay suficiente stock"))
                return

            # Calcular total y ganancia
            total = precio_venta * cantidad
            ganancia = (precio_venta - costo) * cantidad
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Guardar venta en la base de datos
            self.cursor.execute("""
                INSERT INTO ventas (producto_nombre, cantidad, total, ganancia, fecha, nombre_cliente, tipo_pago)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (producto_nombre, cantidad, total, ganancia, fecha, nombre_cliente if nombre_cliente else None, tipo_pago))
            venta_id = self.cursor.lastrowid
            self.conn.commit()

            # Si es "debe" y hay un nombre de cliente, registrar una deuda
            if tipo_pago == "debe" and nombre_cliente:
                self.cursor.execute("""
                    INSERT INTO deudas (venta_id, nombre_deudor, monto, fecha)
                    VALUES (?, ?, ?, ?)
                """, (venta_id, nombre_cliente, total, fecha))
                self.conn.commit()

            # Actualizar la tabla de ventas
            self.cargar_ventas()

            # Limpiar campos
            self.producto_combobox.setCurrentIndex(-1)
            self.input_cantidad.clear()
            self.input_cliente.clear()

            # Emitir señal para notificar que se registró una venta
            self.venta_registrada.emit()

    def cargar_ventas(self):
        # Limpiar la tabla
        self.tabla_ventas.setRowCount(0)

        # Obtener las ventas de la base de datos
        self.cursor.execute("SELECT producto_nombre, cantidad, total, ganancia, fecha, nombre_cliente, tipo_pago FROM ventas")
        ventas = self.cursor.fetchall()

        # Llenar la tabla con las ventas
        for producto_nombre, cantidad, total, ganancia, fecha, nombre_cliente, tipo_pago in ventas:
            row_position = self.tabla_ventas.rowCount()
            self.tabla_ventas.insertRow(row_position)

            cliente_texto = nombre_cliente if nombre_cliente else "No especificado"

            self.tabla_ventas.setItem(row_position, 0, QTableWidgetItem(str(producto_nombre)))
            self.tabla_ventas.setItem(row_position, 1, QTableWidgetItem(str(cantidad)))
            self.tabla_ventas.setItem(row_position, 2, QTableWidgetItem(f"${total:.2f}"))
            self.tabla_ventas.setItem(row_position, 3, QTableWidgetItem(f"${ganancia:.2f}"))
            self.tabla_ventas.setItem(row_position, 4, QTableWidgetItem(fecha))
            self.tabla_ventas.setItem(row_position, 5, QTableWidgetItem(cliente_texto))
            self.tabla_ventas.setItem(row_position, 6, QTableWidgetItem(tipo_pago))