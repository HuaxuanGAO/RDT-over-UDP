from socket import *
import multiprocessing
import struct
from builtins import bytes

def initHeader(fin = 0, seq = 0):
    # initialize the header
    src_port = 8080
    dest_port = 8081
    seq_num = seq
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

def calc_checksum(data):
    # https://www.rfc-editor.org/rfc/rfc1071
    s = 0  
    for i in range(0, len(data), 2):
        a = data[i%len(data)]
        b = data[(i+1)%len(data)]
        s = s + (a+(b << 8))
        s = s + (s >> 16)
        s = ~s & 0xffff
    return s

def generate_packet(header, data=b''):        
    checksum = calc_checksum(header + data)
    old_header = struct.unpack("!HHLLBBHHH", header)            
    src, dest, seq_num, ack_num, header_len, controls, rcv_window, prev_checksum, urgent_ptr = old_header
    new_header = struct.pack('!HHLLBBHHH', src, dest, seq_num, ack_num, header_len, controls, rcv_window, checksum, urgent_ptr)
    return new_header + data

def sendDataUntilACK(packet, clientSocket, seq = 0, data_len = 0):
    ACK = False
    while not ACK:
        try:
            print("sending " + str(seq))
            clientSocket.sendto(packet, (serverName, serverPort))
            res, serverAddr = clientSocket.recvfrom(2048)
            print(res.decode() + " vs " + str(seq))
            #  already ACKed
            if int(res.decode()) >= seq + data_len:                
                ACK = True
        except:
            # print("Not ACKed")
            continue

HOST = '127.0.0.1'
PORT = 8080
ADDR = (HOST, PORT)

serverName = "127.0.1.1"
serverPort = 41192

CHUNK_SIZE = 556 # 576-20
SEQ_NUM = 0
WINDOW_SIZE = 5
TIMEOUT = 1
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(ADDR)
clientSocket.settimeout(TIMEOUT)



with open('infile.txt', 'rb') as infile:
    EOF = False
    def read_send(seq_count):
        infile.seek(seq_count*CHUNK_SIZE)
        chunk = infile.read(CHUNK_SIZE)
        if not chunk:
            return True
        else:
            header = initHeader(fin=0, seq = seq_count * CHUNK_SIZE)     
            packet = generate_packet(header, chunk)
            sendDataUntilACK(packet, clientSocket, seq_count * CHUNK_SIZE, data_len = len(chunk))
            return False
    k = 0    
    while not EOF:
        with multiprocessing.Pool(WINDOW_SIZE) as p:
            res = p.map(read_send, [i for i in range(k*WINDOW_SIZE, (k+1)*WINDOW_SIZE)])
            if any(res):
                break
        k += 1

header = initHeader(fin=1)
packet = generate_packet(header)
sendDataUntilACK(packet, clientSocket)
clientSocket.close()