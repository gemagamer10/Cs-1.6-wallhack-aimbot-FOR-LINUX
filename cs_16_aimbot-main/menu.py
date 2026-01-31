import tkinter as tk
from tkinter import ttk
import threading
from main import aim_active, toggle_aimbot, running  # Importa variáveis do main.py

class AimbotMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CS 1.6 Aimbot Linux - By Grok & Gema")
        self.root.geometry("400x500")
        self.root.configure(bg='#1e1e1e')
        self.root.resizable(False, False)

        # Estilo dark
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background='#1e1e1e', foreground='white', font=('Helvetica', 10))
        style.configure('TButton', background='#333333', foreground='white')
        style.configure('TCheckbutton', background='#1e1e1e', foreground='white')
        style.configure('TScale', background='#1e1e1e')

        # Título
        title = tk.Label(self.root, text="CS 1.6 AIMBOT", font=('Helvetica', 18, 'bold'), bg='#1e1e1e', fg='#00ff00')
        title.pack(pady=20)

        # Status
        self.status_label = tk.Label(self.root, text="Aimbot: DESATIVADO", font=('Helvetica', 14), bg='#1e1e1e', fg='red')
        self.status_label.pack(pady=10)

        # Toggle button
        toggle_btn = ttk.Button(self.root, text="Toggle Aimbot (INSERT)", command=self.toggle)
        toggle_btn.pack(pady=10)

        # Sensibilidade
        tk.Label(self.root, text="Sensibilidade (ajusta no código por agora)", bg='#1e1e1e', fg='white').pack(pady=(20,5))
        self.sens_scale = ttk.Scale(self.root, from_=0.01, to=0.05, orient='horizontal')
        self.sens_scale.set(0.022)
        self.sens_scale.pack(pady=5, fill='x', padx=50)

        # FOV (visual - não usado ainda)
        tk.Label(self.root, text="FOV (em graus)", bg='#1e1e1e', fg='white').pack(pady=(20,5))
        self.fov_scale = ttk.Scale(self.root, from_=30, to=180, orient='horizontal')
        self.fov_scale.set(90)
        self.fov_scale.pack(pady=5, fill='x', padx=50)

        # Status do jogo
        self.game_status = tk.Label(self.root, text="Jogo: Não detetado", bg='#1e1e1e', fg='orange', font=('Helvetica', 12))
        self.game_status.pack(pady=20)

        # Atualiza status em loop
        self.update_status()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def toggle(self):
        toggle_aimbot()
        self.update_status()

    def update_status(self):
        global aim_active
        if aim_active:
            self.status_label.config(text="Aimbot: ATIVO", fg='#00ff00')
        else:
            self.status_label.config(text="Aimbot: DESATIVADO", fg='red')

        # Atualiza status do jogo (simples)
        from main import mem
        if mem.pid:
            self.game_status.config(text=f"Jogo detetado - PID: {mem.pid}", fg='#00ff00')
        else:
            self.game_status.config(text="Jogo: Não detetado", fg='orange')

        self.root.after(500, self.update_status)  # Atualiza a cada 0.5s

    def on_close(self):
        global running
        running = False
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    menu = AimbotMenu()
    menu.run()
