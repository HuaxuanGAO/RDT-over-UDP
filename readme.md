Link Emulator
./newudpl -vv -i 127.0.0.1:8080 -o 127.0.0.1:8081 -L 20 -B 20 -O 20 -C 5 -U 20
Receiver
Usage: $python3 receiver.py [file] [listening_port] [address_for_acks] [port_for_acks]
python3 receiver.py outfile.txt 8081 127.0.0.1 8080

Sender
Usage: $python3 sender.py [filename] [destination_IP] [destination_port] [window_size] [chunk_size] [ack_port]
python3 sender.py infile.txt 127.0.1.1 41192 5 200 8080