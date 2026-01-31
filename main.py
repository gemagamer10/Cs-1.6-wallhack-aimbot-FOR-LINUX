# main.py - Aimbot + Wallhack ESP + Menu GUI para CS 1.6 Linux
import tkinter as tk
from tkinter import ttk
import threading
import time
import math
from pynput.mouse import Controller
from pynput import keyboard
import pygame
import sys

# Imports locais
from memory import Memory
from offsets import *
from entity import Player
from vector import calc_angle, normalize_angles

# Globais
mem = Memory()
mouse = Controller()
aim_active = False
wallhack_active = False
running = True
SENS = 0.022  # Sensibilidade do aimbot (ajusta aqui)

# Resolução da tela (muda para a tua)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Variáveis para overlay
pygame_display = None
overlay_surface = None

def toggle_aim():
    global aim_active
    aim_active = not aim_active
    print(f"\n>>> Aimbot {'ATIVO' if aim_active else 'DESATIVO'} <<<")

def toggle_wallhack():
    global wallhack_active
    wallhack_active = not wallhack_active
    print(f"\n>>> Wallhack/ESP {'ATIVO' if wallhack_active else 'DESATIVO'} <<<")
    if wallhack_active:
        start_esp_overlay()
    else:
        stop_esp_overlay()

def start_esp_overlay():
    global pygame_display, overlay_surface
    pygame.init()
    pygame_display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption("CS 1.6 ESP")
    overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    threading.Thread(target=esp_loop, daemon=True).start()

def stop_esp_overlay():
    global wallhack_active
    wallhack_active = False
    if pygame.get_init():
        pygame.quit()

def get_local_player():
    local_addr = mem.read_uint(mem.client_base + DW_LOCALPLAYER)
    if local_addr == 0:
        return None
    player = Player(mem, local_addr)
    player.update()
    return player if 0 < player.health <= 100 else None

def find_enemies(local):
    enemies = []
    entity_base = mem.client_base + ENTITY_LIST
    for i in range(1, 32):
        entity_addr = mem.read_uint(entity_base + i * 4)
        if not entity_addr or entity_addr == local.addr:
            continue
        enemy = Player(mem, entity_addr)
        enemy.update()
        if 0 < enemy.health <= 100 and enemy.team != local.team:
            enemies.append(enemy)
    return enemies

def aim_loop():
    global running
    while running:
        if not mem.pid or not aim_active:
            time.sleep(0.01)
            continue

        local = get_local_player()
        if not local:
            time.sleep(0.01)
            continue

        enemies = find_enemies(local)
        if enemies:
            closest = min(enemies, key=lambda e: e.pos.distance_to(local.pos))
            pitch, yaw = calc_angle(local.pos, closest.pos)
            pitch, yaw = normalize_angles(pitch, yaw)
            mouse.move(int(yaw * SENS * 1000), int(pitch * SENS * 1000))

        time.sleep(0.001)

def esp_loop():
    global running, overlay_surface, pygame_display
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)

    while running and wallhack_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                toggle_wallhack()
                break

        overlay_surface.fill((0, 0, 0, 0))  # Fundo transparente

        if mem.pid:
            local = get_local_player()
            if local:
                enemies = find_enemies(local)
                for enemy in enemies:
                    # Aproximação simples para teste (centro da tela + offset)
                    # Com offsets corretos e world2screen real, fica perfeito
                    x = SCREEN_WIDTH // 2 - 50
                    y = SCREEN_HEIGHT // 2 - 100
                    w, h = 100, 200

                    # Caixa vermelha semi-transparente
                    pygame.draw.rect(overlay_surface, (255, 0, 0, 150), (x, y, w, h), 4)
                    # Health
                    text = font.render(str(enemy.health), True, (255, 255, 255))
                    pygame_display.blit(text, (x + 40, y + 80))

        pygame_display.blit(overlay_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

class CheatMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CS 1.6 Cheat Menu")
        self.root.geometry("380x480")
        self.root.configure(bg='#1e1e1e')
        self.root.resizable(False, False)

        tk.Label(self.root, text="CS 1.6 CHEAT", font=('Helvetica', 20, 'bold'), bg='#1e1e1e', fg='#00ff00').pack(pady=20)

        self.aim_label = tk.Label(self.root, text="Aimbot: OFF", font=('Helvetica', 14), bg='#1e1e1e', fg='red')
        self.aim_label.pack(pady=10)

        ttk.Button(self.root, text="Toggle Aimbot (INSERT)", command=toggle_aim).pack(pady=5)

        self.wh_label = tk.Label(self.root, text="Wallhack: OFF", font=('Helvetica', 14), bg='#1e1e1e', fg='red')
        self.wh_label.pack(pady=10)

        ttk.Button(self.root, text="Toggle Wallhack (F12)", command=toggle_wallhack).pack(pady=5)

        self.game_label = tk.Label(self.root, text="Jogo: Não detetado", bg='#1e1e1e', fg='orange', font=('Helvetica', 12))
        self.game_label.pack(pady=30)

        self.update_status()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_status(self):
        self.aim_label.config(text="Aimbot: ON" if aim_active else "Aimbot: OFF", fg='lime' if aim_active else 'red')
        self.wh_label.config(text="Wallhack: ON" if wallhack_active else "Wallhack: OFF", fg='lime' if wallhack_active else 'red')

        if mem.pid:
            self.game_label.config(text=f"Jogo detetado - PID: {mem.pid}", fg='lime')
        else:
            self.game_label.config(text="Jogo: Não detetado", fg='orange')

        self.root.after(500, self.update_status)

    def on_close(self):
        global running
        running = False
        toggle_wallhack()  # Fecha overlay
        self.root.destroy()

if __name__ == "__main__":
    print("=== CS 1.6 CHEAT LINUX - Aimbot + Wallhack ESP ===")
    print("INSERT = Aimbot | F12 = Wallhack/ESP")

    # Threads principais
    threading.Thread(target=lambda: [mem.find_cs_pid() or time.sleep(2) for _ in iter(int, 1)], daemon=True).start()
    threading.Thread(target=aim_loop, daemon=True).start()

    # Hotkeys
    with keyboard.Listener(
        on_press=lambda k: toggle_aim() if k == keyboard.Key.insert else toggle_wallhack() if k == keyboard.Key.f12 else None
    ) as listener:
        # Menu GUI
        menu = CheatMenu()
        menu.root.mainloop()

        listener.stop()
        running = False