import customtkinter as ctk
import mss
import pygame

# Configurar el tema moderno
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class ModernLucioDJ(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Lúcio DJ Mixer Pro")
        self.geometry("350x380")
        self.resizable(False, False)

        # --- CONFIGURACIÓN DE AUDIO ---
        pygame.mixer.init()
        try:
            self.musica_curacion = pygame.mixer.Sound("music/curacion.mp3")
            self.musica_velocidad = pygame.mixer.Sound("music/velocidad.mp3")
        except FileNotFoundError:
            print("⚠️ Faltan los mp3 en la carpeta 'music'")
            self.musica_curacion = None
            self.musica_velocidad = None
            
        self.canal = pygame.mixer.Channel(0)
        self.estado_actual = None
        self.escaneando = False

        # --- CONFIGURACIÓN DEL ESCÁNER (MSS) ---
        self.sct = mss.mss()
        # Coordenadas (AJUSTA ESTO SEGÚN TU MONITOR)
        self.X = 960 
        self.Y = 600
        # Le decimos a MSS que solo capture un cuadrado de 1x1 píxel en esas coordenadas
        self.monitor = {"top": self.Y, "left": self.X, "width": 1, "height": 1}

        # --- INTERFAZ GRÁFICA MODERNA ---
        self.label_titulo = ctk.CTkLabel(self, text="🎧 LÚCIO DJ MIXER", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_titulo.pack(pady=(20, 10))

        self.label_estado = ctk.CTkLabel(self, text="Esperando conexión...", text_color="gray", font=ctk.CTkFont(size=14))
        self.label_estado.pack(pady=5)

        self.frame_debug = ctk.CTkFrame(self)
        self.frame_debug.pack(pady=15, padx=20, fill="x")

        self.label_debug_title = ctk.CTkLabel(self.frame_debug, text="Monitor de Color en Vivo", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_debug_title.pack(pady=(10, 0))

        self.color_box = ctk.CTkFrame(self.frame_debug, width=50, height=50, fg_color="black", border_width=2, border_color="gray")
        self.color_box.pack(pady=10)
        
        self.label_rgb = ctk.CTkLabel(self.frame_debug, text="RGB: (?, ?, ?)", font=ctk.CTkFont(size=11))
        self.label_rgb.pack(pady=(0, 10))

        self.btn_toggle = ctk.CTkButton(self, text="▶ INICIAR ESCANEO", command=self.toggle_escaneo, height=40, font=ctk.CTkFont(weight="bold"))
        self.btn_toggle.pack(pady=15)

    def rgb_a_hex(self, r, g, b):
        return f'#{r:02x}{g:02x}{b:02x}'

    def toggle_escaneo(self):
        self.escaneando = not self.escaneando
        if self.escaneando:
            self.btn_toggle.configure(text="⏹ DETENER ESCANEO", fg_color="#c0392b", hover_color="#e74c3c")
            self.label_estado.configure(text="Buscando a Lúcio en pantalla...", text_color="white")
            self.escanear_pixel()
        else:
            self.btn_toggle.configure(text="▶ INICIAR ESCANEO", fg_color=["#2CC985", "#2FA572"], hover_color=["#0C955A", "#106A43"])
            self.label_estado.configure(text="Pausado", text_color="gray")
            self.color_box.configure(fg_color="black")
            self.label_rgb.configure(text="RGB: (?, ?, ?)")
            self.canal.stop()
            self.estado_actual = None

    def escanear_pixel(self):
        if not self.escaneando: return

        try:
            # Capturar solo el píxel específico usando MSS (¡Súper rápido y sin gnome-screenshot!)
            captura = self.sct.grab(self.monitor)
            # mss devuelve el color en formato RGB directamente desde el pixel 0,0 de nuestra captura de 1x1
            r, g, b = captura.pixel(0, 0)
            
            # Actualizar la interfaz
            color_hex = self.rgb_a_hex(r, g, b)
            self.color_box.configure(fg_color=color_hex)
            self.label_rgb.configure(text=f"RGB: ({r}, {g}, {b})")

            # Lógica de detección (ajusta estos valores si el cuadro de arriba no coincide con tu juego)
            es_amarillo = (r > 150 and g > 150 and b < 100)
            es_verde = (r < 100 and g > 150 and b < 100)
            es_negro_o_gris = (r < 50 and g < 50 and b < 50)

            if es_negro_o_gris:
                self.label_estado.configure(text="⚠️ ¿Overwatch está minimizado?", text_color="orange")
            elif es_amarillo and self.estado_actual != "curacion":
                if self.musica_curacion: self.canal.play(self.musica_curacion, loops=-1)
                self.estado_actual = "curacion"
                self.label_estado.configure(text="¡SANANDO! 💛", text_color="#f1c40f", font=ctk.CTkFont(size=18, weight="bold"))
            elif es_verde and self.estado_actual != "velocidad":
                if self.musica_velocidad: self.canal.play(self.musica_velocidad, loops=-1)
                self.estado_actual = "velocidad"
                self.label_estado.configure(text="¡VELOCIDAD! 💚", text_color="#2ecc71", font=ctk.CTkFont(size=18, weight="bold"))
            elif not es_amarillo and not es_verde and not es_negro_o_gris:
                 if self.estado_actual != "perdido":
                     self.label_estado.configure(text="Detectando juego...", text_color="white", font=ctk.CTkFont(size=14))
                     self.estado_actual = "perdido"

        except Exception as e:
            self.label_estado.configure(text="Error de lectura", text_color="red")
            print(f"Error MSS: {e}")

        # Ejecutar de nuevo (¡Con MSS podemos bajar esto a 100ms porque no consume casi nada!)
        self.after(100, self.escanear_pixel)

if __name__ == "__main__":
    app = ModernLucioDJ()
    app.mainloop()