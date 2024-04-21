import socket

def send_to_esp32(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        s.sendall(message.encode())

esp_ip = '192.168.20.116'  # IP of the ESP32
port = 80                 # Port number must match the ESP32 server

while True:
    number = input("Enter a number to send: ")
    send_to_esp32(esp_ip, port, number)