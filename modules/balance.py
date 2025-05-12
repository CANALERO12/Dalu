import sqlite3
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import matplotlib.pyplot as plt
import numpy as np
import os

class BalanceWidget(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.init_ui()
        self.calcular_balance()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Etiqueta para el título
        self.title_label = QLabel("Balance")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A3C6D; margin-bottom: 10px;")
        layout.addWidget(self.title_label)

        # Área de texto para mostrar el balance
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
        layout.addWidget(self.resultado_texto)

        # Etiqueta para el gráfico
        self.grafico_label = QLabel()
        self.grafico_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.grafico_label)

        self.setStyleSheet("background-color: #F5F7FA;")
        self.setLayout(layout)

    def calcular_balance(self):
        # Calcular balance basado en todas las ventas
        self.cursor.execute("SELECT SUM(total) FROM ventas")
        total_ventas = self.cursor.fetchone()[0] or 0

        self.cursor.execute("SELECT SUM(monto) FROM deudas WHERE pagado = 0")
        deudas_pendientes = self.cursor.fetchone()[0] or 0

        self.cursor.execute("SELECT SUM(monto) FROM gastos")
        total_gastos = self.cursor.fetchone()[0] or 0

        balance = total_ventas - deudas_pendientes - total_gastos
        self.resultado_texto.clear()
        self.resultado_texto.append(f"Total Ventas: ${total_ventas:.2f}")
        self.resultado_texto.append(f"Deudas Pendientes: ${deudas_pendientes:.2f}")
        self.resultado_texto.append(f"Total Gastos: ${total_gastos:.2f}")
        self.resultado_texto.append(f"Balance: ${balance:.2f}")

        # Generar el gráfico
        self.generar_grafico(total_ventas, deudas_pendientes, total_gastos, balance)

    def generar_grafico(self, total_ventas, deudas_pendientes, total_gastos, balance):
        # Datos para el gráfico
        categorias = ['Ventas', 'Deudas', 'Gastos', 'Balance']
        valores = [total_ventas, deudas_pendientes, total_gastos, balance]
        
        # Crear gráfico de barras
        plt.figure(figsize=(6, 4), dpi=300)  # Aumentar la resolución a 300 DPI
        plt.bar(categorias, valores, color=['#4A90E2', '#FF6347', '#FFA500', '#32CD32'])
        plt.title('Resumen Financiero', fontsize=12)
        plt.ylabel('Monto ($)', fontsize=10)
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)

        # Guardar el gráfico como imagen
        plt.savefig('balance_grafico.png', bbox_inches='tight', pad_inches=0.1)
        plt.close()

        # Mostrar el gráfico en el QLabel con mejor escalado
        pixmap = QPixmap('balance_grafico.png')
        if not pixmap.isNull():
            self.grafico_label.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.grafico_label.setText("Error al cargar el gráfico")

        # Limpiar el archivo generado
        if os.path.exists('balance_grafico.png'):
            os.remove('balance_grafico.png')