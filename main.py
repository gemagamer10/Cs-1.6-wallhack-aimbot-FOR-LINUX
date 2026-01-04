# main.py - Main entry point for CS 1.6 aimbot with anti-detection measures
import time
import keyboard
import os
import sys
import random
import threading
import psutil
from memory import MemoryManager
from offsets import Offsets
from entity import Player
from aimbot import Aimbot
from config import Config
from vector import Vector3
from wallhack import Wallhack

# Global variables for anti-detection
STATUS_UPDATE_INTERVAL = random.uniform(2.0, 5.0)
PROCESS_CHECK_INTERVAL = random.uniform(10.0, 20.0)
last_status_update = 0
last_process_check = 0
suspicious_processes = [
    "wireshark", "procmon", "processhacker", "ollydbg", "x64dbg", "ida", 
    "immunity", "cheatengine", "httpdebugger", "fiddler", "charles"
]

# ...existing code...

def main():
    try:
        # Use obfuscated startup messages
        startup_messages = [
            "Initializing system components...",
            "Starting performance monitor...",
            "Loading game assistant...",
            "Preparing environment...",
            "Setting up utilities..."
        ]
        print(random.choice(startup_messages))
        
        # Add random startup delay
        time.sleep(random.uniform(0.5, 1.5))
        
        # Initialize components
        config = Config()
        memory = None
        
        # Try to connect to game with better error handling
        try:
            print("Connecting to game process...")
            memory = MemoryManager()
            print("Game process found successfully.")
        except Exception as e:
            print("Initialization failed. Please make sure Counter-Strike is running.")
            print("Error details:", str(e))
            input("Press Enter to exit...")
            return
        
        try:
            print("Initializing aimbot...")
            aimbot = Aimbot(memory, config)
            aimbot.initialize()
            print("Aimbot initialized successfully.")
        except Exception as e:
            print("Aimbot initialization failed.")
            print("Error details:", str(e))
            input("Press Enter to exit...")
            return
        
        wallhack = None
        try:
            print("Initializing wallhack...")
            wallhack = Wallhack(memory, config)
            wallhack.initialize()
            print("Wallhack initialized successfully.")
        except Exception as e:
            print("Wallhack initialization failed.")
            print("Error details:", str(e))
            wallhack = None
        
        # Use obfuscated initialization messages
        init_messages = [
            "Components initialized successfully.",
            "System ready.",
            "Setup complete.",
            "Environment prepared."
        ]
        print(random.choice(init_messages))
        print(f"Press {config.toggle_key.upper()} to toggle assistant.")
        print(f"Press {config.exit_key.upper()} to exit.")
        print(f"Press INSERT to toggle wallhack.")  # ← MUDADO PARA INSERT
        
        # Register hotkeys with randomized delay
        time.sleep(random.uniform(0.1, 0.3))
        keyboard.add_hotkey(config.toggle_key, lambda: toggle_aimbot(aimbot))
        keyboard.add_hotkey('insert', lambda: toggle_wallhack(wallhack) if wallhack else None)  # ← MUDADO PARA 'insert'
        
        # Start anti-detection thread
        anti_detect_thread = threading.Thread(target=anti_detection_thread, args=(aimbot,), daemon=True)
        anti_detect_thread.start()
        
        # Main loop variables
        running = True
        frame_count = 0
        last_time = time.time()
        fps = 0
        
        # Variables for randomized execution
        next_player_scan = time.time()
        player_scan_interval = random.uniform(0.05, 0.15)
        
        while running:
            # Add randomized execution pattern
            randomize_execution_pattern()
            
            # Check exit key with randomized polling
            if random.random() < 0.8:
                if keyboard.is_pressed(config.exit_key):
                    print("Shutting down...")
                    break
                
            current_time = time.time()
            frame_count += 1
            
            # Calculate FPS and update status with randomized interval
            global last_status_update
            if current_time - last_status_update >= STATUS_UPDATE_INTERVAL:
                fps = frame_count / (current_time - last_time)
                frame_count = 0
                last_time = current_time
                last_status_update = current_time
                
                # Update status display
                print_status(aimbot, fps)
                
                # Randomize next status update interval (2-5 seconds)
                STATUS_UPDATE_INTERVAL = random.uniform(2.0, 5.0)
            
            # Check for monitoring processes periodically
            global last_process_check, PROCESS_CHECK_INTERVAL
            if current_time - last_process_check >= PROCESS_CHECK_INTERVAL:
                last_process_check = current_time
                
                # Randomize next check interval (10-20 seconds)
                PROCESS_CHECK_INTERVAL = random.uniform(10.0, 20.0)
                
                # If monitoring detected, temporarily disable
                if check_for_monitoring() and aimbot.is_active:
                    aimbot.toggle()
            
            if aimbot.is_active:
                try:
                    # Only scan for players at randomized intervals
                    if current_time >= next_player_scan:
                        # Get local player
                        local_player_addr = memory.read_int(memory.client_module + Offsets.dwLocalPlayer)
                        print(f"Local player address: {local_player_addr}")
                        
                        if local_player_addr:
                            local_player = Player(memory, local_player_addr)
                            print(f"Local player: Health={local_player.health}, Team={local_player.team}")
                            
                            if not local_player.is_valid():
                                print("Local player is not valid")
                                # Randomized sleep on invalid player
                                time.sleep(random.uniform(0.005, 0.015))
                                
                                # Set next scan time
                                next_player_scan = current_time + random.uniform(0.05, 0.15)
                                continue
                            else:
                                print("Local player is valid")
                            
                            # Get players with randomized scanning pattern
                            players = []
                            
                            # Randomize scanning order
                            indices = list(range(1, Offsets.MAX_PLAYERS))
                            random.shuffle(indices)
                            
                            print(f"Scanning for players (max: {Offsets.MAX_PLAYERS})")
                            
                            # Only scan a random subset of players each time (70-100%)
                            scan_count = int(len(indices) * random.uniform(0.7, 1.0))
                            print(f"Scanning {scan_count} player slots")
                            
                            for i in indices[:scan_count]:
                                entity_addr = memory.read_int(memory.client_module + Offsets.dwEntityList + i * 4)
                                print(f"Player slot {i}: Address {entity_addr}")
                                
                                if entity_addr and entity_addr != local_player_addr:
                                    print(f"Found player at slot {i}, address {entity_addr}")
                                    players.append(Player(memory, entity_addr))
                                    
                                    # Add small random delay between player scans
                                    if random.random() < 0.1:
                                        time.sleep(random.uniform(0.0001, 0.0005))
                            
                            print(f"Found {len(players)} potential players")
                            
                            # Find and aim at best target
                            target = aimbot.get_best_target(local_player, players)
                            if target:
                                aimbot.aim_at_target(target, local_player)
                            
                            if wallhack and wallhack.is_active:
                                wallhack.update(local_player, players)
                        
                        # Set next player scan time with jitter
                        next_player_scan = current_time + random.uniform(0.05, 0.15)
                
                except Exception as e:
                    # Print exception for debugging
                    print(f"Error in main loop: {str(e)}")
                    time.sleep(random.uniform(0.1, 0.3))
            
            # Variable sleep to reduce CPU usage and avoid detection
            sleep_time = random.uniform(0.0005, 0.002)
            time.sleep(sleep_time)
        
        # Save config on exit with randomized delay
        time.sleep(random.uniform(0.1, 0.3))
        config.save_config()
        
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        # Print exception for debugging
        print(f"Unhandled exception: {str(e)}")
        input("Press Enter to exit...")

def toggle_aimbot(aimbot):
    status = aimbot.toggle()
    
    # Use obfuscated terminology
    status_terms = {
        True: ["Assistant enabled", "System active", "Monitoring started"],
        False: ["Assistant disabled", "System inactive", "Monitoring stopped"]
    }
    
    # Print random status message
    print(random.choice(status_terms[status]))

def toggle_wallhack(wallhack):
    """Toggle wallhack on/off"""
    if not wallhack:
        return
    
    status = wallhack.toggle()
    
    status_terms = {
        True: ["Wallhack enabled", "ESP active", "Vision enabled"],
        False: ["Wallhack disabled", "ESP inactive", "Vision disabled"]
    }
    
    print(random.choice(status_terms[status]))

if __name__ == "__main__":
    main()