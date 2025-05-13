from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
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
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.title_label = QLabel("Deudas Pendientes")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A3C6D; margin-bottom: 10px;")
        layout.addWidget(self.title_label)

        self.tabla_deudas = QTableWidget()
        self.tabla_deudas.setRowCount(0)
        self.tabla_deudas.setColumnCount(5)
        self.tabla_deudas.setHorizontalHeaderLabels(["Deudor", "Monto ($)", "Fecha", "Venta ID", "Acción"])
        self.tabla_deudas.setStyleSheet("""
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
        self.tabla_deudas.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_deudas.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_deudas.setWordWrap(True)
        self.tabla_deudas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_deudas.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Deudor
        self.tabla_deudas.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Monto
        self.tabla_deudas.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Fecha
        self.tabla_deudas.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Venta ID
        self.tabla_deudas.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)  # Acción
        self.tabla_deudas.setColumnWidth(4, 100)
        self.tabla_deudas.verticalHeader().setDefaultSectionSize(40)
        self.tabla_deudas.setMinimumHeight(200)
        layout.addWidget(self.tabla_deudas)

        self.setStyleSheet("background-color: #F5F7FA;")
        self.setLayout(layout)
        self.mostrar_deudas()

    def resizeEvent(self, event):
        self.tabla_deudas.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_deudas.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla_deudas.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla_deudas.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabla_deudas.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        super().resizeEvent(event)

    def mostrar_deudas(self):
        self.tabla_deudas.setRowCount(0)
        self.cursor.execute("""
            SELECT d.id, d.nombre_deudor, d.monto, d.fecha, d.venta_id
            FROM deudas d
            JOIN ventas v ON d.venta_id = v.id
            WHERE d.pagado = 0
        """)
        deudas = self.cursor.fetchall()
        if not deudas:
            self.tabla_deudas.setRowCount(1)
            self.tabla_deudas.setItem(0, 0, QTableWidgetItem("No hay deudas pendientes."))
            print("No se encontraron deudas pendientes.")
            return

        for deuda in deudas:
            deuda_id, nombre_deudor, monto, fecha, venta_id = deuda
            row_position = self.tabla_deudas.rowCount()
            self.tabla_deudas.insertRow(row_position)
            self.tabla_deudas.setItem(row_position, 0, QTableWidgetItem(nombre_deudor))
            self.tabla_deudas.setItem(row_position, 1, QTableWidgetItem(f"${monto:.2f}"))
            self.tabla_deudas.setItem(row_position, 2, QTableWidgetItem(fecha))
            self.tabla_deudas.setItem(row_position, 3, QTableWidgetItem(str(venta_id)))
            btn_pagar = QPushButton("Pagar")
            btn_pagar.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4A90E2, stop:1 #357ABD);
                    color: white;
                    border: none;
                    padding: 3px 6px;
                    font-size: 11px;
                    font-weight: bold;
                    border-radius: 5px;
                    min-width: 80px;
                    min-height: 20px;
                }
                QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6AA8F7, stop:1 #4A90E2); }
                QPushButton:pressed { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #357ABD, stop:1 #2A5F9A); }
            """)
            btn_pagar.clicked.connect(lambda checked, d_id=deuda_id: self.marcar_pagada(d_id))
            self.tabla_deudas.setCellWidget(row_position, 4, btn_pagar)
        print(f"Se cargaron {len(deudas)} deudas pendientes.")

    def marcar_pagada(self, deuda_id):
        self.cursor.execute("UPDATE deudas SET pagado = 1 WHERE id = ?", (deuda_id,))
        self.conn.commit()
        print(f"Deuda con ID {deuda_id} marcada como pagada.")
        self.mostrar_deudas()
        self.deuda_pagada.emit()

    def actualizar(self):
        print("Actualizando lista de deudas...")
        self.mostrar_deudas()