from flask import Flask, Response
import cv2
import time
import threading
import socket
import struct

app = Flask(__name__)

# --- CONFIGURAÇÕES DA TELA ---
IP_ESP32 = "192.168.0.41" # IP do seu ESP32
PORTA_UDP = 5555
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Variável global que vai guardar a foto mais recente da câmera
frame_global = None

# 1. TAREFA: Ler a câmera sem parar
def leitor_de_camera():
    global frame_global
    cap = None
    indices = [0, 2, -1, 1, 10]
    
    print("Iniciando varredura do hardware da câmera...", flush=True)
    for index in indices:
        temp_cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
        if temp_cap.isOpened():
            for _ in range(5):
                sucesso, frame = temp_cap.read()
                if sucesso and frame is not None and frame.max() > 0:
                    cap = temp_cap
                    print(f"SUCESSO: Câmera travada no índice {index}!", flush=True)
                    break
            if cap is not None:
                break
            temp_cap.release()

    if cap is None:
        print("ERRO: Câmera não encontrada no hardware.", flush=True)
        return

    # Loop infinito lendo a câmera e atualizando a variável global
    while True:
        sucesso, frame = cap.read()
        if sucesso:
            # Gira a imagem 180 graus para corrigir a fixação invertida
           # frame = cv2.rotate(frame, cv2.ROTATE_180)
            
            frame_global = frame
        time.sleep(0.01)

# 2. TAREFA: Enviar para a tela física (UDP)
def transmissor_tela():
    global frame_global
    ultimo_frame = None

    print(f"Iniciando envio UDP para a tela no IP {IP_ESP32}...", flush=True)
    while True:
        # Só processa se houver imagem E se for uma imagem nova
        if frame_global is not None and frame_global is not ultimo_frame:
            try:
                # Fazemos uma cópia rápida para não travar a câmera
                frame_atual = frame_global.copy()
                ultimo_frame = frame_global

                # Processamento da imagem
                frame_resized = cv2.resize(frame_atual, (480, 320))
                frame_rgb565 = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2BGR565)
                frame_bytes = frame_rgb565.tobytes()

                # Envio em massa
                for linha in range(320):
                    pacote = struct.pack('>H', linha) + frame_bytes[linha*960:(linha+1)*960]
                    sock.sendto(pacote, (IP_ESP32, PORTA_UDP))
                    # Delay super reduzido para aumentar o FPS na telinha
                    time.sleep(0.0002) 
            except Exception as e:
                pass
        else:
            # Descansa o processador se não tem frame novo
            time.sleep(0.01) 

# 3. TAREFA: O Servidor de Internet (Flask)
def gen_frames():
    global frame_global
    ultimo_frame_web = None
    
    while True:
        # Só converte e envia se houver um frame novo
        if frame_global is not None and frame_global is not ultimo_frame_web:
            frame_atual_web = frame_global.copy()
            ultimo_frame_web = frame_global
            
            ret, buffer = cv2.imencode('.jpg', frame_atual_web)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.01)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return "Servidor Biocam online! Acesse /video_feed para o vídeo."

if __name__ == '__main__':
    # Inicia as tarefas de câmera e tela em segundo plano (Threads)
    thread_camera = threading.Thread(target=leitor_de_camera, daemon=True)
    thread_tela = threading.Thread(target=transmissor_tela, daemon=True)
    
    thread_camera.start()
    thread_tela.start()
    
    # Inicia o servidor web na porta 80
    app.run(host='0.0.0.0', port=80, threaded=True)