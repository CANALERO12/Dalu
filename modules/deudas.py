from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal
import sqlite3

class DeudasWidget(QWidget):
    deuda_pagada = Signal()

    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.title_label = QLabel("Deudas Pendientes")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A3C6D; margin-bottom: 10px;")
        layout.addWidget(self.title_label)

        self.lista_deudas = QListWidget()
        self.lista_deudas.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                color: #1A3C6D;
                border: 1px solid #D3DCE6;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QListWidget::item:selected { background-color: #E6F0FA; color: #1A3C6D; }
        """)
        self.lista_deudas.setMinimumWidth(300)  # Ancho mínimo inicial
        layout.addWidget(self.lista_deudas)

        self.marcar_pagada_btn = QPushButton("Marcar Deuda como Pagada")
        self.marcar_pagada_btn.setStyleSheet("""
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
        self.marcar_pagada_btn.clicked.connect(self.marcar_pagada)
        layout.addWidget(self.marcar_pagada_btn, alignment=Qt.AlignCenter)

        self.setStyleSheet("background-color: #F5F7FA;")
        self.setLayout(layout)
        self.mostrar_deudas()

    def resizeEvent(self, event):
        new_width = self.width() - 40  # Ajustar al ancho disponible
        self.lista_deudas.setMinimumWidth(new_width)
        super().resizeEvent(event)

    def mostrar_deudas(self):
        self.lista_deudas.clear()
        self.cursor.execute("""
            SELECT d.id, d.nombre_deudor, d.monto, d.fecha
            FROM deudas d
            JOIN ventas v ON d.venta_id = v.id
            WHERE d.pagado = 0
        """)
        deudas = self.cursor.fetchall()
        if not deudas:
            self.lista_deudas.addItem("No hay deudas pendientes.")
            self.lista_deudas.setEnabled(False)
            self.marcar_pagada_btn.setEnabled(False)
            return

        self.lista_deudas.setEnabled(True)
        self.marcar_pagada_btn.setEnabled(True)
        for deuda in deudas:
            item_text = f"Deudor: {deuda[1]}, Monto: {deuda[2]}, Fecha: {deuda[3]}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, deuda[0])
            self.lista_deudas.addItem(item)

    def marcar_pagada(self):
        selected_item = self.lista_deudas.currentItem()
        if not selected_item:
            return

        deuda_id = selected_item.data(Qt.UserRole)
        self.cursor.execute("UPDATE deudas SET pagado = 1 WHERE id = ?", (deuda_id,))
        self.conn.commit()
        self.mostrar_deudas()
        self.deuda_pagada.emit()

    def actualizar(self):
        self.mostrar_deudas()