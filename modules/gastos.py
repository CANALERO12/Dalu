from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt, Signal
import sqlite3
from datetime import datetime

class GastosWidget(QWidget):
    gasto_registrado = Signal()

    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.crear_tabla()
        self.init_ui()

    def crear_tabla(self):
        print("Creando tabla gastos en GastosWidget...")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monto REAL NOT NULL,
                descripcion TEXT,
                fecha TEXT NOT NULL
            )
        """)
        self.conn.commit()
        print("Tabla gastos creada o verificada en GastosWidget")

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Gestión de Gastos")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A3C6D; margin-bottom: 10px;")
        layout.addWidget(title)

        self.monto_input = QLineEdit()
        self.monto_input.setPlaceholderText("Monto del gasto")
        self.monto_input.setStyleSheet("""
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
        layout.addWidget(self.monto_input)

        self.descripcion_input = QLineEdit()
        self.descripcion_input.setPlaceholderText("Descripción (opcional)")
        self.descripcion_input.setStyleSheet("""
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
        layout.addWidget(self.descripcion_input)

        btn_registrar = QPushButton("Registrar Gasto")
        btn_registrar.setStyleSheet("""
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
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6AA8F7, stop:1 #4A90E2); }
            QPushButton:pressed { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #357ABD, stop:1 #2A5F9A); }
        """)
        btn_registrar.clicked.connect(self.registrar_gasto)
        layout.addWidget(btn_registrar, alignment=Qt.AlignCenter)

        self.tabla_gastos = QTableWidget()
        self.tabla_gastos.setRowCount(0)
        self.tabla_gastos.setColumnCount(3)
        self.tabla_gastos.setHorizontalHeaderLabels(["Monto ($)", "Descripción", "Fecha"])
        self.tabla_gastos.setStyleSheet("""
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
        self.tabla_gastos.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_gastos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_gastos.setWordWrap(True)
        self.tabla_gastos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_gastos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Monto
        self.tabla_gastos.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Descripción
        self.tabla_gastos.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Fecha
        self.tabla_gastos.verticalHeader().setDefaultSectionSize(40)
        self.tabla_gastos.setMinimumHeight(200)
        layout.addWidget(self.tabla_gastos)

        self.setStyleSheet("background-color: #F5F7FA;")
        self.setLayout(layout)
        self.cargar_gastos()

    def resizeEvent(self, event):
        self.tabla_gastos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla_gastos.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_gastos.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        super().resizeEvent(event)

    def registrar_gasto(self):
        try:
            monto = float(self.monto_input.text())
            if monto <= 0:
                self.tabla_gastos.setRowCount(self.tabla_gastos.rowCount() + 1)
                self.tabla_gastos.setItem(self.tabla_gastos.rowCount() - 1, 0, QTableWidgetItem("El monto debe ser mayor a 0."))
                return

            descripcion = self.descripcion_input.text().strip() or "Sin descripción"
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.cursor.execute("""
                INSERT INTO gastos (monto, descripcion, fecha)
                VALUES (?, ?, ?)
            """, (monto, descripcion, fecha))
            self.conn.commit()
            print(f"Gasto registrado: {monto} - {descripcion} ({fecha})")

            self.monto_input.clear()
            self.descripcion_input.clear()
            self.cargar_gastos()
            self.gasto_registrado.emit()

        except ValueError:
            self.tabla_gastos.setRowCount(self.tabla_gastos.rowCount() + 1)
            self.tabla_gastos.setItem(self.tabla_gastos.rowCount() - 1, 0, QTableWidgetItem("Entrada inválida. Asegúrese de ingresar un número válido."))

    def cargar_gastos(self):
        self.tabla_gastos.setRowCount(0)
        self.cursor.execute("SELECT monto, descripcion, fecha FROM gastos")
        gastos = self.cursor.fetchall()
        if not gastos:
            self.tabla_gastos.setRowCount(1)
            self.tabla_gastos.setItem(0, 0, QTableWidgetItem("No hay gastos registrados."))
            return
        for monto, descripcion, fecha in gastos:
            row_position = self.tabla_gastos.rowCount()
            self.tabla_gastos.insertRow(row_position)
            self.tabla_gastos.setItem(row_position, 0, QTableWidgetItem(f"${monto:.2f}"))
            self.tabla_gastos.setItem(row_position, 1, QTableWidgetItem(descripcion))
            self.tabla_gastos.setItem(row_position, 2, QTableWidgetItem(fecha))