import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
from google import genai
from google.genai import types

# CONFIGURACIÓN DEL CEREBRO IA
cliente_ia = genai.Client(api_key="API KEY") 

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
        texto = reconocedor.recognize_google(audio, language='es-MX').lower()
        print(f"> Tú dijiste: '{texto}'") 
        return texto
    except:
        return ""

# BUCLE PRINCIPAL
def ejecutar_jarvis():
    hablar("Sistemas en línea. Entrando en modo de espera.")
    
    while True:
        comando = escuchar()

        if not comando:
            continue

        es_jarvis = any(palabra in comando for palabra in ['jarvis', 'yarvis', 'harvis', 'charris', 'jerry'])

        if es_jarvis:
            for palabra in ['jarvis', 'yarvis', 'harvis', 'charris', 'jerry']:
                comando = comando.replace(palabra, '')
            comando = comando.strip()
            
            if comando == "":
                hablar("Dígame, señor.")
                comando = escuchar() 
                
                if not comando:
                    continue 
            
            # COMANDOS BÁSICOS RÁPIDOS
            if 'hora' in comando:
                hora = datetime.datetime.now().strftime('%I:%M %p')
                hablar(f"La hora actual es {hora}")

            elif 'youtube' in comando or 'videos' in comando:
                hablar("Abriendo YouTube enseguida, señor.")
                webbrowser.open("https://www.youtube.com")

            elif 'música' in comando or 'spotify' in comando:
                hablar("Abriendo Spotify de inmediato.")
                webbrowser.open("https://open.spotify.com")

            elif 'navegador' in comando or 'ópera' in comando:
                hablar("abriendo opera gx")
                os.startfile(r"C:\Users\josel\AppData\Local\Programs\Opera GX\opera.exe")

            elif 'minecraft' in comando or 'mods' in comando:
                hablar("abriendo curseforge")
                os.startfile(r"C:\Users\josel\AppData\Local\Programs\CurseForge Windows\CurseForge.exe")

            elif 'Fifa' in comando or 'fifita' in comando:
                hablar("listo pa unas retas señor?")
                os.startfile(r"D:\Games\FIFA 23\Launcher.exe")

            elif 'calculadora' in comando:
                hablar("abriendo Calculadora")
                os.system ("calc")
            
            elif 'notas' in comando or 'bloc de notas' in comando:
                hablar("abriendo bloc de notas")
                os.system ("notepad")

            elif 'silencio' in comando or 'callate' in comando:
                hablar("Desconectando red neuronal. Que tenga un excelente día.")
                break
                
            # MOTOR DE IA
            else:
                if comando != "":
                    try:
                        respuesta = cliente_ia.models.generate_content(
                            model='gemini-3.5-flash',
                            contents=comando,
                            config=types.GenerateContentConfig(
                                system_instruction="Eres Jarvis, un asistente virtual muy inteligente y educado. Tus respuestas deben ser conversacionales, muy breves (máximo 2 o 3 oraciones cortas), y sin usar símbolos raros porque serás leído en voz alta."
                            )
                        )
                        texto_limpio = respuesta.text.replace('*', '')
                        hablar(texto_limpio)
                    except Exception as e:
                        print(f"\n[ERROR TÉCNICO]: {e}\n") 
                        hablar("Lo siento señor, tuve un problema de conexión con mi base de datos principal.")
if __name__ == "__main__":
    ejecutar_jarvis()
