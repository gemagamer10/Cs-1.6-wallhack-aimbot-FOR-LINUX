// aimbot_cs16_linux_64bit.c
// Compilar com: gcc -shared -fPIC -o aimbot.so aimbot_cs16_linux_64bit.c -ldl

#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/uio.h>
#include <dlfcn.h>
#include <math.h>
#include <stdint.h>
#include <inttypes.h>
#include <dirent.h>

// Estruturas
typedef struct {
    uint32_t health;
    uint32_t team;
    float x, y, z;
    uintptr_t address;
} Player;

// Offsets PLACEHOLDERS - tens de substituir pelos reais!
#define OFFSET_HEALTH      0x90   // Comum em builds antigos (ex: 0x90 ou 0xFC)
#define OFFSET_TEAM        0x98   // Comum (ex: 0x98 ou 0xA0)
#define OFFSET_ORIGIN      0x34   // Posição (Vector3) - procura perto dos flags
#define OFFSET_VIEW_ANGLE  0x4C   // View angles (pitch/yaw/roll) - placeholder

// Variáveis globais
static int is_active = 0;
static pid_t target_pid = 0;
static uintptr_t client_module = 0;

// Funções de memória
int read_memory(pid_t pid, uintptr_t addr, void *buffer, size_t size) {
    struct iovec local, remote;
    local.iov_base = buffer;
    local.iov_len = size;
    remote.iov_base = (void *)addr;
    remote.iov_len = size;
    return process_vm_readv(pid, &local, 1, &remote, 1, 0) == (ssize_t)size ? 0 : -1;
}

int write_memory(pid_t pid, uintptr_t addr, const void *buffer, size_t size) {
    struct iovec local, remote;
    local.iov_base = (void *)buffer;
    local.iov_len = size;
    remote.iov_base = (void *)addr;
    remote.iov_len = size;
    return process_vm_writev(pid, &local, 1, &remote, 1, 0) == (ssize_t)size ? 0 : -1;
}

// Encontra PID do CS 1.6
int find_cs_process() {
    DIR *dir = opendir("/proc");
    if (!dir) return -1;

    struct dirent *ent;
    while ((ent = readdir(dir)) != NULL) {
        pid_t pid = atoi(ent->d_name);
        if (pid <= 0) continue;

        char path[256], line[256];
        snprintf(path, sizeof(path), "/proc/%d/comm", pid);
        FILE *fp = fopen(path, "r");
        if (fp) {
            if (fgets(line, sizeof(line), fp)) {
                line[strcspn(line, "\n")] = 0;
                if (strstr(line, "hl_linux") || strstr(line, "hlds") || strstr(line, "counter-strike")) {
                    fclose(fp);
                    closedir(dir);
                    return pid;
                }
            }
            fclose(fp);
        }
    }
    closedir(dir);
    return -1;
}

// Encontra base do client.so
uintptr_t find_client_module(pid_t pid) {
    char path[256];
    snprintf(path, sizeof(path), "/proc/%d/maps", pid);
    FILE *fp = fopen(path, "r");
    if (!fp) return 0;

    char line[512];
    uintptr_t addr = 0;
    while (fgets(line, sizeof(line), fp)) {
        if (strstr(line, "client.so") || strstr(line, "client_client.so")) {
            sscanf(line, "%" SCNx64 "-%*", &addr);
            break;
        }
    }
    fclose(fp);
    return addr;
}

// Calcula aim
void aim_at_target(Player *local, Player *target) {
    if (!local || !target || !target_pid) return;

    float dx = target->x - local->x;
    float dy = target->y - local->y;
    float dz = target->z - local->z;

    float dist = sqrtf(dx*dx + dy*dy + dz*dz);
    if (dist == 0) return;

    float pitch = -asinf(dz / dist) * (180.0f / M_PI);
    float yaw = atan2f(dy, dx) * (180.0f / M_PI);

    float angles[2] = { pitch, yaw };
    uintptr_t view_angle_addr = local->address + OFFSET_VIEW_ANGLE;
    write_memory(target_pid, view_angle_addr, angles, sizeof(angles));
}

// Loop de jogadores (placeholder - precisas dos endereços reais!)
int get_players(Player *players, int max_players) {
    if (!client_module || !target_pid) return 0;

    int count = 0;

    // PLACEHOLDER: local player e entity list - substitui por valores reais!
    uintptr_t local_player_addr = 0;  // Ex: client_module + 0xXXXXXXXX
    uintptr_t entity_list = 0;        // Ex: client_module + 0xYYYYYYYY

    if (!local_player_addr || !entity_list) return 0;

    Player local = {0};
    local.address = local_player_addr;

    read_memory(target_pid, local_player_addr + OFFSET_HEALTH, &local.health, sizeof(uint32_t));
    read_memory(target_pid, local_player_addr + OFFSET_TEAM, &local.team, sizeof(uint32_t));
    read_memory(target_pid, local_player_addr + OFFSET_ORIGIN, &local.x, sizeof(float)*3);

    for (int i = 1; i < max_players && count < 31; i++) {
        uintptr_t entity_addr = 0;
        read_memory(target_pid, entity_list + i * sizeof(uintptr_t), &entity_addr, sizeof(entity_addr));
        if (!entity_addr || entity_addr == local_player_addr) continue;

        Player p = {0};
        p.address = entity_addr;

        read_memory(target_pid, entity_addr + OFFSET_HEALTH, &p.health, sizeof(uint32_t));
        read_memory(target_pid, entity_addr + OFFSET_TEAM, &p.team, sizeof(uint32_t));
        read_memory(target_pid, entity_addr + OFFSET_ORIGIN, &p.x, sizeof(float)*3);

        if (p.health > 0 && p.health <= 100 && p.team != local.team) {
            players[count++] = p;
            aim_at_target(&local, &p);
        }
    }
    return count;
}

// Funções exportadas
__attribute__((visibility("default"))) int init_aimbot() {
    target_pid = find_cs_process();
    if (target_pid <= 0) return -1;
    client_module = find_client_module(target_pid);
    if (!client_module) return -1;
    is_active = 1;
    return 0;
}

__attribute__((visibility("default"))) int toggle_aimbot() {
    is_active = !is_active;
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