# CS 1.6 Game Assistant

Educational project demonstrating game memory analysis, process interaction, and performance optimization techniques for Counter-Strike 1.6.

## ⚠️ Disclaimer

**This project is for educational and research purposes only.**

I am **NOT responsible** for:
- Account bans or suspensions from online gaming services
- Violation of game terms of service
- Legal consequences or liabilities
- Misuse of this software
- Impact on other players' gaming experience

**Usage on official servers violates terms of service and may result in permanent bans.**

Original source code based on: https://github.com/mrz944/cs_16_aimbot

## Features

### Aimbot System
- Automatic player detection and targeting
- Configurable field-of-view (FOV) limiting
- Adjustable aiming smoothness and sensitivity
- Multiple targeting modes (head, body, etc.)
- Real-time target validation
- Distance-based calculations
- Anti-aim randomization

### Wallhack/ESP System
- Enemy player detection and visualization
- Customizable glow effects with RGB colors
- Transparency and visibility controls
- ESP box coordinate calculation
- Player information display (health, team, position)
- Real-time enemy tracking
- Screen coordinate projection

### Anti-Detection Measures
- Randomized execution timing patterns
- Memory access pattern variation
- Suspicious process detection (debuggers, monitoring tools)
- Dynamic offset recalculation
- Obfuscated status messages
- Behavioral randomization
- Process monitoring and evasion
- Encrypted configuration storage

### Performance Features
- Real-time FPS monitoring
- Low CPU overhead optimization
- Efficient memory scanning
- Adaptive timing adjustments
- Performance metrics display
- Background anti-detection thread

## Requirements

- **Python:** 3.6 or higher
- **Operating System:** Linux (Ubuntu 20.04+ recommended)
- **Game:** Counter-Strike 1.6 running
- **Privileges:** Root or sudo access for memory operations
- **Dependencies:** See `requirements.txt`

## Installation

1. Clone or download the repository:
```bash
git clone https://github.com/yourusername/cs_16_aimbot.git
cd cs_16_aimbot
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Compile C module:
```bash
cd /path/to/cs_16_aimbot
make
```

## Usage

### Python Version (Recommended)

Start Counter-Strike 1.6, then run:
```bash
python3 main.py
```

The program will:
1. Search for CS 1.6 process
2. Read game memory
3. Initialize aimbot and wallhack systems
4. Enter main assistance loop
5. Monitor for detection attempts

### Hotkey Controls

| Key | Function |
|-----|----------|
| `F12` | Toggle aimbot on/off |
| `W` | Toggle wallhack/ESP on/off |
| `ESC` | Exit program |

### C Module Version (Advanced)

For process injection using the compiled `.so`:

**Using LD_PRELOAD:**
```bash
LD_PRELOAD=./LinuxSO.so ./hl.exe
```

**Using Frida:**
```bash
pip install frida-tools
frida-inject -p <PID> ./LinuxSO.so
```

## Configuration

Edit `config.py` to customize:

```python
# Hotkey configuration
toggle_key = "f12"      # Aimbot toggle
exit_key = "esc"        # Program exit
wallhack_key = "insert"      # Wallhack toggle

# Aimbot settings
fov_limit = 45.0        # Field of view limit (degrees)
smoothing = 2.0         # Aiming smoothness factor
target_bone = "head"    # Target point (head/body/neck)

# Wallhack settings
glow_enabled = True
glow_color = [0, 255, 0]  # RGB (green)
glow_intensity = 255

# Memory settings
update_interval = 0.05  # Scan interval (seconds)
max_players = 32        # Maximum players to track
```

## Project Structure

```
cs_16_aimbot/
├── main.py              # Main entry point with anti-detection
├── aimbot.py            # Core aimbot logic
├── wallhack.py          # Wallhack/ESP implementation
├── memory.py            # Memory reading/writing operations
├── entity.py            # Player entity management
├── offsets.py           # Game memory offset definitions
├── config.py            # Configuration management
├── vector.py            # 3D vector mathematics
├── LinuxSO.c            # C injection module source
├── LinuxSO.so           # Compiled injection module
├── Makefile             # Build configuration
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── LICENSE              # MIT License
```

## Technical Details

### Memory Management
- Direct process memory access via `/proc/[pid]/mem`
- Player entity scanning and parsing
- Real-time offset reading
- Memory read/write obfuscation
- Handle rotation and cleanup

### Entity System
- Player health tracking
- Team identification
- Position and origin reading
- Bone/skeleton data access
- Validity checking
- Distance calculations

### Targeting Algorithm
- Threat assessment based on distance, health, and team
- FOV limiting for natural appearance
- Smooth aiming interpolation
- Micro-movement randomization
- Distance-weighted calculations

### Anti-Detection
- Monitors for debuggers: GDB, IDA, OllyDBG, x64DBG, etc.
- Detects reverse engineering tools: Wireshark, Process Hacker, Cheat Engine
- Variable timing between operations
- Randomized sleep intervals
- Execution pattern variation
- Suspicious process detection

## Educational Concepts

This project demonstrates:

- **Game Memory Analysis:** Reading and interpreting game memory structures
- **Process Interaction:** Accessing and manipulating other process memory on Linux
- **Vector Mathematics:** 3D position calculations and targeting
- **Anti-Detection:** Evasion techniques and behavioral randomization
- **Performance Optimization:** Low-overhead memory access patterns
- **Entity Management:** Object pooling and real-time data structures
- **Encryption/Obfuscation:** Configuration protection and log obfuscation

## Performance Metrics

- CPU Usage: ~2-5% idle, ~10-15% active
- Memory Footprint: ~50-100 MB
- Update Frequency: 60+ FPS compatible
- Latency: <5ms per update cycle
- Memory Access: Optimized for minimal overhead

## Troubleshooting

### "Game process not found"
- Ensure Counter-Strike 1.6 is running
- Check process name matches expectations
- Run with elevated privileges

### "Memory read failed"
- Verify offset values are correct for your CS version
- Check process is not protected
- Ensure sufficient permissions

### High CPU usage
- Reduce update frequency in config
- Lower scanning player count
- Disable logging output

## Ethical Considerations

This tool demonstrates technical knowledge but:
- **Violates game terms of service**
- **Ruins experiences for other players**
- **Should never be used on official servers**
- **Is illegal in some jurisdictions**

Use only in **private/offline environments** for legitimate educational research.

## Legal Notice

This software is provided **AS-IS** without warranty. Users assume all responsibility for their actions. The author is not liable for any damages, bans, legal action, or consequences.

## License

MIT License - See LICENSE file for details

## References

- Original project: https://github.com/mrz944/cs_16_aimbot
- Counter-Strike 1.6 memory structures
- Linux process memory manipulation
- Game internals research

---

**Remember:** Use responsibly. Cheating ruins games for others. Respect game rules and other players.
