import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import json
from google import genai
from google.genai import types

# CARGAR CONFIGURACIÓN
def cargar_configuracion():
    try:
        with open('config.json', 'r', encoding='utf-8') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        # Si no existe el archivo, usamos una configuración por defecto
        return {
            "nombre_ia": "jarvis",
            "idioma": "es-MX",
            "webs_personalizadas": {},
            "apps_personalizadas": {}
        }

config = cargar_configuracion()
NOMBRE_IA = config["nombre_ia"].lower()
IDIOMA = config["idioma"]

# CONFIGURACIÓN DEL CEREBRO IA
cliente_ia = genai.Client(api_key="TU_API_KEY_AQUI") 

# CONFIGURACIÓN DE VOZ
def hablar(texto):
    print(f"Jarvis: {texto}") 
    motor_voz = pyttsx3.init()
    motor_voz.setProperty('voice', motor_voz.getProperty('voices')[0].id) 
    
    tasa_actual = motor_voz.getProperty('rate')
    motor_voz.setProperty('rate', tasa_actual - 20) 
    
    motor_voz.say(texto)
    motor_voz.runAndWait()

def escuchar():
    reconocedor = sr.Recognizer()
    with sr.Microphone() as fuente:
        print("\nEscuchando...")
        reconocedor.adjust_for_ambient_noise(fuente, duration=0.2)
        audio = reconocedor.listen(fuente)

    try:
        print("Analizando...")
        # Aquí usamos la variable IDIOMA en lugar de 'es-MX' fijo
        texto = reconocedor.recognize_google(audio, language=IDIOMA).lower()
        print(f"> Tú dijiste: '{texto}'") 
        return texto
    except:
        return ""

# BUCLE PRINCIPAL
def ejecutar_jarvis():
    hablar(f"Sistemas en línea. Entrando en modo de espera, llámeme {NOMBRE_IA} si me necesita.")
    
    while True:
        comando = escuchar()

        if not comando:
            continue

        # Verifica si mencionaste el nombre configurado de la IA
        if NOMBRE_IA in comando:
            comando = comando.replace(NOMBRE_IA, '').strip()
            
            if comando == "":
                hablar("Dígame, señor.")
                comando = escuchar()
                
                if not comando:
                    continue
            
            # COMANDOS BÁSICOS RÁPIDOS
            if 'hora' in comando or 'time' in comando:
                hora = datetime.datetime.now().strftime('%I:%M %p')
                hablar(f"La hora actual es {hora}")

            elif 'descansa' in comando or 'sleep' in comando:
                hablar("Desconectando red neuronal. Que tenga un excelente día.")
                break
            # COMANDOS DINÁMICOS (PÁGINAS WEB)
            # Revisa si alguna palabra clave del JSON está en lo que dijiste
            elif any(clave in comando for clave in config["webs_personalizadas"]):
                for clave, url in config["webs_personalizadas"].items():
                    if clave in comando:
                        hablar(f"Abriendo {clave} enseguida.")
                        webbrowser.open(url)
                        break 
                        
            # COMANDOS DINÁMICOS (APLICACIONES)
            elif any(clave in comando for clave in config["apps_personalizadas"]):
                for clave, ruta in config["apps_personalizadas"].items():
                    if clave in comando:
                        hablar(f"Iniciando {clave}.")
                        os.startfile(ruta) 
                        break
            # MOTOR DE IA
            else:
                if comando != "":
                    try:
                        respuesta = cliente_ia.models.generate_content(
                            model='gemini-3.5-flash',
                            contents=comando,
                            config=types.GenerateContentConfig(
                                # Le pasamos su nuevo nombre a las instrucciones de la IA
                                system_instruction=f"Eres {NOMBRE_IA}, un asistente virtual muy inteligente y educado. Tus respuestas deben ser conversacionales, muy breves (máximo 2 o 3 oraciones cortas), y sin usar símbolos raros porque serás leído en voz alta."
                            )
                        )
                        texto_limpio = respuesta.text.replace('*', '')
                        hablar(texto_limpio)
                    except Exception as e:
                        print(f"\n[ERROR TÉCNICO]: {e}\n") 
                        hablar("Lo siento señor, tuve un problema de conexión con mi base de datos principal.")
if __name__ == "__main__":
    ejecutar_jarvis()