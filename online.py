import random
import sys
import tkinter as tk
from tkinter import messagebox
from gtts import gTTS
from playsound3 import playsound
import tempfile
import unicodedata
import os


# ===================== CONFIGURACIÓN =====================
WORD_FILE = "isw.txt"             # Tu archivo con una palabra por línea


# ===================== TTS (pronunciación) =====================
# pyttsx3 for "correcto" / "la palabra era"; gTTS for Pronunciar. sapi5 = Windows only.
engine = None
try:
    import pyttsx3
    if sys.platform == "win32":
        engine = pyttsx3.init("sapi5")
    else:
        engine = pyttsx3.init()
except Exception:
    pass

if engine:
    engine.setProperty("rate", 140)
    voices = engine.getProperty("voices")
    spanish_voice_set = False
    for voice in voices:
        if "spanish" in voice.name.lower() or "es-" in voice.id.lower() or "helena" in voice.name.lower():
            engine.setProperty("voice", voice.id)
            spanish_voice_set = True
            print(f"Voz seleccionada: {voice.name}")
            break
    if not spanish_voice_set:
        print("No se encontró voz en español → usando voz por defecto")
else:
    print("pyttsx3 no disponible → solo gTTS (Pronunciar) para audio")


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


# ===================== INTERFAZ GRÁFICA =====================
root = tk.Tk()
root.title("Spanish Spelling Bee - ISW")
root.geometry("760x520")
root.configure(bg="#f0f8ff")
root.resizable(False, False)


# Título
titulo = tk.Label(root, text="¡Escucha y escribe la palabra!", font=("Helvetica", 26, "bold"),
                  bg="#f0f8ff", fg="#2c3e50")
titulo.pack(pady=(28, 10))


# Área de indicación (sin mostrar la palabra)
hint_var = tk.StringVar(value="Presiona 'Nueva palabra' para comenzar")
hint_label = tk.Label(root, textvariable=hint_var, font=("Helvetica", 18),
                      bg="#e8f4f8", fg="#2c3e50", width=36, height=2,
                      relief="ridge", borderwidth=2, padx=10, pady=10)
hint_label.pack(pady=20)


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
    hint_var.set("??? — Escucha con 🔊 Pronunciar y escribe la palabra")
    entry.delete(0, tk.END)
    entry.focus()
    status_var.set(f"Palabra de {len(palabra_actual)} letras")


def pronunciar():
    global palabra_actual
    if not palabra_actual:
        return
    try:
        tts = gTTS(text=palabra_actual, lang="es", slow=False)
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        tts.save(path)
        try:
            playsound(path)
        finally:
            os.remove(path)
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
        messagebox.showinfo("¡Correcto!", "¡Muy bien!")
        if engine:
            engine.say("correcto")
            engine.runAndWait()
        nueva_palabra()
    else:
        messagebox.showwarning("Incorrecto", f"La palabra era:\n\n{palabra_actual.upper()}")
        if engine:
            engine.say(f"la palabra era {palabra_actual}")
            engine.runAndWait()


# Atajos de teclado
def on_enter(event=None):
    comprobar()


def on_ctrl_n(event=None):
    nueva_palabra()


entry.bind("<Return>", on_enter)
root.bind("<Control-n>", on_ctrl_n)
root.bind("<Control-N>", on_ctrl_n)


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
status_var = tk.StringVar(value="Listo – Nueva palabra (Ctrl+N) para empezar")
status_label = tk.Label(root, textvariable=status_var,
                        font=("Arial", 13), bg="#f0f8ff", fg="#7f8c8d")
status_label.pack(pady=10)


# ===================== INICIAR =====================
root.mainloop()
