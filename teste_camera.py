import cv2
import socket
import struct
import time
import sys

IP_DO_WEMOS = "192.168.0.41"
PORTA_UDP = 5555

print("Iniciando Biocam - Aguardando Hardware...")
sys.stdout.flush()

# Tentativa robusta de abertura de câmera
cap = None
while cap is None or not cap.isOpened():
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("Câmera não acessível. Tentando novamente em 2s...")
        time.sleep(2)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
print("Fluxo de vídeo estabelecido.")

try:
    while True:
        ret, frame = cap.read()
        if not ret: continue
        
        # Redimensionamento processado para o display TFT
        frame_pequeno = cv2.resize(frame, (480, 320))
        frame_rgb565 = cv2.cvtColor(frame_pequeno, cv2.COLOR_BGR2BGR565)
        frame_bytes = frame_rgb565.tobytes()

        # Transmissão cadenciada
        for linha in range(320):
            pacote = struct.pack('>H', linha) + frame_bytes[linha*960:(linha+1)*960]
            sock.sendto(pacote, (IP_DO_WEMOS, PORTA_UDP))
            time.sleep(0.002)
        time.sleep(0.05)
except Exception as e:
    print(f"Erro: {e}")