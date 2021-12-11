# Introduction
In this project, we designed and implemented a reliable data transfer protocol build on top of UDP.
We make use of the link emulator for local testing.
# Design and Implementation
## TCP like Header
The TCP like Header has a fixed length of 20 bytes. The structure is as follows:
```python
"""
this format is used to encode TCP header
H | unsigned short
B | unsigned char
L | unsigned long
""" 
PACK_FORMAT = '!HHLLBBHHH'
header = struct.pack(
    PACK_FORMAT, # Data Structure Representation
    src_port,   # Source port
    dest_port,    # Destination port
    seq_num,    # Sequence Number
    ack_num,  # Acknownlegment Sequence Number
    header_len,   # Header Length
    contorls ,    # Contorls
    rcv_window,   # Windows
    checksum,  # cheksum
    urgent_ptr # Urgent Pointer
)
```
### Controls
The controls consists of a number of flags. The structure is as follows:
```python
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
```
## Checksum calculation
The checksum is calculated based on the algorithm in `RFC 1071`
```python
for i in range(0, len(data), 2):
    a = data[i%len(data)]
    b = data[(i+1)%len(data)]
    s = s + (a+(b << 8))
    s = s + (s >> 16)
    s = ~s & 0xffff
```
## Reading File
We read the input file using fixed size buffer. We keep track of the number of packets processed to find the correct starting location in the file using `f.seek()` and then read fix length of data using `f.read(chunk_size)`
```python
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
```
## Pipelining 
Multiple processes will be created based on the user specified window size. This is achieved by the `multiprocessing` package of Python. We keep track of the sequence counter, and pass it to the `read_send` function as an argument. The function will take this counter and generate the sequence number based on chunk size and header size. The sequence counter is also used to locate the correct location in the file.
```python
with multiprocessing.Pool(window_size) as p:
    # generate the sequence counter
    res = p.map(read_send, [i for i in range(k*window_size, (k+1)*window_size)])
```
## Sequence Number
The sequence number denotes that starting number of bytes of a packet. It is calculated based on number of packets sent, and the chunk size of each packet.
## ACK number
The ACK number received must be larger than the `sequence_number + chunk_size` of this packet, 
because that means the receiver has correctly received all the previous packets including the current one. Otherwise, the process will try to retransmit the data.

## Dynamic Timeout
The transmission function will record the first RTT and return the value for timeout update calculation.
The timeout is calculated like this:
```python
estimatedRTT = (1-alpha)*estimatedRTT+ alpha*sampleRTT
deviation= (1-beta)*deviation + beta*abs(sampleRTT-estimatedRTT)
timeout= estimatedRTT + 4*deviation
```