from socket import *
import multiprocessing
import struct
import sys

"""
this format is used to encode TCP header
H | unsigned short
B | unsigned char
L | unsigned long
""" 
PACK_FORMAT = '!HHLLBBHHH'

# initialize the header
def initHeader(fin = 0, seq = 0):
    src_port = 8080
    dest_port = 8081
    seq_num = seq
    ack_num = 0
    header_len = 20
    #  place the controls using bit shift
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

    header = struct.pack(PACK_FORMAT, # Data Structure Representation
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
    return header

# calculate the checksum
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

# calculate checksum and put it in the header
def generate_packet(header, data=b''):        
    checksum = calc_checksum(header + data)
    old_header = struct.unpack(PACK_FORMAT, header)            
    src, dest, seq_num, ack_num, header_len, controls, rcv_window, prev_checksum, urgent_ptr = old_header
    new_header = struct.pack(PACK_FORMAT, src, dest, seq_num, ack_num, header_len, controls, rcv_window, checksum, urgent_ptr)
    return new_header + data

# keep sending with timeout until ACKed
def sendDataUntilACK(remote_IP, remote_port, packet, clientSocket, seq = 0, data_len = 0):
    ACK = False
    while not ACK:
        try:
            print("sending packet with sequence number: " + str(seq))
            clientSocket.sendto(packet, (remote_IP, remote_port))
            res, serverAddr = clientSocket.recvfrom(2048)
            print("received ACK of " + res.decode())
            #  already ACKed
            if int(res.decode()) >= seq + data_len:                
                ACK = True
        except:
            # "Not ACKed"
            continue

def take_input():
    try:
        print(sys.argv)
        filename = sys.argv[1]
        remote_IP = sys.argv[2]
        remote_port = int(sys.argv[3])
        window_size = int(sys.argv[4])
        ack_port = int(sys.argv[5])
    except:
        exit("Usage: $python3 sender.py [filename] [destination_IP] [destination_port] [window_size] [ack_port]")
    return filename, remote_IP, remote_port, window_size, ack_port

if __name__ == "__main__":
    filename, remote_IP, remote_port, window_size, ack_port = take_input()

    ADDR = ('', ack_port)   
    TIMEOUT = 1
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind(ADDR)
    clientSocket.settimeout(TIMEOUT)

    MAX_SEGMENT_SIZE = 576
    HEADER_LEN = 20
    chunk_size = MAX_SEGMENT_SIZE - HEADER_LEN
    # sendFile(filename, remote_IP, remote_port, CHUNK_SIZE, window_size, clientSocket)
    with open(filename, 'rb') as infile:
        EOF = False
        def read_send(seq_count):
            # go to the desired location
            infile.seek(seq_count*chunk_size) 
            # read fixed length data 
            chunk = infile.read(chunk_size)
            # EOF reached
            if not chunk:
                return True
            else:
                header = initHeader(fin=0, seq = seq_count * chunk_size)     
                packet = generate_packet(header, chunk)
                sendDataUntilACK(remote_IP, remote_port, packet, clientSocket, seq_count * chunk_size, data_len = len(chunk))
                return False
        k = 0    
        while not EOF:
            # Create a thread pool of size of the window
            with multiprocessing.Pool(window_size) as p:
                # generate the sequence counter
                res = p.map(read_send, [i for i in range(k*window_size, (k+1)*window_size)])
                # if any item is True in the result, that means we finished reading
                if any(res):
                    break
            k += 1
    # sending the FIN request
    header = initHeader(fin=1)
    packet = generate_packet(header)
    sendDataUntilACK(remote_IP, remote_port, packet, clientSocket)
    clientSocket.close()
