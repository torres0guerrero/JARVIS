import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import string

# Variable global para guardar las apps encontradas
apps_encontradas = {}

# FUNCIONES DE LECTURA DE DISCOS
def obtener_discos():
    # Detecta qué discos existen
    discos_conectados = []
    for letra in string.ascii_uppercase:
        disco = f"{letra}:\\"
        if os.path.exists(disco):
            discos_conectados.append(disco)
    return discos_conectados

# FUNCIONES DE CONFIGURACIÓN Y MANUAL
def cargar_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return {"nombre_ia": "jarvis", "idioma": "es-MX", "webs_personalizadas": {}, "apps_personalizadas": {}}

def guardar_config(datos):
    with open('config.json', 'w', encoding='utf-8') as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

def guardar_basicos():
    datos = cargar_config()
    datos["nombre_ia"] = entrada_nombre.get().strip().lower()
    datos["idioma"] = combo_idioma.get()
    guardar_config(datos)
    messagebox.showinfo("Guardado", "Configuración básica actualizada.")

def generar_manual():
    datos = cargar_config()
    nombre = datos.get("nombre_ia", "jarvis").capitalize()
    escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
    ruta_archivo = os.path.join(escritorio, f"Manual_Comandos_{nombre}.txt")
    
    try:
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(f"=== MANUAL DE COMANDOS PARA {nombre.upper()} ===\n\n")
            f.write(f"Recuerda decir el nombre de tu asistente antes de la orden.\n")
            f.write("--- 1. COMANDOS BÁSICOS ---\n")
            f.write("- 'qué hora es' / 'time' -> Te dice la hora actual.\n")
            f.write("- 'apagar' / 'descansa' -> Cierra el asistente.\n\n")
            
            f.write("--- 2. PÁGINAS WEB ---\n")
            for cmd, url in datos.get("webs_personalizadas", {}).items():
                f.write(f"- '{cmd}' -> Abre web.\n")
            
            f.write("\n--- 3. APLICACIONES ---\n")
            for cmd, ruta in datos.get("apps_personalizadas", {}).items():
                nombre_app = os.path.basename(ruta).replace('.lnk', '').replace('.exe', '')
                f.write(f"- '{cmd}' -> Abre: {nombre_app}\n")
                
        messagebox.showinfo("Éxito", f"¡Manual guardado en:\n{ruta_archivo}")
        os.startfile(ruta_archivo)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# FUNCIONES DE WEBS
def agregar_web():
    comando = entrada_comando_web.get().strip().lower()
    url = entrada_url.get().strip()
    if comando and url:
        datos = cargar_config()
        datos["webs_personalizadas"][comando] = url
        guardar_config(datos)
        entrada_comando_web.delete(0, tk.END)
        entrada_url.delete(0, tk.END)
        actualizar_listas()

# FUNCIONES DEL ESCÁNER AVANZADO DE APPS
def escanear_disco():
    disco_seleccionado = combo_discos.get()
    if not disco_seleccionado:
        messagebox.showwarning("Atención", "Selecciona un disco primero.")
        return

    boton_escanear.config(text="Escaneando... (Esto tardará un momento)", state="disabled")
    ventana.update()
    
    apps_encontradas.clear()
    
    # Carpetas que ignora
    carpetas_ignoradas = ['windows', 'temp', 'appdata', 'programdata']
    
    for raiz, carpetas, archivos in os.walk(disco_seleccionado):
        # Filtro de carpetas
        carpetas[:] = [c for c in carpetas if c.lower() not in carpetas_ignoradas]
        
        for archivo in archivos:
            if archivo.lower().endswith('.exe'):
                # Ignora desinstaladores
                if "uninstall" not in archivo.lower() and "unins000" not in archivo.lower():
                    nombre_limpio = archivo[:-4] # Quita el .exe
                    ruta_completa = os.path.join(raiz, archivo)
                    apps_encontradas[nombre_limpio] = ruta_completa
                        
    nombres_apps = sorted(list(apps_encontradas.keys()))
    combo_apps['values'] = nombres_apps
    
    boton_escanear.config(text="1. Escanear Disco", state="normal")
    messagebox.showinfo("Escaneo Completo", f"Se encontraron {len(nombres_apps)} archivos .exe en el disco {disco_seleccionado}.")

def buscar_manual():
    # Abre el explorador de Windows
    ruta = filedialog.askopenfilename(title="Selecciona el ejecutable (.exe)", filetypes=[("Archivos EXE", "*.exe")])
    if ruta:
        nombre_limpio = os.path.basename(ruta)[:-4]
        apps_encontradas[nombre_limpio] = ruta
        combo_apps['values'] = list(apps_encontradas.keys())
        combo_apps.set(nombre_limpio)
        messagebox.showinfo("Cargado", f"{nombre_limpio} listo para ser vinculado.")

