import random
import tkinter as tk
from tkinter import messagebox
import pyttsx3
from gtts import gTTS
from playsound3 import playsound
import unicodedata
import os


# ===================== CONFIGURACIÓN =====================
WORD_FILE = "isw.txt"             # Tu archivo con una palabra por línea
BLANK_PROBABILITY = 0.65        # 0.4 = fácil   |   0.8 = difícil


# ===================== TTS (pronunciación) =====================
engine = pyttsx3.init('sapi5')
engine.setProperty('rate', 140)

voices = engine.getProperty('voices')
spanish_voice_set = False
for voice in voices:
    if "spanish" in voice.name.lower() or "es-" in voice.id.lower() or "helena" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        spanish_voice_set = True
        print(f"Voz seleccionada: {voice.name}")
        break

if not spanish_voice_set:
    print("No se encontró voz en español → usando voz por defecto")


# ===================== CARGAR PALABRAS =====================
def load_words():
    try:
        with open(WORD_FILE, 'r', encoding='utf-8') as f:
            words = [line.strip().lower() for line in f if line.strip() and not line.startswith('#')]
        if not words:
            messagebox.showerror("Error", "El archivo está vacío o no tiene palabras válidas")
            return []
        return words
    except FileNotFoundError:
        messagebox.showerror("Error", f"No se encontró el archivo '{WORD_FILE}'.\nAsegúrate de que esté en la misma carpeta.")
        return []
    except Exception as e:
        messagebox.showerror("Error", f"Problema al leer el archivo:\n{e}")
        return []


palabras = load_words()
if not palabras:
    print("No se cargaron palabras. Cerrando programa.")
    exit()


# ===================== CREAR BLANKS =====================
def crear_blanks(palabra):
    if len(palabra) <= 3:
        return " ".join(["_" if i > 0 else c for i, c in enumerate(palabra)])

    chars = list(palabra)
    for i in range(1, len(chars)):
        if random.random() < BLANK_PROBABILITY:
            chars[i] = "_"
    return " ".join(chars)


# ===================== INTERFAZ GRÁFICA =====================
root = tk.Tk()
root.title("Spanish Word Completion Game - ISW")
root.geometry("760x540")
root.configure(bg="#f0f8ff")
root.resizable(False, False)


# Título
titulo = tk.Label(root, text="¡Completa la palabra!", font=("Helvetica", 28, "bold"),
                  bg="#f0f8ff", fg="#2c3e50")
titulo.pack(pady=(30, 10))


# Área de la palabra con blanks
palabra_var = tk.StringVar(value="Presiona 'Nueva palabra' para comenzar")
palabra_label = tk.Label(root, textvariable=palabra_var, font=("Consolas", 40, "bold"),
                         bg="#ffffff", fg="#34495e", width=22, height=2,
                         relief="ridge", borderwidth=4, padx=10, pady=10)
palabra_label.pack(pady=20)


# ─── Entrada + botón ñ ───────────────────────────────────────
input_frame = tk.Frame(root, bg="#f0f8ff")
input_frame.pack(pady=15)

entry = tk.Entry(input_frame, font=("Arial", 22), justify="center", width=18)
entry.pack(side="left", padx=(0, 8))
entry.focus()

def insert_ñ():
    current = entry.get()
    pos = entry.index(tk.INSERT)
    entry.delete(0, tk.END)
    entry.insert(0, current[:pos] + "ñ" + current[pos:])
    entry.focus()
    entry.icursor(pos + 1)

btn_ñ = tk.Button(input_frame, text="ñ", font=("Arial", 22, "bold"),
                  width=3, height=1, bg="#95a5a6", fg="white",
                  command=insert_ñ)
btn_ñ.pack(side="left")


palabra_actual = ""


# ===================== FUNCIONES =====================
def nueva_palabra():
    global palabra_actual
    palabra_actual = random.choice(palabras)
    blanks = crear_blanks(palabra_actual)
    palabra_var.set(blanks)
    entry.delete(0, tk.END)
    entry.focus()
    status_var.set(f"Palabra de {len(palabra_actual)} letras")


def pronunciar():
    global palabra_actual
    if not palabra_actual:
        return
    try:
        tts = gTTS(text=palabra_actual, lang='es', slow=False)
        filename = "temp_word.mp3"
        tts.save(filename)
        playsound(filename)
        os.remove(filename)
    except Exception as e:
        print("Audio error:", e)
        messagebox.showwarning("Problema de audio", "No se pudo reproducir.\nRevisa conexión a internet.")


def normalize_no_accents(text: str) -> str:
    # First preserve ñ / Ñ so it is not turned into n
    text = text.replace('ñ', '[tilde-n]').replace('Ñ', '[TILDE-N]')

    # Now remove other diacritics (á→a, é→e, etc.)
    nfkd_form = unicodedata.normalize('NFKD', text)
    cleaned = ''.join(
        c for c in nfkd_form
        if unicodedata.category(c) != 'Mn'
    )

    # Restore ñ / Ñ
    cleaned = cleaned.replace('[tilde-n]', 'ñ').replace('[TILDE-N]', 'Ñ')

    return cleaned.lower()


def comprobar():
    if not palabra_actual:
        return

    respuesta = entry.get().strip().lower()
    respuesta_norm = normalize_no_accents(respuesta)
    palabra_norm   = normalize_no_accents(palabra_actual)

    if respuesta_norm == palabra_norm:
        messagebox.showinfo("¡Correcto!", f"¡Muy bien!\n\n{palabra_actual.upper()}")
        engine.say("correcto")
        engine.runAndWait()
        nueva_palabra()
    else:
        messagebox.showwarning("Incorrecto", f"La palabra era:\n\n{palabra_actual.upper()}")
        engine.say(f"la palabra era {palabra_actual}")
        engine.runAndWait()


# Atajos de teclado (solo Enter para comprobar)
def on_enter(event=None):
    comprobar()


entry.bind("<Return>", on_enter)


# ===================== BOTONES =====================
frame_botones = tk.Frame(root, bg="#f0f8ff")
frame_botones.pack(pady=25)

btn_nueva = tk.Button(frame_botones, text="Nueva palabra", font=("Arial", 16, "bold"),
                      width=16, height=2, bg="#3498db", fg="white",
                      command=nueva_palabra)
btn_nueva.grid(row=0, column=0, padx=30)

btn_pronunciar = tk.Button(frame_botones, text="🔊 Pronunciar", font=("Arial", 16, "bold"),
                           width=18, height=2, bg="#e74c3c", fg="white",
                           command=pronunciar)
btn_pronunciar.grid(row=0, column=1, padx=30)

btn_comprobar = tk.Button(root, text="Comprobar (Enter)", font=("Arial", 18, "bold"),
                          width=25, height=2, bg="#27ae60", fg="white",
                          command=comprobar)
btn_comprobar.pack(pady=10)


# Estado
status_var = tk.StringVar(value="Listo – presiona Nueva palabra para empezar")
status_label = tk.Label(root, textvariable=status_var,
                        font=("Arial", 13), bg="#f0f8ff", fg="#7f8c8d")
status_label.pack(pady=10)


# ===================== INICIAR =====================
root.mainloop()