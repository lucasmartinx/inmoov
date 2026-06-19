import socket
import time

# O IP que aparece na tela do seu Wemos
IP_WEMOS = "192.168.0.41"
PORTA = 5555

print(f"Tentando enviar pacote para {IP_WEMOS}:{PORTA}...")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Vamos enviar a palavra "TESTE" 5 vezes para garantir que o Wemos perceba
for i in range(5):
    sock.sendto(b"TESTE", (IP_WEMOS, PORTA))
    print("Pacote enviado!")
    time.sleep(1)

sock.close()
print("Teste finalizado.")