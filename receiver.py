from socket import *
import struct

port = 8081
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', port))
print("Listening to %d"%port)

ACKAddr = ("127.0.0.1", 8080)

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

MAX_SEGMENT_SIZE = 576
expected_seq = 0

while True:
    with open('outfile.txt', 'a') as outfile:
        while True:
            packet, clientAddr = serverSocket.recvfrom(2048)
            header = struct.unpack("!HHLLBBHHH", packet[:20])
            data = packet[20:]
            chunk_size = len(data)            
            src, dest, seq_num, ack_num, header_len, controls, rcv_window, checksum, urgent_ptr = header 
            print(header)            
            old_header = struct.pack('!HHLLBBHHH', src, dest, seq_num, ack_num, header_len, controls, rcv_window, 0, urgent_ptr)
            if checksum != calc_checksum(old_header+data):
                break
            # FIN received 
            if controls & 1 == 1:
                outfile.close()
                serverSocket.sendto("0".encode(), ACKAddr)
                expected_seq = 0
                break
            if seq_num != expected_seq:
                serverSocket.sendto(str(expected_seq).encode(), ACKAddr)
            else:
                expected_seq += chunk_size
                print(str(seq_num) + " received, expecting: " + str(expected_seq))
                data = data.decode()       
                outfile.write(data)
                outfile.flush()
                serverSocket.sendto(str(expected_seq).encode(), ACKAddr)
                