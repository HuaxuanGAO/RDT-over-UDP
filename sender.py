from socket import *
from multiprocessing import Process
import struct

def initHeader(fin):
    src_port = 8080
    dest_port = 8081
    seq_num = 0
    ack_num = 0
    header_len = 20
    
    RSV = (0 << 9)
    NOC = (0 << 8)
    CWR = (0 << 7)
    ECE = (0 << 6)
    URG = (0 << 5)
    ACK = (0 << 4)
    PSH = (0 << 3)
    RST = (0 << 2)
    SYN = (1 << 1)
    FIN = (fin)
  
    rcv_window = 80
    checksum = 0
    urgent_ptr = 0

    contorls = RSV + NOC + CWR + ECE + URG + ACK + PSH + RST + SYN + FIN

    header = struct.pack('!HHLLBBHHH', # Data Structure Representation
        src_port,   # Source IP
        dest_port,    # Destination IP
        seq_num,    # Sequence
        ack_num,  # Acknownlegment Sequence
        header_len,   # Header Length
        contorls ,    # Contorls
        rcv_window,   # Windows
        checksum,  # cheksum
        urgent_ptr # Urgent Pointer
    )
    print(header)
    return header

def sendDataUntilACK(data, clientSocket):
    ACK = None
    while not ACK:
        try:
            clientSocket.sendto(data, (serverName, serverPort))
            ACK, serverAddr = clientSocket.recvfrom(2048)
            print(ACK.decode())
        except:
            print("Not ACKed")
            continue

HOST = '127.0.0.1'
PORT = 8080
ADDR = (HOST, PORT)

serverName = "127.0.1.1"
serverPort = 41192

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(ADDR)
clientSocket.settimeout(1)

with open('infile.txt') as openfileobject:
    for line in openfileobject:
        print(line)
        header = initHeader(fin=0)
        data = line.encode()
        packet = header + data
        sendDataUntilACK(packet, clientSocket)

header = initHeader(fin=1)
sendDataUntilACK(header, clientSocket)
clientSocket.close()