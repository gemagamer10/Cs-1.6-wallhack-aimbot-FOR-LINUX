# setup.py - Versão adaptada para LINUX (removida verificação Windows, pacotes cross-platform)
import subprocess
import sys
import os
import random
import time
import platform

def install_requirements():
    """Instala pacotes necessários para Linux"""
    print("Instalando dependências para Linux...")
    requirements = [
        "numpy",
        "pynput",  # Mouse e keyboard cross-platform (sem sudo)
        "psutil"   # Encontrar PID do processo
    ]
    random.shuffle(requirements)
    for req in requirements:
        time.sleep(random.uniform(0.2, 0.5))
        print(f"Instalando {req}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", req])
    print("\nDependências instaladas!")

def check_environment():
    """Verificação básica para Linux"""
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 8:
        print("Aviso: Python 3.8+ recomendado.")
        return False
    print(f"Python OK: {platform.python_version()}")
    print(f"SO OK: {platform.system()}")
    return True

def print_instructions():
    print("\n=== CHEAT CS 1.6 LINUX PRONTO ===\n")
    print("1. Compile LinuxSO.so: gcc -m32 -shared -fPIC -o LinuxSO.so LinuxSO.c -ldl")
    print("2. Abra CS 1.6 em modo janela (-window nas opções Steam)")
    print("3. Rode: python3 main.py")
    print("4. Hotkey: INSERT para toggle aimbot")
    print("\nOffsets são placeholders - atualize em offsets.py com GDB/Cheat Engine")
    print("AVISO: Para fins educacionais. Use por sua conta e risco!")

if __name__ == "__main__":
    if check_environment():
        install_requirements()
        print_instructions()
        input("\nPressione Enter para sair...")
    else:
        input("Corrija e tente novamente...")