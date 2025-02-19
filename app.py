import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
import json
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def obtener_clima(ciudad):
    api_key = "4bcbbd484b64ae5160c180c82a3db758"
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={ciudad}&appid={api_key}&units=metric&lang=es"
    respuesta = requests.get(url)
    datos = respuesta.json()
    
    if datos["cod"] == "200":
        pronostico = [(item["dt_txt"].split(" ")[1][:5], item["main"]["temp"]) for item in datos["list"][:6]]
        temperatura_actual = datos["list"][0]["main"]["temp"]
        descripcion = datos["list"][0]["weather"][0]["description"].capitalize()
        icono = datos["list"][0]["weather"][0]["icon"]
        return temperatura_actual, descripcion, icono, pronostico
    else:
        return None, "No se pudo obtener los datos del clima", None, []

def actualizar_clima():
    ciudad = entrada_ciudad.get()
    temperatura, descripcion, icono, pronostico = obtener_clima(ciudad)
    
    if temperatura is not None:
        etiqueta_temp.config(text=f"{temperatura}°C")
        etiqueta_desc.config(text=descripcion)
        cargar_icono(icono)
        actualizar_grafico(pronostico)
    else:
        etiqueta_temp.config(text="--")
        etiqueta_desc.config(text=descripcion)

def cargar_icono(icono):
    url = f"http://openweathermap.org/img/wn/{icono}@2x.png"
    img_data = requests.get(url).content
    img = Image.open(io.BytesIO(img_data))
    img = img.resize((100, 100), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    etiqueta_icono.config(image=img_tk)
    etiqueta_icono.image = img_tk

def actualizar_grafico(pronostico):
    for widget in frame_grafica.winfo_children():
        widget.destroy()
    
    if pronostico:
        tiempos, temperaturas = zip(*pronostico)
        figura, ax = plt.subplots(figsize=(5, 2), dpi=100)
        ax.plot(tiempos, temperaturas, marker='o', linestyle='-', color='orange')
        ax.set_ylabel("°C")
        ax.set_title("Temperatura próximas horas")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        canvas = FigureCanvasTkAgg(figura, master=frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack()

ventana = tk.Tk()
ventana.title("Clima App")
ventana.geometry("400x700")
ventana.configure(bg="#87CEEB")

frame_superior = tk.Frame(ventana, bg="#FFA500", height=150)
frame_superior.pack(fill="x")

etiqueta_titulo = tk.Label(frame_superior, text="Clima App", font=("Arial", 18, "bold"), bg="#FFA500", fg="white")
etiqueta_titulo.pack(pady=20)

entrada_ciudad = ttk.Entry(ventana, font=("Arial", 14))
entrada_ciudad.pack(pady=10, ipadx=10, ipady=5)

boton_obtener = ttk.Button(ventana, text="Obtener Clima", command=actualizar_clima)
boton_obtener.pack(pady=10)

etiqueta_icono = tk.Label(ventana, bg="#87CEEB")
etiqueta_icono.pack(pady=10)

etiqueta_temp = tk.Label(ventana, text="--°C", font=("Arial", 28), bg="#87CEEB", fg="black")
etiqueta_temp.pack()

etiqueta_desc = tk.Label(ventana, text="", font=("Arial", 14), bg="#87CEEB", fg="black")
etiqueta_desc.pack()

frame_grafica = tk.Frame(ventana, bg="#87CEEB")
frame_grafica.pack(pady=10)

ventana.mainloop()