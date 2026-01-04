// aimbot_cs16_linux_32bit.c
// Compilar com: gcc -m32 -shared -fPIC -o aimbot.so aimbot_cs16_linux_32bit.c -ldl

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <sys/uio.h>
#include <dlfcn.h>
#include <math.h>
#include <stdint.h>     // Para tipos exatos em 32-bits
#include <inttypes.h>

// Estruturas para o aimbot
typedef struct {
    uint32_t health;
    uint32_t team;
    float x, y, z;
    uintptr_t address;
} Player;

typedef struct {
    float x, y, z;
} Vector3;

// Offsets para CS 1.6 Linux (client.so) - ATENÇÃO: estes são EXEMPLO/PLACEHOLDER
// Você precisa encontrar os offsets corretos com reverse engineering (GDB, etc.)
#define OFFSET_HEALTH       0x6C    // Placeholder
#define OFFSET_TEAM         0x78    // Placeholder
#define OFFSET_ORIGIN       0x2C    // Placeholder (x,y,z)
#define OFFSET_VIEW_ANGLE   0x4C    // Placeholder

// Variáveis globais
static int is_active = 0;
static pid_t target_pid = 0;
static uintptr_t client_module = 0;

// Função para ler memória
int read_memory(pid_t pid, uintptr_t addr, void *buffer, size_t size) {
    struct iovec local, remote;
    
    local.iov_base = buffer;
    local.iov_len = size;
    remote.iov_base = (void*)addr;
    remote.iov_len = size;
    
    return process_vm_readv(pid, &local, 1, &remote, 1, 0) == (ssize_t)size ? 0 : -1;
}

// Função para escrever memória
int write_memory(pid_t pid, uintptr_t addr, const void *buffer, size_t size) {
    struct iovec local, remote;
    
    local.iov_base = (void*)buffer;
    local.iov_len = size;
    remote.iov_base = (void*)addr;
    remote.iov_len = size;
    
    return process_vm_writev(pid, &local, 1, &remote, 1, 0) == (ssize_t)size ? 0 : -1;
}

// Encontra o processo do CS 1.6 (hl.exe ou hlds no Linux geralmente é hl_linux ou counter-strike)
int find_cs_process() {
    FILE *fp;
    char cmd[256];
    char line[256];
    
    snprintf(cmd, sizeof(cmd), "pgrep -f 'hl_linux\\|counter-strike'");
    fp = popen(cmd, "r");
    if (!fp) return -1;
    
    if (fgets(line, sizeof(line), fp) != NULL) {
        target_pid = atoi(line);
        pclose(fp);
        return target_pid;
    }
    
    pclose(fp);
    return -1;
}

// Encontra o base address do client.so
uintptr_t find_client_module() {
    FILE *fp;
    char line[512];
    char filename[256];
    uintptr_t addr = 0;
    
    snprintf(filename, sizeof(filename), "/proc/%d/maps", target_pid);
    fp = fopen(filename, "r");
    if (!fp) return 0;
    
    while (fgets(line, sizeof(line), fp) != NULL) {
        if (strstr(line, "client.so") != NULL) {
            sscanf(line, "%" SCNxPTR "-%", &addr);
            break;
        }
    }
    
    fclose(fp);
    return addr;
}

// Calcula e aplica aim no alvo
void aim_at_target(Player *local, Player *target) {
    if (!local || !target || !target_pid) return;
    
    float dx = target->x - local->x;
    float dy = target->y - local->y;
    float dz = target->z - local->z;
    
    float distance = sqrtf(dx*dx + dy*dy);
    float pitch = asinf(dz / sqrtf(dx*dx + dy*dy + dz*dz));  // Melhor cálculo
    float yaw = atan2f(dy, dx);
    
    // Converter para graus (se o jogo usar graus)
    pitch = pitch * (180.0f / M_PI);
    yaw   = yaw   * (180.0f / M_PI);
    
    float angles[2] = { pitch, yaw };
    uintptr_t view_angle_addr = target->address + OFFSET_VIEW_ANGLE;
    
    write_memory(target_pid, view_angle_addr, angles, sizeof(angles));
}

// Lê jogadores da entity list
int get_players(Player *players, int max_players) {
    if (!client_module || !target_pid) return 0;
    
    int count = 0;
    
    // Placeholder: endereço do local player (você precisa achar o real)
    uintptr_t local_player_addr = 0;
    read_memory(target_pid, client_module + 0x80, &local_player_addr, sizeof(local_player_addr));
    if (!local_player_addr) return 0;
    
    Player local_player = {0};
    local_player.address = local_player_addr;
    
    read_memory(target_pid, local_player_addr + OFFSET_HEALTH, &local_player.health, sizeof(uint32_t));
    read_memory(target_pid, local_player_addr + OFFSET_TEAM,   &local_player.team,   sizeof(uint32_t));
    read_memory(target_pid, local_player_addr + OFFSET_ORIGIN, &local_player.x,      sizeof(float)*3);
    
    // Placeholder: entity list base
    uintptr_t entity_list = client_module + 0x400;
    
    for (int i = 1; i < max_players && count < 31; i++) {
        uintptr_t entity_addr = 0;
        read_memory(target_pid, entity_list + i * 4, &entity_addr, sizeof(entity_addr));
        
        if (!entity_addr || entity_addr == local_player_addr) continue;
        
        Player player = {0};
        player.address = entity_addr;
        
        read_memory(target_pid, entity_addr + OFFSET_HEALTH, &player.health, sizeof(uint32_t));
        read_memory(target_pid, entity_addr + OFFSET_TEAM,   &player.team,   sizeof(uint32_t));
        read_memory(target_pid, entity_addr + OFFSET_ORIGIN, &player.x,      sizeof(float)*3);
        
        if (player.health > 0 && player.health <= 100 && player.team != local_player.team) {
            players[count++] = player;
            aim_at_target(&local_player, &player);  // Aplica aim no primeiro inimigo válido
        }
    }
    
    return count;
}

// Funções exportadas (para injeção via LD_PRELOAD ou dlopen)
__attribute__((visibility("default"))) int init_aimbot() {
    target_pid = find_cs_process();
    if (target_pid <= 0) return -1;
    
    client_module = find_client_module();
    if (!client_module) return -1;
    
    is_active = 1;
    return 0;
}

__attribute__((visibility("default"))) int toggle_aimbot() {
    is_active = !is_active;
    return is_active;
}

__attribute__((visibility("default"))) int get_aimbot_status() {
    return is_active;
}

__attribute__((visibility("default"))) int update_aimbot() {
    if (!is_active) return 0;
    
    Player players[32];
    return get_players(players, 32);
}

__attribute__((visibility("default"))) void cleanup_aimbot() {
    is_active = 0;
    target_pid = 0;
    client_module = 0;
}