def agregar_app():
    nombre_seleccionado = combo_apps.get()
    comando = entrada_comando_app.get().strip().lower()
    
    if not nombre_seleccionado or not comando:
        messagebox.showwarning("Faltan datos", "Selecciona una app y escribe el comando de voz.")
        return
        
    ruta = apps_encontradas.get(nombre_seleccionado)
    
    datos = cargar_config()
    datos["apps_personalizadas"][comando] = ruta
    guardar_config(datos)
    
    entrada_comando_app.delete(0, tk.END)
    combo_apps.set('')
    actualizar_listas()
    messagebox.showinfo("Éxito", f"App vinculada al comando: '{comando}'")

def actualizar_listas():
    lista_webs.delete(0, tk.END)
    lista_apps.delete(0, tk.END)
    datos = cargar_config()
    
    for cmd, url in datos.get("webs_personalizadas", {}).items():
        lista_webs.insert(tk.END, f"Comando: '{cmd}' -> {url}")
        
    for cmd, ruta in datos.get("apps_personalizadas", {}).items():
        nombre_archivo = os.path.basename(ruta)
        lista_apps.insert(tk.END, f"Comando: '{cmd}' -> {nombre_archivo}")

# DISEÑO UI
ventana = tk.Tk()
ventana.title("Panel de Control del Asistente")
ventana.geometry("600x550")

cuaderno = ttk.Notebook(ventana)
cuaderno.pack(fill="both", expand=True, padx=10, pady=10)

pestaña_general = ttk.Frame(cuaderno)
pestaña_apps = ttk.Frame(cuaderno)
cuaderno.add(pestaña_general, text="General y Webs")
cuaderno.add(pestaña_apps, text="Aplicaciones (.exe)")

config_actual = cargar_config()

# GENERAL
tk.Label(pestaña_general, text="Nombre de tu IA:").pack(anchor="w", pady=(10,0), padx=10)
entrada_nombre = tk.Entry(pestaña_general, width=40)
entrada_nombre.insert(0, config_actual.get("nombre_ia", "jarvis"))
entrada_nombre.pack(anchor="w", padx=10)

tk.Label(pestaña_general, text="Idioma:").pack(anchor="w", pady=(10,0), padx=10)
combo_idioma = ttk.Combobox(pestaña_general, values=["es-MX", "en-US", "es-ES"], state="readonly", width=37)
combo_idioma.set(config_actual.get("idioma", "es-MX"))
combo_idioma.pack(anchor="w", padx=10)

tk.Button(pestaña_general, text="Guardar Básico", command=guardar_basicos).pack(anchor="w", pady=10, padx=10)
tk.Button(pestaña_general, text="Generar Manual de Comandos", command=generar_manual, bg="#2196F3", fg="white").pack(anchor="w", padx=10)
tk.Label(pestaña_general, text="-"*80).pack(pady=5)

tk.Label(pestaña_general, text="Añadir Webs (Comando / URL):").pack(anchor="w", padx=10)
entrada_comando_web = tk.Entry(pestaña_general, width=20)
entrada_comando_web.pack(side=tk.LEFT, padx=(10, 5))
entrada_url = tk.Entry(pestaña_general, width=35)
entrada_url.pack(side=tk.LEFT, padx=5)
tk.Button(pestaña_general, text="Añadir", command=agregar_web).pack(side=tk.LEFT, padx=5)

lista_webs = tk.Listbox(pestaña_general, width=80, height=8)
lista_webs.pack(side=tk.BOTTOM, padx=10, pady=20)

# ESCÁNER DE DISCOS
marco_discos = tk.Frame(pestaña_apps)
marco_discos.pack(anchor="w", pady=10, padx=10)

tk.Label(marco_discos, text="Discos detectados:").pack(side=tk.LEFT)
combo_discos = ttk.Combobox(marco_discos, values=obtener_discos(), state="readonly", width=10)
if obtener_discos(): combo_discos.set(obtener_discos()[0])
combo_discos.pack(side=tk.LEFT, padx=5)

boton_escanear = tk.Button(marco_discos, text="1. Escanear Disco", command=escanear_disco, bg="#FF9800", fg="white")
boton_escanear.pack(side=tk.LEFT, padx=5)

tk.Button(marco_discos, text="Buscar manual (.exe)", command=buscar_manual).pack(side=tk.LEFT, padx=5)

tk.Label(pestaña_apps, text="2. Selecciona el ejecutable encontrado:").pack(anchor="w", pady=(10,0), padx=10)
combo_apps = ttk.Combobox(pestaña_apps, state="readonly", width=50)
combo_apps.pack(anchor="w", padx=10)

tk.Label(pestaña_apps, text="3. Palabra clave para abrirlo (ej. gta):").pack(anchor="w", pady=(10,0), padx=10)
entrada_comando_app = tk.Entry(pestaña_apps, width=40)
entrada_comando_app.pack(anchor="w", padx=10)

tk.Button(pestaña_apps, text="Vincular Aplicación", command=agregar_app, bg="#4CAF50", fg="white").pack(anchor="w", pady=10, padx=10)

tk.Label(pestaña_apps, text="Tus apps actuales:").pack(anchor="w", padx=10)
lista_apps = tk.Listbox(pestaña_apps, width=80, height=8)
lista_apps.pack(anchor="w", padx=10, pady=5)

actualizar_listas()
ventana.mainloop()