import recursos_rc
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QApplication, QMessageBox
from PySide6.QtCore import Qt, Signal
import sqlite3
from datetime import datetime
import csv
import os

class InventarioWidget(QWidget):
    producto_agregado = Signal()
    producto_eliminado = Signal()

    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.init_ui()

    def init_ui(self):
        app = QApplication.instance()
        if app:
            app.setStyle("Fusion")

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Gestión de Inventario")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1A3C6D; margin-bottom: 20px;")
        layout.addWidget(title)

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
                min-width: 250px;
            }
            QLineEdit:focus { border: 2px solid #4A90E2; }
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
                min-width: 250px;
            }
            QLineEdit:focus { border: 2px solid #4A90E2; }
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
                min-width: 250px;
            }
            QLineEdit:focus { border: 2px solid #4A90E2; }
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
                min-width: 250px;
            }
            QLineEdit:focus { border: 2px solid #4A90E2; }
        """)
        layout.addWidget(self.input_cantidad)

        btn_agregar = QPushButton("Agregar Producto")
        btn_agregar.setStyleSheet("""
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
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6AA8F7, stop:1 #4A90E2); }
            QPushButton:pressed { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #357ABD, stop:1 #2A5F9A); }
        """)
        btn_agregar.clicked.connect(self.agregar_producto)
        layout.addWidget(btn_agregar, alignment=Qt.AlignCenter)

        btn_exportar = QPushButton("Exportar Historial")
        btn_exportar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4A90E2, stop:1 #357ABD);
                color: white;
                border: none;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                min-width: 200px;
                margin-top: 10px;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6AA8F7, stop:1 #4A90E2); }
            QPushButton:pressed { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #357ABD, stop:1 #2A5F9A); }
        """)
        btn_exportar.clicked.connect(self.exportar_historial)
        layout.addWidget(btn_exportar, alignment=Qt.AlignCenter)

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
                min-width: 250px;
            }
            QLineEdit:focus { border: 2px solid #4A90E2; }
        """)
        self.input_buscar.textChanged.connect(self.buscar_producto)
        layout.addWidget(self.input_buscar)

        self.tabla_productos = QTableWidget()
        self.tabla_productos.setRowCount(0)
        self.tabla_productos.setColumnCount(5)
        self.tabla_productos.setHorizontalHeaderLabels(["Nombre", "Costo ($)", "Precio Venta ($)", "Cantidad", "Acción"])
        self.tabla_productos.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #1A3C6D;
                border: 1px solid #D3DCE6;
                border-radius: 5px;
                font-size: 14px;
                margin-top: 20px;
            }
            QTableWidget::item { padding: 5px; border: none; }
            QHeaderView::section {
                background-color: #E6F0FA;
                color: #1A3C6D;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #D3DCE6;
            }
            QTableWidget::item:selected { background-color: #E6F0FA; color: #1A3C6D; }
        """)
        self.tabla_productos.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_productos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_productos.setWordWrap(True)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Nombre se estira
        self.tabla_productos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Costo
        self.tabla_productos.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Precio Venta
        self.tabla_productos.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Cantidad
        self.tabla_productos.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)  # Acción fija
        self.tabla_productos.setColumnWidth(4, 70)
        self.tabla_productos.verticalHeader().setDefaultSectionSize(40)
        self.tabla_productos.setMinimumHeight(200)
        layout.addWidget(self.tabla_productos)

        self.setStyleSheet("background-color: #F5F7FA;")
        self.setLayout(layout)
        self.cargar_productos()

    def resizeEvent(self, event):
        self.tabla_productos.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        super().resizeEvent(event)

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
                return

            # Registrar en el historial
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            descripcion = "Producto agregado al inventario"
            self.cursor.execute("""
                INSERT INTO inventario_historial (nombre, accion, cantidad, costo, precio_venta, fecha, descripcion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nombre, "agregar", cantidad, costo, precio_venta, fecha, descripcion))

            # Insertar o actualizar el inventario
            self.cursor.execute("INSERT INTO inventario (nombre, costo, precio_venta, cantidad) VALUES (?, ?, ?, ?)", 
                               (nombre, costo, precio_venta, cantidad))
        except sqlite3.IntegrityError:
            self.cursor.execute("UPDATE inventario SET cantidad = cantidad + ?, costo = ?, precio_venta = ? WHERE nombre = ?", 
                               (cantidad, costo, precio_venta, nombre))
            descripcion = "Producto actualizado en el inventario"
            self.cursor.execute("""
                INSERT INTO inventario_historial (nombre, accion, cantidad, costo, precio_venta, fecha, descripcion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nombre, "agregar", cantidad, costo, precio_venta, fecha, descripcion))

        self.conn.commit()
        print(f"Producto {nombre} agregado o actualizado en la base de datos")
        self.input_nombre.clear()
        self.input_costo.clear()
        self.input_precio_venta.clear()
        self.input_cantidad.clear()
        self.cargar_productos()
        self.producto_agregado.emit()

    def buscar_producto(self):
        texto = self.input_buscar.text().lower()
        self.tabla_productos.setRowCount(0)
        self.cursor.execute("SELECT nombre, costo, precio_venta, cantidad FROM inventario")
        for nombre, costo, precio_venta, cantidad in self.cursor.fetchall():
            if texto in nombre.lower():
                row_position = self.tabla_productos.rowCount()
                self.tabla_productos.insertRow(row_position)
                self.tabla_productos.setItem(row_position, 0, QTableWidgetItem(nombre))
                self.tabla_productos.setItem(row_position, 1, QTableWidgetItem(f"{costo:.2f}"))
                self.tabla_productos.setItem(row_position, 2, QTableWidgetItem(f"{precio_venta:.2f}"))
                self.tabla_productos.setItem(row_position, 3, QTableWidgetItem(str(cantidad)))
                btn_eliminar = QPushButton("Eliminar")
                btn_eliminar.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FF6B6B, stop:1 #D32F2F);
                        color: white;
                        border: none;
                        padding: 3px 6px;
                        font-size: 11px;
                        font-weight: bold;
                        border-radius: 5px;
                        min-width: 50px;
                        min-height: 20px;
                    }
                    QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FF8787, stop:1 #EF5350); }
                    QPushButton:pressed { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #D32F2F, stop:1 #B71C1C); }
                """)
                btn_eliminar.clicked.connect(lambda checked, n=nombre: self.eliminar_producto(n))
                self.tabla_productos.setCellWidget(row_position, 4, btn_eliminar)

    def cargar_productos(self):
        self.tabla_productos.setRowCount(0)
        self.cursor.execute("SELECT nombre, costo, precio_venta, cantidad FROM inventario")
        for nombre, costo, precio_venta, cantidad in self.cursor.fetchall():
            row_position = self.tabla_productos.rowCount()
            self.tabla_productos.insertRow(row_position)
            self.tabla_productos.setItem(row_position, 0, QTableWidgetItem(nombre))
            self.tabla_productos.setItem(row_position, 1, QTableWidgetItem(f"{costo:.2f}"))
            self.tabla_productos.setItem(row_position, 2, QTableWidgetItem(f"{precio_venta:.2f}"))
            self.tabla_productos.setItem(row_position, 3, QTableWidgetItem(str(cantidad)))
            btn_eliminar = QPushButton("Eliminar")
            btn_eliminar.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FF6B6B, stop:1 #D32F2F);
                    color: white;
                    border: none;
                    padding: 3px 6px;
                    font-size: 11px;
                    font-weight: bold;
                    border-radius: 5px;
                    min-width: 50px;
                    min-height: 20px;
                }
                QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FF8787, stop:1 #EF5350); }
                QPushButton:pressed { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #D32F2F, stop:1 #B71C1C); }
            """)
            btn_eliminar.clicked.connect(lambda checked, n=nombre: self.eliminar_producto(n))
            self.tabla_productos.setCellWidget(row_position, 4, btn_eliminar)

    def eliminar_producto(self, nombre):
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmar Eliminación")
        msg.setText(f"¿Estás seguro de eliminar el producto '{nombre}'?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setStyleSheet("""
            QMessageBox { background-color: #F5F7FA; color: #1A3C6D; font-size: 14px; }
            QMessageBox QLabel { color: #1A3C6D; }
            QMessageBox QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4A90E2, stop:1 #357ABD);
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 12px;
                border-radius: 5px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6AA8F7, stop:1 #4A90E2); }
            QMessageBox QPushButton:pressed { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #357ABD, stop:1 #2A5F9A); }
        """)
        if msg.exec_() == QMessageBox.Yes:
            # Obtener datos del producto antes de eliminar
            self.cursor.execute("SELECT cantidad, costo, precio_venta FROM inventario WHERE nombre = ?", (nombre,))
            resultado = self.cursor.fetchone()
            if resultado:
                cantidad, costo, precio_venta = resultado
                fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                descripcion = "Producto eliminado manualmente"
                self.cursor.execute("""
                    INSERT INTO inventario_historial (nombre, accion, cantidad, costo, precio_venta, fecha, descripcion)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (nombre, "eliminar", cantidad, costo, precio_venta, fecha, descripcion))

            self.cursor.execute("DELETE FROM inventario WHERE nombre = ?", (nombre,))
            self.conn.commit()
            print(f"Producto {nombre} eliminado de la base de datos")
            self.cargar_productos()
            self.producto_eliminado.emit()

    def reducir_stock(self, nombre_producto, cantidad):
        self.cursor.execute("SELECT cantidad, costo, precio_venta FROM inventario WHERE nombre = ?", (nombre_producto,))
        resultado = self.cursor.fetchone()
        if resultado:
            stock_actual, costo, precio_venta = resultado
            if stock_actual >= cantidad:
                nueva_cantidad = stock_actual - cantidad
                self.cursor.execute("UPDATE inventario SET cantidad = ? WHERE nombre = ?", (nueva_cantidad, nombre_producto))

                # Registrar en el historial
                fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                descripcion = "Producto vendido"
                self.cursor.execute("""
                    INSERT INTO inventario_historial (nombre, accion, cantidad, costo, precio_venta, fecha, descripcion)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (nombre_producto, "vender", cantidad, costo, precio_venta, fecha, descripcion))

                self.conn.commit()
                print(f"Stock reducido para {nombre_producto}. Nuevo stock: {nueva_cantidad}")
                self.cargar_productos()
                return True
        return False

    def obtener_precio_y_costo(self, nombre_producto):
        self.cursor.execute("SELECT costo, precio_venta FROM inventario WHERE nombre = ?", (nombre_producto,))
        resultado = self.cursor.fetchone()
        return resultado[0], resultado[1] if resultado else (None, None)

    def exportar_historial(self):
        # Obtener el directorio de datos del usuario
        user_data_dir = os.path.join(os.path.expanduser("~"), "DaluData")
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
        export_path = os.path.join(user_data_dir, f"inventario_historial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

        try:
            # Obtener el historial
            self.cursor.execute("SELECT nombre, accion, cantidad, costo, precio_venta, fecha, descripcion FROM inventario_historial")
            historial = self.cursor.fetchall()

            # Obtener el inventario actual
            self.cursor.execute("SELECT nombre, costo, precio_venta, cantidad FROM inventario")
            inventario_actual = self.cursor.fetchall()

            with open(export_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Escribir el historial de cambios
                writer.writerow(["Historial de Cambios"])
                writer.writerow(["Nombre", "Acción", "Cantidad", "Costo ($)", "Precio Venta ($)", "Fecha", "Descripción"])
                for row in historial:
                    writer.writerow(row)

                # Escribir el inventario actual
                writer.writerow([])
                writer.writerow(["Inventario Actual"])
                writer.writerow(["Nombre", "Costo ($)", "Precio Venta ($)", "Cantidad"])
                for row in inventario_actual:
                    writer.writerow(row)

            # Verificar que el archivo existe
            if os.path.exists(export_path):
                msg = QMessageBox(self)
                msg.setWindowTitle("Éxito")
                msg.setText(f"Historial exportado a {export_path}")
                msg.setStyleSheet("""
                    QMessageBox { 
                        background-color: #F5F7FA; 
                        color: #1A3C6D; 
                        font-size: 14px; 
                    }
                    QMessageBox QLabel { 
                        color: #1A3C6D; 
                        font-size: 14px; 
                    }
                    QMessageBox QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4A90E2, stop:1 #357ABD);
                        color: white;
                        border: none;
                        padding: 8px 15px;
                        font-size: 12px;
                        border-radius: 5px;
                        min-width: 80px;
                    }
                    QMessageBox QPushButton:hover { 
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6AA8F7, stop:1 #4A90E2); 
                    }
                    QMessageBox QPushButton:pressed { 
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #357ABD, stop:1 #2A5F9A); 
                    }
                """)
                msg.exec_()
                print(f"Historial exportado a {export_path}")
            else:
                raise Exception("El archivo CSV no se creó correctamente")

        except Exception as e:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"No se pudo exportar el historial: {str(e)}")
            msg.setStyleSheet("""
                QMessageBox { 
                    background-color: #F5F7FA; 
                    color: #1A3C6D; 
                    font-size: 14px; 
                }
                QMessageBox QLabel { 
                    color: #1A3C6D; 
                    font-size: 14px; 
                }
                QMessageBox QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FF6B6B, stop:1 #D32F2F);
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    font-size: 12px;
                    border-radius: 5px;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover { 
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FF8787, stop:1 #EF5350); 
                }
                QMessageBox QPushButton:pressed { 
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #D32F2F, stop:1 #B71C1C); 
                }
            """)
            msg.exec_()
            print(f"Error al exportar historial: {str(e)}")