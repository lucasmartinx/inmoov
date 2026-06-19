import socket
import struct
import numpy as np
import time

# O IP do seu Wemos
IP_WEMOS = "192.168.0.41"
PORTA = 5555
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Enviando padrão de teste para o Wemos...")

# Cria uma imagem de teste (480x320) com listras coloridas
frame = np.zeros((320, 480, 3), dtype=np.uint8)
frame[:, :, 0] = 255 # Azul

# Converte para RGB565 (o formato que o TFT espera)
def to_rgb565(r, g, b):
    return struct.pack('>H', ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3))

for i in range(320):
    linha_bytes = bytearray()
    for j in range(480):
        # Cria um padrão de cores que muda a cada linha
        linha_bytes += to_rgb565(i % 255, j % 255, 100)
    
    # Envia linha: [2 bytes linha] + [960 bytes imagem]
    pacote = struct.pack('>H', i) + linha_bytes
    sock.sendto(pacote, (IP_WEMOS, PORTA))
    time.sleep(0.005)

print("Teste enviado. Olhe para a tela do Wemos.")