import sys
import sqlite3
import os
import shutil
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QLabel, QWidget, QScrollArea
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QScreen

from modules.ventas import VentasWidget
from modules.gastos import GastosWidget
from modules.deudas import DeudasWidget
from modules.balance import BalanceWidget
from modules.Inventario import InventarioWidget

def resource_path(relative_path):
    """Obtiene la ruta correcta del archivo, manejando el entorno de PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class DaluApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dalu")

        # Obtener el tamaño de la pantalla
        app = QApplication.instance()
        screen = app.primaryScreen()
        screen_size = screen.availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        # Establecer el tamaño de la ventana
        window_width = int(screen_width * 0.5)
        window_height = int(screen_height * 0.8)
        self.setMinimumSize(window_width, window_height)
        self.resize(window_width, window_height)

        # Ruta dinámica para la base de datos
        base_db_path = resource_path("dalu_inventario.db")
        user_data_dir = os.path.join(os.path.expanduser("~"), "DaluData")
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
        persistent_db_path = os.path.join(user_data_dir, "dalu_inventario.db")

        # Copiar la base de datos inicial si no existe
        if not os.path.exists(persistent_db_path):
            print(f"Copiando base de datos inicial de {base_db_path} a {persistent_db_path}")
            shutil.copy2(base_db_path, persistent_db_path)

        # Conectar a la base de datos persistente
        print(f"Conectando a la base de datos en: {persistent_db_path}")
        self.conn = sqlite3.connect(persistent_db_path)
        self.cursor = self.conn.cursor()
        self.crear_tablas()

        # Widget principal con layout vertical
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)

        # Espacio para el logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        logo_path = resource_path("modules/Logo/logo_dalu.png")
        if not os.path.exists(logo_path):
            print(f"Error: El archivo {logo_path} no existe en la ruta especificada")
            self.logo_label.setText("Logo no encontrado - Archivo no existe")
        else:
            pixmap = QPixmap(logo_path)
            if pixmap.isNull():
                print(f"Error: No se pudo cargar el archivo {logo_path}")
                self.logo_label.setText("Logo no encontrado - Error al cargar")
            else:
                print("Logo cargado exitosamente")
                self.logo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setStyleSheet("""
            background-color: #F5F7FA; 
            border: 1px solid #D3DCE6; 
            border-radius: 15px; 
            margin: 15px; 
            padding: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        """)
        self.logo_label.setMaximumSize(220, 220)
        self.logo_label.setMinimumSize(220, 220)
        self.layout.addWidget(self.logo_label, alignment=Qt.AlignHCenter)

        # Pestañas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget { 
                background-color: #F5F7FA; 
                color: #1A3C6D; 
                border: none; 
                margin: 0px 10px;
            }
            QTabBar::tab { 
                background-color: #4A90E2; 
                color: white; 
                padding: 12px 25px; 
                margin-right: 3px; 
                border-top-left-radius: 10px; 
                border-top-right-radius: 10px; 
                font-weight: bold; 
                font-size: 15px;
            }
            QTabBar::tab:selected { 
                background-color: #FFFFFF; 
                color: #1A3C6D; 
                border-bottom: 3px solid #4A90E2; 
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            QTabBar::tab:hover { 
                background-color: #6AA8F7; 
            }
        """)

        # Crear instancias de los widgets, pasando la conexión
        self.inventario_widget = InventarioWidget(self.conn)
        self.ventas_widget = VentasWidget(self.conn, inventario_widget=self.inventario_widget)
        self.gastos_widget = GastosWidget(self.conn)
        self.deudas_widget = DeudasWidget(self.conn)
        self.balance_widget = BalanceWidget(self.conn)

        # Agregar pestañas
        self.tabs.addTab(self.ventas_widget, "Ventas")
        self.tabs.addTab(self.gastos_widget, "Gastos")
        self.tabs.addTab(self.deudas_widget, "Deudas")
        self.tabs.addTab(self.balance_widget, "Balance")
        self.tabs.addTab(self.inventario_widget, "Inventario")

        # Envolver las pestañas en un QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.tabs)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #F5F7FA; 
                border: none;
                margin: 0px 10px;
            }
            QScrollBar:vertical {
                border: none;
                background: #E6ECF0;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #4A90E2;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6AA8F7;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.layout.addWidget(self.scroll_area)

        # Ajustar el layout
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        self.layout.setStretch(0, 0)  # Logo con peso 0
        self.layout.setStretch(1, 1)  # ScrollArea con peso 1 para ocupar el espacio restante

        # Estilo general de la ventana
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F7FA;
                color: #1A3C6D;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        # Conectar señales
        self.ventas_widget.venta_registrada.connect(self.balance_widget.calcular_balance)
        self.deudas_widget.deuda_pagada.connect(self.balance_widget.calcular_balance)
        self.ventas_widget.venta_registrada.connect(self.deudas_widget.actualizar)
        self.gastos_widget.gasto_registrado.connect(self.balance_widget.calcular_balance)

    def resizeEvent(self, event):
        new_width = self.width() - 40
        self.tabs.setMaximumWidth(new_width)
        self.scroll_area.setMaximumWidth(new_width)
        self.scroll_area.setMinimumWidth(new_width)
        super().resizeEvent(event)

    def crear_tablas(self):
        print("Creando tabla inventario...")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                costo REAL,
                precio_venta REAL,
                cantidad INTEGER
            )
        """)

        print("Creando tabla inventario_historial...")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventario_historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                accion TEXT,  -- 'agregar', 'vender', 'eliminar'
                cantidad INTEGER,
                costo REAL,
                precio_venta REAL,
                fecha TEXT,
                descripcion TEXT
            )
        """)

        print("Creando tabla ventas...")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_nombre TEXT,
                cantidad INTEGER NOT NULL,
                total REAL NOT NULL,
                ganancia REAL NOT NULL,
                fecha TEXT NOT NULL,
                nombre_cliente TEXT,
                tipo_pago TEXT NOT NULL DEFAULT 'contado',
                FOREIGN KEY (producto_nombre) REFERENCES inventario(nombre)
            )
        """)

        try:
            self.cursor.execute("SELECT tipo_pago FROM ventas LIMIT 1")
            print("Columna tipo_pago ya existe en tabla ventas")
        except sqlite3.OperationalError as e:
            if "no such column: tipo_pago" in str(e):
                print("Realizando migración de la tabla ventas para agregar tipo_pago...")
                self.cursor.execute("ALTER TABLE ventas RENAME TO ventas_old")
                self.cursor.execute("""
                    CREATE TABLE ventas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        producto_nombre TEXT,
                        cantidad INTEGER NOT NULL,
                        total REAL NOT NULL,
                        ganancia REAL NOT NULL,
                        fecha TEXT NOT NULL,
                        nombre_cliente TEXT,
                        tipo_pago TEXT NOT NULL DEFAULT 'contado',
                        FOREIGN KEY (producto_nombre) REFERENCES inventario(nombre)
                    )
                """)
                self.cursor.execute("""
                    INSERT INTO ventas (id, producto_nombre, cantidad, total, ganancia, fecha, nombre_cliente)
                    SELECT id, producto_nombre, cantidad, total, ganancia, fecha, nombre_cliente
                    FROM ventas_old
                """)
                self.cursor.execute("DROP TABLE ventas_old")
                self.conn.commit()
                print("Migración completada")

        print("Creando tabla deudas...")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS deudas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER,
                nombre_deudor TEXT NOT NULL,
                monto REAL NOT NULL,
                fecha TEXT NOT NULL,
                pagado INTEGER DEFAULT 0,
                FOREIGN KEY (venta_id) REFERENCES ventas(id)
            )
        """)

        print("Creando tabla gastos...")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monto REAL NOT NULL,
                descripcion TEXT,
                fecha TEXT NOT NULL
            )
        """)
        self.conn.commit()
        print("Tablas creadas o verificadas correctamente")

    def closeEvent(self, event):
        print("Cerrando la conexión a la base de datos...")
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DaluApp()
    window.show()
    sys.exit(app.exec())