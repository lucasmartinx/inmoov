import socket
import pyaudio

# ==========================================
# 1. CONFIGURAÇÕES
# ==========================================
# Rede (Mesma porta do ESP32)
UDP_IP = "0.0.0.0"
UDP_PORT = 4444
BUFFER_SIZE = 2048 # Tamanho máximo do pacote

# Áudio (Tem que bater EXATAMENTE com o I2S do Wemos)
FORMATO = pyaudio.paInt16  # 16-bit
CANAIS = 1                 # Mono (Left channel)
TAXA_AMOSTRAGEM = 16000    # 16kHz (Sample Rate)

print("Iniciando motor de áudio (PyAudio)...")

# ==========================================
# 2. INICIALIZAÇÃO DOS MOTORES
# ==========================================
audio = pyaudio.PyAudio()

# Abre o canal de som para saída (alto-falante)
stream = audio.open(format=FORMATO,
                    channels=CANAIS,
                    rate=TAXA_AMOSTRAGEM,
                    output=True)

# Abre a "antena" de rede
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"========================================")
print(f"🔊 PRONTO! OUVINDO NA PORTA {UDP_PORT} E REPRODUZINDO...")
print(f"========================================")

# ==========================================
# 3. LOOP DE REPRODUÇÃO EM TEMPO REAL
# ==========================================
try:
    while True:
        # Recebe o pacote do ar
        data, addr = sock.recvfrom(BUFFER_SIZE)
        
        # Joga o dado cru direto para o alto-falante
        if data:
            stream.write(data)

except KeyboardInterrupt:
    print("\n🛑 Encerrando o sistema de áudio...")

finally:
    # Limpa a memória e desliga tudo graciosamente
    stream.stop_stream()
    stream.close()
    audio.terminate()
    sock.close()