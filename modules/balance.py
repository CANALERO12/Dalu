from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt

class BalanceWidget(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Balance")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1A3C6D; margin-bottom: 20px;")
        layout.addWidget(title)

        self.label_ingresos = QLabel("Ingresos: $0.00")
        self.label_ingresos.setStyleSheet("font-size: 16px; color: #1A3C6D;")
        layout.addWidget(self.label_ingresos)

        self.label_gastos = QLabel("Gastos: $0.00")
        self.label_gastos.setStyleSheet("font-size: 16px; color: #1A3C6D;")
        layout.addWidget(self.label_gastos)

        self.label_deudas = QLabel("Deudas Pendientes: $0.00")
        self.label_deudas.setStyleSheet("font-size: 16px; color: #1A3C6D;")
        layout.addWidget(self.label_deudas)

        self.label_balance = QLabel("Balance: $0.00")
        self.label_balance.setStyleSheet("font-size: 18px; font-weight: bold; color: #1A3C6D;")
        layout.addWidget(self.label_balance)

        self.tabla_transacciones = QTableWidget()
        self.tabla_transacciones.setRowCount(0)
        self.tabla_transacciones.setColumnCount(4)
        self.tabla_transacciones.setHorizontalHeaderLabels(["Tipo", "Monto ($)", "Descripción", "Fecha"])
        self.tabla_transacciones.setStyleSheet("""
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
        self.tabla_transacciones.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_transacciones.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_transacciones.setWordWrap(True)
        self.tabla_transacciones.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_transacciones.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Tipo
        self.tabla_transacciones.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Monto
        self.tabla_transacciones.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Descripción
        self.tabla_transacciones.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Fecha
        self.tabla_transacciones.verticalHeader().setDefaultSectionSize(40)
        self.tabla_transacciones.setMinimumHeight(200)
        layout.addWidget(self.tabla_transacciones)

        self.setStyleSheet("background-color: #F5F7FA;")
        self.setLayout(layout)
        self.calcular_balance()

    def resizeEvent(self, event):
        self.tabla_transacciones.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla_transacciones.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla_transacciones.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla_transacciones.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        super().resizeEvent(event)

    def calcular_balance(self):
        self.tabla_transacciones.setRowCount(0)

        # Calcular ingresos (ventas pagadas al contado y deudas pagadas)
        self.cursor.execute("SELECT SUM(total) FROM ventas WHERE tipo_pago = 'contado'")
        ingresos_contado = self.cursor.fetchone()[0] or 0.0
        self.cursor.execute("SELECT SUM(monto) FROM deudas WHERE pagado = 1")
        ingresos_deudas_pagadas = self.cursor.fetchone()[0] or 0.0
        ingresos = ingresos_contado + ingresos_deudas_pagadas

        # Calcular gastos
        self.cursor.execute("SELECT SUM(monto) FROM gastos")
        gastos = self.cursor.fetchone()[0] or 0.0

        # Calcular deudas pendientes
        self.cursor.execute("SELECT SUM(monto) FROM deudas WHERE pagado = 0")
        deudas_pendientes = self.cursor.fetchone()[0] or 0.0

        # Calcular balance
        balance = ingresos - gastos

        # Actualizar etiquetas
        self.label_ingresos.setText(f"Ingresos: ${ingresos:.2f}")
        self.label_gastos.setText(f"Gastos: ${gastos:.2f}")
        self.label_deudas.setText(f"Deudas Pendientes: ${deudas_pendientes:.2f}")
        self.label_balance.setText(f"Balance: ${balance:.2f}")
        print(f"Balance actualizado: Ingresos=${ingresos:.2f}, Gastos=${gastos:.2f}, Deudas pendientes=${deudas_pendientes:.2f}, Balance=${balance:.2f}")

        # Cargar transacciones en la tabla
        # Ventas al contado
        self.cursor.execute("SELECT total, producto_nombre, fecha FROM ventas WHERE tipo_pago = 'contado'")
        ventas_contado = self.cursor.fetchall()
        for total, producto, fecha in ventas_contado:
            row_position = self.tabla_transacciones.rowCount()
            self.tabla_transacciones.insertRow(row_position)
            self.tabla_transacciones.setItem(row_position, 0, QTableWidgetItem("Venta (Contado)"))
            self.tabla_transacciones.setItem(row_position, 1, QTableWidgetItem(f"${total:.2f}"))
            self.tabla_transacciones.setItem(row_position, 2, QTableWidgetItem(f"Venta de {producto}"))
            self.tabla_transacciones.setItem(row_position, 3, QTableWidgetItem(fecha))

        # Deudas pagadas
        self.cursor.execute("SELECT monto, nombre_deudor, fecha FROM deudas WHERE pagado = 1")
        deudas_pagadas = self.cursor.fetchall()
        for monto, deudor, fecha in deudas_pagadas:
            row_position = self.tabla_transacciones.rowCount()
            self.tabla_transacciones.insertRow(row_position)
            self.tabla_transacciones.setItem(row_position, 0, QTableWidgetItem("Deuda Pagada"))
            self.tabla_transacciones.setItem(row_position, 1, QTableWidgetItem(f"${monto:.2f}"))
            self.tabla_transacciones.setItem(row_position, 2, QTableWidgetItem(f"Pago de {deudor}"))
            self.tabla_transacciones.setItem(row_position, 3, QTableWidgetItem(fecha))

        # Gastos
        self.cursor.execute("SELECT monto, descripcion, fecha FROM gastos")
        gastos = self.cursor.fetchall()
        for monto, descripcion, fecha in gastos:
            row_position = self.tabla_transacciones.rowCount()
            self.tabla_transacciones.insertRow(row_position)
            self.tabla_transacciones.setItem(row_position, 0, QTableWidgetItem("Gasto"))
            self.tabla_transacciones.setItem(row_position, 1, QTableWidgetItem(f"$-{monto:.2f}"))
            self.tabla_transacciones.setItem(row_position, 2, QTableWidgetItem(descripcion))
            self.tabla_transacciones.setItem(row_position, 3, QTableWidgetItem(fecha))

        if self.tabla_transacciones.rowCount() == 0:
            self.tabla_transacciones.setRowCount(1)
            self.tabla_transacciones.setItem(0, 0, QTableWidgetItem("No hay transacciones."))
