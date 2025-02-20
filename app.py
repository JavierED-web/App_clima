from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGraphicsOpacityEffect, QProgressBar
from PyQt6.QtCore import QEasingCurve, QTimer
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QPropertyAnimation
import requests
import sys
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class ClimaApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.actualizar_clima("Bogotá")  # Cargar Bogotá al iniciar

    def initUI(self):
        self.setWindowTitle("Clima App")
        self.setGeometry(100, 100, 500, 700)
        self.setStyleSheet("background-color: #2c3e50; color: white;")

        self.layout = QVBoxLayout()
        
        self.titulo = QLabel("Clima", self)
        self.titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.titulo)
        
        self.entrada_ciudad = QLineEdit(self)
        self.entrada_ciudad.setPlaceholderText("Ingrese la ciudad")
        self.entrada_ciudad.setStyleSheet("padding: 10px; border-radius: 5px; background-color: white; color: black;")
        self.layout.addWidget(self.entrada_ciudad)
        
        self.boton_obtener = QPushButton("Obtener Clima", self)
        self.boton_obtener.setStyleSheet("background-color: #e67e22; color: white; padding: 10px; border-radius: 5px;")
        self.boton_obtener.clicked.connect(lambda: self.actualizar_clima(self.entrada_ciudad.text()))
        self.layout.addWidget(self.boton_obtener)

        # Barra de carga
        self.barra_carga = QProgressBar(self)
        self.barra_carga.setMaximum(100)
        self.barra_carga.setValue(0)
        self.barra_carga.setStyleSheet("QProgressBar { border-radius: 5px; } QProgressBar::chunk { background-color: #27ae60; }")
        self.layout.addWidget(self.barra_carga)
        self.barra_carga.hide()  # Ocultar al inicio

        self.etiqueta_icono = QLabel(self)
        self.etiqueta_icono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.etiqueta_icono)
        
        self.etiqueta_temp = QLabel("--°C", self)
        self.etiqueta_temp.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.etiqueta_temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.etiqueta_temp)
        
        self.etiqueta_desc = QLabel("", self)
        self.etiqueta_desc.setFont(QFont("Arial", 14))
        self.etiqueta_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.etiqueta_desc)
        
        self.canvas = FigureCanvas(plt.figure())
        self.layout.addWidget(self.canvas)
        
        self.setLayout(self.layout)

        self.initAnimations()

    def initAnimations(self):
        self.efecto_opacidad_temp = QGraphicsOpacityEffect(self.etiqueta_temp)
        self.etiqueta_temp.setGraphicsEffect(self.efecto_opacidad_temp)
        self.animacion_temp = QPropertyAnimation(self.efecto_opacidad_temp, b"opacity")

        self.efecto_opacidad_desc = QGraphicsOpacityEffect(self.etiqueta_desc)
        self.etiqueta_desc.setGraphicsEffect(self.efecto_opacidad_desc)
        self.animacion_desc = QPropertyAnimation(self.efecto_opacidad_desc, b"opacity")

        self.efecto_opacidad_icono = QGraphicsOpacityEffect(self.etiqueta_icono)
        self.etiqueta_icono.setGraphicsEffect(self.efecto_opacidad_icono)
        self.animacion_icono = QPropertyAnimation(self.efecto_opacidad_icono, b"opacity")

    def obtener_clima(self, ciudad):
        api_key = "4bcbbd484b64ae5160c180c82a3db758"
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={ciudad}&appid={api_key}&units=metric&lang=es"
        respuesta = requests.get(url)
        datos = respuesta.json()
        
        if datos.get("cod") != "200":
            return None, "No se pudo obtener los datos del clima", None, []
        
        primer_item = datos["list"][0]
        temperatura_actual = primer_item["main"]["temp"]
        descripcion = primer_item["weather"][0]["description"].capitalize()
        icono = primer_item["weather"][0]["icon"]
        
        pronostico = [(item["dt_txt"].split(" ")[1][:5], item["main"]["temp"]) for item in datos["list"][:6]]
        
        return temperatura_actual, descripcion, icono, pronostico

    def actualizar_clima(self, ciudad):
        self.barra_carga.show()
        self.barra_carga.setValue(0)
        self.simular_progreso()

        temperatura, descripcion, icono, pronostico = self.obtener_clima(ciudad)
        
        if temperatura is not None:
            self.animar_aparicion(self.animacion_temp, self.etiqueta_temp, f"{temperatura}°C")
            self.animar_aparicion(self.animacion_desc, self.etiqueta_desc, descripcion)
            self.cargar_icono(icono)
            self.actualizar_grafico(pronostico)
        else:
            self.etiqueta_temp.setText("--°C")
            self.etiqueta_desc.setText(descripcion)

        self.barra_carga.setValue(100)
        QTimer.singleShot(500, self.barra_carga.hide)  # Oculta la barra después de 500ms

    def simular_progreso(self):
        for i in range(1, 101, 20):
            QTimer.singleShot(i * 10, lambda v=i: self.barra_carga.setValue(v))

    def cargar_icono(self, icono):
        url = f"http://openweathermap.org/img/wn/{icono}@2x.png"
        img_data = requests.get(url).content
        pixmap = QPixmap()
        pixmap.loadFromData(img_data)
        self.animar_aparicion(self.animacion_icono, self.etiqueta_icono, pixmap)

    def actualizar_grafico(self, pronostico):
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        tiempos, temperaturas = zip(*pronostico)
        ax.plot(tiempos, temperaturas, marker='o', linestyle='-', color='orange')
        ax.set_ylabel("°C")
        ax.set_title("Temperatura próximas horas")
        self.canvas.draw()

    def animar_aparicion(self, animacion, widget, nuevo_valor):
        if animacion.state() == QPropertyAnimation.State.Running:
            animacion.stop()
        
        if isinstance(nuevo_valor, QPixmap):
            widget.setPixmap(nuevo_valor)
        else:
            widget.setText(nuevo_valor)
        
        animacion.setDuration(2000)
        animacion.setStartValue(0.0)
        animacion.setEndValue(1.0)
        animacion.setEasingCurve(QEasingCurve.Type.OutCubic)
        animacion.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ClimaApp()
    ventana.show()
    sys.exit(app.exec())
