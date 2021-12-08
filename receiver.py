from socket import *
import struct

port = 8081
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', port))
print("Listening to %d"%port)

ACKAddr = ("127.0.0.1", 8080)

def calc_checksum(data):
    # According to RFC 1071 
    # https://www.rfc-editor.org/rfc/rfc1071
    s = 0  
    for i in range(0, len(data), 2):
        a = data[i]
        b = data[i+1]
        s = s + (a+(b << 8))
        s = s + (s >> 16)
        s = ~s & 0xffff
    return s

while True:
    with open('outfile.txt', 'a') as outfile:
        while True:
            packet, clientAddr = serverSocket.recvfrom(2048)
            header = struct.unpack("!HHLLBBHHH", packet[:20])            
            src, dest, seq_num, ack_num, header_len, controls, rcv_window, checksum, urgent_ptr = header   
            if checksum != calc_checksum(packet):
                serverSocket.sendto("Corrupted".encode(), ACKAddr)
            if controls & 1 == 1:
                outfile.close()
                serverSocket.sendto("FIN".encode(), ACKAddr)
                break
            else:       
                print("write")  
                data = packet[20:].decode()       
                outfile.write(data)
                serverSocket.sendto("ACK".encode(), ACKAddr)
                