from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QSizePolicy, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap
import qtawesome as qta
import requests
import sys
import json
import os

class ClimaWorker(QThread):
    datos_obtenidos = pyqtSignal(dict)
    error_obtenido = pyqtSignal(str)
    
    def __init__(self, ciudad, parent=None):
        super().__init__(parent)
        self.ciudad = ciudad

    def run(self):
        api_key = "4bcbbd484b64ae5160c180c82a3db758"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={self.ciudad}&appid={api_key}&units=metric&lang=es"
        try:
            respuesta = requests.get(url)
            datos = respuesta.json()
            if datos.get("cod") != 200:
                self.error_obtenido.emit("No se pudo obtener los datos del clima")
            else:
                self.datos_obtenidos.emit(datos)
        except Exception as e:
            self.error_obtenido.emit(str(e))

class ClimaApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cargar_historial()
        self.actualizar_clima("Bogotá")

    def initUI(self):
        self.setGeometry(100, 100, 500, 700)
        self.setStyleSheet("background-color: #2c3e50; color: white;")
        self.setWindowIcon(QIcon("./assets/icono.ico"))
        self.layout = QVBoxLayout()

        self.imagen_clima = QLabel(self)
        self.imagen_clima.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.imagen_clima)

        self.historial_ciudades = QComboBox(self)
        self.historial_ciudades.setEditable(True)
        self.historial_ciudades.setStyleSheet("padding: 5px; border-radius: 5px; background-color: white; color: black;")
        self.historial_ciudades.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.historial_ciudades.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)
        self.historial_ciudades.setFixedHeight(30)
        self.historial_ciudades.activated.connect(self.seleccionar_ciudad)
        self.layout.addWidget(self.historial_ciudades)

        self.boton_obtener = QPushButton("Obtener Clima", self)
        self.boton_obtener.setStyleSheet("background-color: #3674B5; color: white; padding: 10px; border-radius: 5px;")
        self.boton_obtener.clicked.connect(lambda: self.actualizar_clima(self.historial_ciudades.currentText()))
        self.layout.addWidget(self.boton_obtener)

        self.etiqueta_temp = QLabel("--°C", self)
        self.etiqueta_temp.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.etiqueta_temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.etiqueta_temp)

        self.etiqueta_desc = QLabel("", self)
        self.etiqueta_desc.setFont(QFont("Arial", 14))
        self.etiqueta_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.etiqueta_desc)

        self.recomendaciones_layout = QVBoxLayout()
        self.layout.addLayout(self.recomendaciones_layout)

        self.setLayout(self.layout)

    def seleccionar_ciudad(self):
        ciudad_seleccionada = self.historial_ciudades.currentText()
        self.actualizar_clima(ciudad_seleccionada)

    def actualizar_clima(self, ciudad):
        self.worker = ClimaWorker(ciudad)
        self.worker.datos_obtenidos.connect(self.mostrar_clima)
        self.worker.error_obtenido.connect(self.mostrar_error)
        self.worker.start()
    
    def mostrar_clima(self, datos):
        temperatura = datos["main"]["temp"]
        descripcion = datos["weather"][0]["description"].capitalize()
        icono_clima = datos["weather"][0]["icon"]

        self.etiqueta_temp.setText(f"{temperatura}°C")
        self.etiqueta_desc.setText(descripcion)
        self.actualizar_recomendaciones(temperatura)
        self.agregar_al_historial(self.historial_ciudades.currentText())
        self.setWindowTitle(f"El Clima en {self.historial_ciudades.currentText()}")
        
        if temperatura < 20:
            self.setStyleSheet("background-color: #2c3e50; color: white")
        else:
            self.setStyleSheet("background-color: #FADA7A; color: black;")
        
        url_imagen = f"http://openweathermap.org/img/wn/{icono_clima}@2x.png"
        pixmap = QPixmap()
        pixmap.loadFromData(requests.get(url_imagen).content)
        self.imagen_clima.setPixmap(pixmap)
    
    def mostrar_error(self, mensaje):
        self.etiqueta_temp.setText("--°C")
        self.etiqueta_desc.setText(mensaje)
        self.imagen_clima.clear()
    
    def actualizar_recomendaciones(self, temperatura):
        while self.recomendaciones_layout.count():
            self.recomendaciones_layout.takeAt(0).widget().deleteLater()

        if temperatura >= 20:
            color_recomendacion = "#e67e22"
            recomendaciones = [
                ("Usa ropa ligera", qta.icon("fa5s.sun", color="black")),
                ("Lleva gafas de sol", qta.icon("fa5s.glasses", color="black")),
                ("Hidrátate bien", qta.icon("fa5s.tint", color="black"))
            ]
        else:
            color_recomendacion = "#3498db"
            recomendaciones = [
                ("Usa abrigo", qta.icon("fa5s.user", color="black")),
                ("Protégete del viento", qta.icon("fa5s.wind", color="black"))
            ]

        for texto, icono in recomendaciones:
            hbox = QHBoxLayout()
            icono_label = QLabel()
            icono_label.setPixmap(icono.pixmap(24, 24))
            texto_label = QLabel(texto)
            texto_label.setFont(QFont("Arial", 12))
            hbox.addWidget(icono_label)
            hbox.addWidget(texto_label)
            frame = QFrame()
            frame.setLayout(hbox)
            frame.setStyleSheet(f"background-color: {color_recomendacion}; padding: 10px; border-radius: 5px;")
            self.recomendaciones_layout.addWidget(frame)
    def cargar_historial(self):
        if os.path.exists("historial.json"):
            with open("historial.json", "r") as archivo:
                historial = json.load(archivo)
                self.historial_ciudades.addItems(historial)
    def agregar_al_historial(self, ciudad):
        historial = [self.historial_ciudades.itemText(i) for i in range(self.historial_ciudades.count())]
        if ciudad not in historial:
            self.historial_ciudades.addItem(ciudad)
            historial.append(ciudad)
            with open("historial.json", "w") as archivo:
                json.dump(historial, archivo)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ClimaApp()
    ventana.show()
    sys.exit(app.exec())