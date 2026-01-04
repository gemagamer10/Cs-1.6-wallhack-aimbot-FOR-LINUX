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

// Estruturas para o aimbot
typedef struct {
    unsigned int health;
    unsigned int team;
    float x, y, z;
    unsigned int address;
} Player;

typedef struct {
    float x, y, z;
} Vector3;

// Offsets CS 1.6
#define OFFSET_HEALTH 0x6C
#define OFFSET_TEAM 0x78
#define OFFSET_ORIGIN 0x2C
#define OFFSET_VIEW_ANGLE 0x4C

// Variáveis globais
static int is_active = 0;
static pid_t target_pid = 0;
static unsigned long client_module = 0;

// Função para ler memória
int read_memory(pid_t pid, unsigned long addr, void *buffer, size_t size) {
    struct iovec local, remote;
    
    local.iov_base = buffer;
    local.iov_len = size;
    remote.iov_base = (void*)addr;
    remote.iov_len = size;
    
    return process_vm_readv(pid, &local, 1, &remote, 1, 0) == size ? 0 : -1;
}

// Função para escrever memória
int write_memory(pid_t pid, unsigned long addr, void *buffer, size_t size) {
    struct iovec local, remote;
    
    local.iov_base = buffer;
    local.iov_len = size;
    remote.iov_base = (void*)addr;
    remote.iov_len = size;
    
    return process_vm_writev(pid, &local, 1, &remote, 1, 0) == size ? 0 : -1;
}

// Função para encontrar o processo CS
int find_cs_process() {
    FILE *fp;
    char cmd[256];
    char line[256];
    
    snprintf(cmd, sizeof(cmd), "pgrep -f 'hl\\.exe|hlds'");
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

// Função para encontrar o módulo do cliente
unsigned long find_client_module() {
    FILE *fp;
    char line[256];
    char filename[256];
    unsigned long addr = 0;
    
    snprintf(filename, sizeof(filename), "/proc/%d/maps", target_pid);
    fp = fopen(filename, "r");
    
    if (!fp) return 0;
    
    while (fgets(line, sizeof(line), fp) != NULL) {
        if (strstr(line, "client.so") != NULL) {
            sscanf(line, "%lx", &addr);
            break;
        }
    }
    
    fclose(fp);
    return addr;
}

// Função principal do aimbot
void aim_at_target(Player *local, Player *target) {
    if (!local || !target || !target_pid) return;
    
    // Calcular direção para o alvo
    float dx = target->x - local->x;
    float dy = target->y - local->y;
    float dz = target->z - local->z;
    
    // Calcular ângulos (pitch e yaw)
    float distance = sqrt(dx*dx + dy*dy);
    float pitch = atan2f(dz, distance);
    float yaw = atan2f(dy, dx);
    
    // Escrever ângulos na memória do processo
    unsigned long view_angle_addr = target->address + OFFSET_VIEW_ANGLE;
    float angles[2] = {pitch, yaw};
    
    write_memory(target_pid, view_angle_addr, angles, sizeof(angles));
}

// Função para ler jogadores
int get_players(Player *players, int max_players) {
    if (!client_module || !target_pid) return 0;
    
    int count = 0;
    
    // Ler endereço do jogador local
    unsigned long local_player_addr = 0;
    read_memory(target_pid, client_module + 0x80, &local_player_addr, sizeof(local_player_addr));
    
    if (!local_player_addr) return 0;
    
    // Ler informações do jogador local
    Player local_player;
    read_memory(target_pid, local_player_addr + OFFSET_HEALTH, &local_player.health, sizeof(int));
    read_memory(target_pid, local_player_addr + OFFSET_TEAM, &local_player.team, sizeof(int));
    read_memory(target_pid, local_player_addr + OFFSET_ORIGIN, &local_player.x, sizeof(float) * 3);
    local_player.address = local_player_addr;
    
    // Escanear outros jogadores
    unsigned long entity_list = client_module + 0x400;
    
    for (int i = 1; i < max_players && count < 31; i++) {
        unsigned long entity_addr = 0;
        read_memory(target_pid, entity_list + i * 4, &entity_addr, sizeof(entity_addr));
        
        if (!entity_addr || entity_addr == local_player_addr) continue;
        
        Player player;
        read_memory(target_pid, entity_addr + OFFSET_HEALTH, &player.health, sizeof(int));
        read_memory(target_pid, entity_addr + OFFSET_TEAM, &player.team, sizeof(int));
        read_memory(target_pid, entity_addr + OFFSET_ORIGIN, &player.x, sizeof(float) * 3);
        player.address = entity_addr;
        
        // Verificar se é inimigo
        if (player.health > 0 && player.team != local_player.team) {
            players[count++] = player;
            aim_at_target(&local_player, &player);
        }
    }
    
    return count;
}

// Funções exportadas para injeção
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
    int count = get_players(players, 32);
    
    return count;
}

__attribute__((visibility("default"))) void cleanup_aimbot() {
    is_active = 0;
    target_pid = 0;
    client_module = 0;
}