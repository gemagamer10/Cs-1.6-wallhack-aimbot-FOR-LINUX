import time
import struct
from memory import MemoryManager
from offsets import Offsets
from entity import Player
from config import Config

class Wallhack:
    def __init__(self, memory: MemoryManager, config: Config):
        self.memory = memory
        self.config = config
        self.is_active = False
        self.glow_color = [0, 255, 0]  # RGB verde
        self.glow_intensity = 255
        
    def initialize(self):
        """Initialize wallhack"""
        print("Wallhack initialized")
        
    def toggle(self):
        """Toggle wallhack on/off"""
        self.is_active = not self.is_active
        status = "enabled" if self.is_active else "disabled"
        print(f"Wallhack {status}")
        return self.is_active
    
    def set_glow_color(self, r: int, g: int, b: int):
        """Set glow color (0-255 each)"""
        self.glow_color = [r, g, b]
        
    def set_glow_intensity(self, intensity: int):
        """Set glow intensity (0-255)"""
        self.glow_intensity = max(0, min(255, intensity))
    
    def apply_glow_to_player(self, player: Player):
        """Apply glow effect to a player"""
        if not player.address:
            return False
            
        try:
            # Offset para o glow effect (varia conforme versão)
            # CS 1.6 usa renderamt para transparency glow
            GLOW_OFFSET = 0x58  # m_flRenderAmt
            
            # Escrever cor do glow
            glow_value = self.glow_intensity
            self.memory.write_int(player.address + GLOW_OFFSET, glow_value)
            
            return True
        except:
            return False
    
    def highlight_enemies(self, local_player: Player, enemies: list):
        """Highlight all enemies with glow"""
        if not self.is_active or not enemies:
            return 0
        
        highlighted = 0
        
        for enemy in enemies:
            # Verificar se é inimigo válido
            if enemy.health > 0 and enemy.team != local_player.team:
                if self.apply_glow_to_player(enemy):
                    highlighted += 1
                    time.sleep(0.001)  # Pequeno delay para evitar detecção
        
        return highlighted
    
    def apply_esp_box(self, player: Player, screen_width=1024, screen_height=768):
        """
        Calculate ESP box coordinates (skeleton/box ESP)
        Retorna as coordenadas para desenhar caixa ao redor do player
        """
        try:
            # Ler posição do player
            origin_offset = 0x2C
            x = self.memory.read_float(player.address + origin_offset)
            y = self.memory.read_float(player.address + origin_offset + 4)
            z = self.memory.read_float(player.address + origin_offset + 8)
            
            # Ler altura (aproximadamente 72 unidades)
            player_height = 72
            
            # Calcular projeção (simplificado - precisa de matriz de view)
            # Isto é uma aproximação
            box_left = int(screen_width / 2 - 20)
            box_right = int(screen_width / 2 + 20)
            box_top = int(screen_height / 2 - 40)
            box_bottom = int(screen_height / 2 + 40)
            
            return {
                'x1': box_left,
                'y1': box_top,
                'x2': box_right,
                'y2': box_bottom,
                'world_pos': (x, y, z)
            }
        except:
            return None
    
    def set_invisible(self, player: Player, invisible: bool):
        """
        Make player invisible to others
        renderamt = 0 para invisível
        """
        try:
            RENDERAMT_OFFSET = 0x58
            
            if invisible:
                self.memory.write_int(player.address + RENDERAMT_OFFSET, 0)
            else:
                self.memory.write_int(player.address + RENDERAMT_OFFSET, 255)
            
            return True
        except:
            return False
    
    def show_player_info(self, player: Player) -> dict:
        """Get player info for ESP display"""
        try:
            info = {
                'health': player.health,
                'team': player.team,
                'alive': player.health > 0,
                'address': hex(player.address) if player.address else "N/A"
            }
            
            # Ler nome do player (varia conforme offset)
            try:
                NAME_OFFSET = 0x200
                name_addr = self.memory.read_int(player.address + NAME_OFFSET)
                # name = self.memory.read_string(name_addr, 32)
                # info['name'] = name
            except:
                pass
            
            return info
        except:
            return None
    
    def update(self, local_player: Player, enemies: list):
        """Main wallhack update loop"""
        if not self.is_active:
            return 0
        
        return self.highlight_enemies(local_player, enemies)