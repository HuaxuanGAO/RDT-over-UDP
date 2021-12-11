# Project Structure
* newudpl: The Link Emulator binary
* infile.txt: The input file for sender to read
* outfile.txt: The output file created by receiver, with content identical to input file
* readme.md: Description and instruction of the project
* sender.py: The sender that sends a file to link emulator
* receiver.py: The receiver that get data from the link emulator, and send ACKs directly to the sender

# Instruction to run
1. Start the Link emulator 
   
   `./newudpl -vv -i 127.0.0.1:8080 -o 127.0.0.1:8081 -L 20 -B 20 -O 20 -C 5 -U 20`
2. Start the Receiver 
   
   Usage: `python3 receiver.py [file] [listening_port] [address_for_acks] [port_for_acks]`
   * file: output filename
   * listening_port: The port that receiver process listens to
   * address_for_acks: The IP to send ACKs to
   * port_for_acks: The port to send ACKs to
  
   Example: `python3 receiver.py outfile.txt 8081 127.0.0.1 8080`

3. Start the Sender 
   
   Usage: `python3 sender.py [filename] [destination_IP] [destination_port] [window_size] [chunk_size] [ack_port]`
   * file: input filename
   * destination_IP: The IP of the link emulator
   * destination_port: The port of the link emulator
   * window_size: The number of packets to send in concurrently in pipeline
   * chunk_size: The number of bytes contained in the data of each packet, this number should be less than max_segment_size - header_len = 576 - 20 = 556
   * ack_port: The port that sender binds to, will listen for ACKs
  
   Example: `python3 sender.py infile.txt 127.0.1.1 41192 5 200 8080`

# Features
- [x] Dynamic timeout calculation
- [x] Pipelining, user specified #concurrent packets
- [x] User specified packet size
- [x] TCP Header fields
  - [x]  Source port #
  - [x]  Dest port #
  - [x]  Sequence number
  - [x]  ACK number
  - [x]  Header Length
  - [x]  RSV
  - [x]  NOC    
  - [x]  CWR
  - [x]  ECE
  - [x]  URG
  - [x]  ACK
  - [x]  PSH
  - [x]  RST
  - [x]  SYN
  - [x]  FIN
  - [x]  rcv_window
  - [x]  checksum
  - [x]  urgent_ptr