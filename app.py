from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QSizePolicy, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QPixmap
import qtawesome as qta
import requests
import sys

class ClimaApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.actualizar_clima("Bogotá")  # Cargar Bogotá al iniciar

    def initUI(self):
        self.setGeometry(100, 100, 500, 700)
        self.setStyleSheet("background-color: #2c3e50; color: white;")
        
        # Icono estático de la ventana (un sol)
        self.setWindowIcon(QIcon("./assets/icono.ico"))  # Asegúrate de que esta ruta sea correcta
        
        self.layout = QVBoxLayout()
        
        # Imagen del clima (se actualizará dinámicamente)
        self.imagen_clima = QLabel(self)
        self.imagen_clima.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.imagen_clima)
        
        # Historial de ciudades
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
    
    def obtener_clima(self, ciudad):
        api_key = "4bcbbd484b64ae5160c180c82a3db758"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={api_key}&units=metric&lang=es"
        respuesta = requests.get(url)
        datos = respuesta.json()
        
        if datos.get("cod") != 200:
            return None, "No se pudo obtener los datos del clima", None
        
        temperatura_actual = datos["main"]["temp"]
        descripcion = datos["weather"][0]["description"].capitalize()
        icono_clima = datos["weather"][0]["icon"]  # Icono del clima de OpenWeather
        
        return temperatura_actual, descripcion, icono_clima
    
    def actualizar_clima(self, ciudad):
        temperatura, descripcion, icono_clima = self.obtener_clima(ciudad)
        
        if temperatura is not None:
            self.etiqueta_temp.setText(f"{temperatura}°C")
            self.etiqueta_desc.setText(descripcion)
            self.actualizar_recomendaciones(temperatura)
            self.agregar_al_historial(ciudad)
            self.setWindowTitle(f"El Clima en {ciudad}")
            
            # Cargar imagen del clima desde OpenWeather
            url_imagen = f"http://openweathermap.org/img/wn/{icono_clima}@2x.png"
            pixmap = QPixmap()
            pixmap.loadFromData(requests.get(url_imagen).content)
            self.imagen_clima.setPixmap(pixmap)
            
            # Cambiar colores según temperatura
            if temperatura >= 20:
                self.setStyleSheet("background-color: #FADA7A; color: black;")
            else:
                self.setStyleSheet("background-color: #2c3e50; color: white;")
        else:
            self.etiqueta_temp.setText("--°C")
            self.etiqueta_desc.setText(descripcion)
            self.imagen_clima.clear()
    
    def actualizar_recomendaciones(self, temperatura):
        for i in reversed(range(self.recomendaciones_layout.count())):
            self.recomendaciones_layout.itemAt(i).widget().deleteLater()
        
        recomendaciones = [
            ("Usa ropa ligera", qta.icon("fa5s.sun", color="black")),
            ("Lleva gafas de sol", qta.icon("fa5s.glasses", color="black")),
            ("Hidrátate bien", qta.icon("fa5s.tint", color="black"))
        ] if temperatura >= 20 else [
            ("Usa abrigo", qta.icon("fa5s.user", color="black")),
            ("Protégete del viento", qta.icon("fa5s.wind", color="black"))
        ]
        
        for texto, icono in recomendaciones:
            contenedor = QFrame()
            contenedor.setStyleSheet("background-color: #DF9755; padding: 10px; border-radius: 10px;")
            contenedor_layout = QHBoxLayout()
            
            contenedor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            
            contenedor_layout = QHBoxLayout()
            contenedor_layout.setContentsMargins(10, 5, 10, 5)  # Espaciado interno
            contenedor_layout.setSpacing(10)  # Espaciado entre icono y texto
            contenedor_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            icon_label = QLabel()
            icon_label.setPixmap(icono.pixmap(32, 32))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            
            text_label = QLabel(texto)
            text_label.setFont(QFont("Arial", 12, QFont.Weight.Medium))
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_label.setStyleSheet("color: black")
            
            contenedor_layout.addWidget(icon_label)
            contenedor_layout.addWidget(text_label)
            contenedor_layout.addStretch()
            contenedor.setLayout(contenedor_layout)
            
            self.recomendaciones_layout.addWidget(contenedor)
    
    def agregar_al_historial(self, ciudad):
        if ciudad and ciudad not in [self.historial_ciudades.itemText(i) for i in range(self.historial_ciudades.count())]:
            self.historial_ciudades.addItem(ciudad)
    
    def seleccionar_ciudad(self):
        self.actualizar_clima(self.historial_ciudades.currentText())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ClimaApp()
    ventana.show()
    sys.exit(app.exec())
