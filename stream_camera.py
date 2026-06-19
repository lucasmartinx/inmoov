import cv2
import socket
import struct
import time

IP_DO_WEMOS = "192.168.0.41"
PORTA_UDP = 5555

# Abre a câmera diretamente no nó do Linux
print("Iniciando captura do /dev/video0...")
cap = cv2.VideoCapture(0)

# Força a resolução baixa para a Biocam não afogar o Wemos
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao ler frame. Tentando reconectar...")
            time.sleep(1)
            continue
        
        # Converte a imagem para RGB565 (formato de telas de microcontrolador)
        frame_rgb565 = cv2.cvtColor(frame, cv2.COLOR_BGR2BGR565)
        frame_bytes = frame_rgb565.tobytes()

        # Envia linha por linha (320 linhas)
        for linha in range(320):
            inicio = linha * 960 # 480 pixels * 2 bytes
            fim = inicio + 960
            pacote = struct.pack('>H', linha) + frame_bytes[inicio:fim]
            sock.sendto(pacote, (IP_DO_WEMOS, PORTA_UDP))
            
        # Pequeno respiro para a rede
        time.sleep(0.01)

except KeyboardInterrupt:
    print("Encerrando...")
finally:
    cap.release()
    sock.close()