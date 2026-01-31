import math

class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def distance_to(self, other):
        return (self - other).length()

def calc_angle(source, dest):
    """
    Calcula pitch e yaw de source para dest
    Retorna tuple (pitch, yaw) em graus
    """
    delta = dest - source
    hypot = math.sqrt(delta.x**2 + delta.y**2)

    if hypot < 1.0:
        hypot = 1.0

    # Pitch: negativo porque o eixo Z no CS é invertido (olhar para cima = pitch negativo)
    pitch = math.degrees(math.atan2(-delta.z, hypot))
    yaw = math.degrees(math.atan2(delta.y, delta.x))

    return pitch, yaw

def normalize_angles(pitch, yaw):
    """
    Normaliza os ângulos para valores válidos no jogo
    Retorna tuple (pitch, yaw)
    """
    # Pitch entre -89 e 89
    if pitch > 89.0:
        pitch = 89.0
    elif pitch < -89.0:
        pitch = -89.0

    # Yaw entre -180 e 180
    while yaw > 180.0:
        yaw -= 360.0
    while yaw < -180.0:
        yaw += 360.0

    return pitch, yaw