from socket import *
import struct

port = 8081
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', port))
print("Listening to %d"%port)

ACKAddr = ("127.0.0.1", 8080)

while True:
    with open('outfile.txt', 'a') as outfile:
        while True:
            packet, clientAddr = serverSocket.recvfrom(2048)
            header = struct.unpack("!HHLLBBHHH", packet[:20])            
            src, dest, seq_num, ack_num, header_len, controls, rcv_window, checksum, urgent_ptr = header            
            print(header)
            ACK = "ACK"
            serverSocket.sendto(ACK.encode(), ACKAddr)
            if controls & 1 == 1:
                outfile.close()
                break
            else:       
                print("write")  
                data = packet[20:].decode()       
                outfile.write(data)
                outfile.flush()
                