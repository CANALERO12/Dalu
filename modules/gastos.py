from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
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
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monto REAL NOT NULL,
                descripcion TEXT,
                fecha TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def init_ui(self):
        layout = QVBoxLayout()

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

        self.resultado_texto = QTextEdit()
        self.resultado_texto.setReadOnly(True)
        self.resultado_texto.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                color: #1A3C6D;
                border: 1px solid #D3DCE6;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
        """)
        self.resultado_texto.setMinimumWidth(300)  # Ancho mínimo inicial
        layout.addWidget(self.resultado_texto)

        self.setStyleSheet("background-color: #F5F7FA;")
        self.setLayout(layout)
        self.cargar_gastos()

    def resizeEvent(self, event):
        new_width = self.width() - 40  # Ajustar al ancho disponible
        self.resultado_texto.setMinimumWidth(new_width)
        super().resizeEvent(event)

    def registrar_gasto(self):
        try:
            monto = float(self.monto_input.text())
            if monto <= 0:
                self.resultado_texto.append("El monto debe ser mayor a 0.")
                return

            descripcion = self.descripcion_input.text().strip() or "Sin descripción"
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.cursor.execute("""
                INSERT INTO gastos (monto, descripcion, fecha)
                VALUES (?, ?, ?)
            """, (monto, descripcion, fecha))
            self.conn.commit()

            self.resultado_texto.append(f"Gasto registrado: {monto} - {descripcion} ({fecha})")
            self.monto_input.clear()
            self.descripcion_input.clear()
            self.cargar_gastos()
            self.gasto_registrado.emit()

        except ValueError:
            self.resultado_texto.append("Entrada inválida. Asegúrese de ingresar un número válido.")

    def cargar_gastos(self):
        self.resultado_texto.clear()
        self.cursor.execute("SELECT monto, descripcion, fecha FROM gastos")
        gastos = self.cursor.fetchall()
        if not gastos:
            self.resultado_texto.append("No hay gastos registrados.")
            return
        for gasto in gastos:
            self.resultado_texto.append(f"Monto: {gasto[0]}, Descripción: {gasto[1]}, Fecha: {gasto[2]}")