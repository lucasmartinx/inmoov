import socket
import pyaudio

UDP_IP = "0.0.0.0"
UDP_PORT = 4444
TAXA_AMOSTRAGEM = 16000
CANAIS = 1
FORMATO = pyaudio.paInt16

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

p = pyaudio.PyAudio()
stream = p.open(format=FORMATO, channels=CANAIS, rate=TAXA_AMOSTRAGEM, output=True)

print(f"Sistema InMoov Escutando na porta {UDP_PORT}...")

try:
    while True:
        dados, addr = sock.recvfrom(1024) 
        stream.write(dados)
except KeyboardInterrupt:
    pass
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    sock.close()