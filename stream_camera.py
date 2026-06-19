from flask import Flask, Response
import cv2
import time

app = Flask(__name__)

print("Iniciando servidor Biocam...", flush=True)

# Sistema de varredura: testa os índices onde o Pi 4 costuma esconder a câmera real
cap = None
indices_para_testar = [0, 2, -1, 1, 10] 

for index in indices_para_testar:
    print(f"Testando câmera no índice {index}...", flush=True)
    temp_cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
    
    if temp_cap.isOpened():
        # Tenta ler alguns frames para dar tempo do sensor acordar e checar se não é tela preta
        sucesso = False
        frame_valido = None
        for _ in range(5):
            sucesso, frame_teste = temp_cap.read()
            # frame.max() > 0 verifica se a imagem não é 100% composta de pixels pretos (valor 0)
            if sucesso and frame_teste is not None and frame_teste.max() > 0:
                frame_valido = True
                break
            time.sleep(0.2)
            
        if frame_valido:
            print(f"SUCESSO! Câmera com imagem real encontrada no índice {index}!", flush=True)
            cap = temp_cap
            break
        else:
            print(f"Índice {index} conectou, mas só enviou tela preta. Descartando...", flush=True)
            temp_cap.release()

if cap is None:
    print("ERRO CRÍTICO: Nenhuma câmera com imagem real encontrada. O cabo flat pode estar invertido ou as variáveis do Balena ausentes.", flush=True)

def gen_frames():
    if cap is None:
        # Se não achou câmera, mantém o gerador vivo mas sem enviar imagem para não travar o Flask
        while True:
            time.sleep(1)
            
    while True:
        success, frame = cap.read()
        if not success:
            time.sleep(0.1)
            continue
        
        # Converte o frame do OpenCV para JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        # Formata como stream para o navegador
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return "Servidor Biocam online! Acesse a rota /video_feed para visualizar a câmera."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=True)