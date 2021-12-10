from socket import *
import struct
import sys

PACK_FORMAT = '!HHLLBBHHH'

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
                
# tcpserver file listening_port address_for_acks port_for_acks
def take_input():
    try:
        print(sys.argv)
        filename = sys.argv[1]
        listen_port = int(sys.argv[2])
        ack_IP = sys.argv[3]
        ack_port = int(sys.argv[4])
    except:
        exit("Usage: $python3 receiver.py [file] [listening_port] [address_for_acks] [port_for_acks]")
    return filename, listen_port, ack_IP, ack_port

if __name__ == "__main__":
    filename, listen_port, ack_IP, ack_port = take_input()
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', listen_port))
    print("Listening to %d"%listen_port)

    ACKAddr = (ack_IP, ack_port)
    MAX_SEGMENT_SIZE = 576
    HEADER_LEN = 20
    expected_seq = 0

    with open('outfile.txt', 'wb') as outfile:
        while True:
            packet, clientAddr = serverSocket.recvfrom(MAX_SEGMENT_SIZE)
            header = struct.unpack(PACK_FORMAT, packet[:HEADER_LEN])
            data = packet[HEADER_LEN:]
            chunk_size = len(data)            
            src, dest, seq_num, ack_num, header_len, controls, rcv_window, checksum, urgent_ptr = header 
            old_header = struct.pack(PACK_FORMAT, src, dest, seq_num, ack_num, header_len, controls, rcv_window, 0, urgent_ptr)
            if checksum != calc_checksum(old_header+data):
                print("Received corrupted packet, expecting: " + str(expected_seq))
                continue
            # FIN received 
            if controls & 1 == 1:
                print("Received FIN request")
                outfile.close()
                serverSocket.sendto("0".encode(), ACKAddr)
                expected_seq = 0
                break
            if seq_num != expected_seq:
                print("Received out of order packet, dump")
                serverSocket.sendto(str(expected_seq).encode(), ACKAddr)
            else:
                expected_seq += chunk_size
                print(str(seq_num) + " received, expecting: " + str(expected_seq))
                outfile.write(data)
                outfile.flush()
                serverSocket.sendto(str(expected_seq).encode(), ACKAddr)