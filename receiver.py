from socket import *
port = 8081
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', port))
print("Listening to %d"%port)

ACKAddr = ("127.0.0.1", 8080)

while True:
    msg, clientAddr = serverSocket.recvfrom(2048)
    msg = msg.decode()
    print("Received: " + msg)
    ACK = "ACK"
    serverSocket.sendto(ACK.encode(), ACKAddr)