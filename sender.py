from socket import *
from multiprocessing import Process
import time

HOST = '127.0.0.1'
PORT = 8080
ADDR = (HOST, PORT)

serverName = "127.0.1.1"
serverPort = 41192

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(ADDR)
clientSocket.settimeout(1)

def sendDataUntilACK(data, clientSocket):
    ACK = None
    while not ACK:
        try:
            clientSocket.sendto(msg_encode, (serverName, serverPort))
            ACK, serverAddr = clientSocket.recvfrom(2048)
            print(ACK.decode())
        except:
            continue

message = "Hello Socket!"
msg_encode = message.encode()
sendDataUntilACK(msg_encode, clientSocket)
clientSocket.close()