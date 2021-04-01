import socket
import time
import random
import hashlib


RECEIVER_ADDR = ('localhost', 8080)
SENDER_ADDR = ('localhost', 9090)
PACKET_SIZE = 2048
BUFFER_SIZE = 20 * PACKET_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(RECEIVER_ADDR)

expected_seq_num = 0

file = open("output", "wb")

packets = dict()

rwnd = BUFFER_SIZE


def helper(recv_data, packet_length):
    global expected_seq_num, rwnd
    expected_seq_num += packet_length
    while str(expected_seq_num) in packets.keys():
        next_packet_data, next_packet_length = packets[str(expected_seq_num)]
        recv_data += next_packet_data
        expected_seq_num += next_packet_length
        rwnd += next_packet_length
    file.write(recv_data)


def send_ack(SYN_bit, FIN_bit):
    global expected_seq_num, rwnd
    ack_send = "SYN=" + str(SYN_bit) + ":FIN=" + \
        str(FIN_bit) + ":rwnd=" + str(rwnd) + ":ack=" + str(expected_seq_num)
    if random.randint(0, 10) > 0:
        print(f'Packet Sent with ACK is {expected_seq_num} at {time.time()}')
        sock.sendto(ack_send.encode(), SENDER_ADDR)
    else:
        print(
            f'Packet with ACK {expected_seq_num} going to Lost at {time.time()}')


while True:
    message, _ = sock.recvfrom(PACKET_SIZE)
    packet_length = len(message)
    temp = message.decode('latin-1').split(':')
    SYN_recv = int(temp[0][4])
    FIN_recv = int(temp[1][4])
    recv_seq_num = int(temp[2][4:])

    print(f'Sequence Number Received is {recv_seq_num} at {time.time()}')

    if SYN_recv == 1 and expected_seq_num == recv_seq_num:
        expected_seq_num += packet_length
        send_ack(1, 0)
    elif SYN_recv == 1:
        send_ack(1, 0)
    elif FIN_recv == 1 and expected_seq_num == recv_seq_num:
        send_ack(0, 0)
        send_ack(0, 1)
        file.close()
    else:
        data_start = len(temp[0])+len(temp[1])+len(temp[2])+len(temp[3])+4+5
        recv_data = message[data_start:]

        checksum_start = len(temp[0])+len(temp[1])+len(temp[2])+2
        data = message[:checksum_start] + message[data_start-6:]
        recv_checksum = temp[3][9:]
        computed_checksum = hashlib.md5(data).hexdigest()

        print(recv_checksum)
        print(computed_checksum)

        if computed_checksum != recv_checksum:
            print('Packet is Corrupted')
            continue

        if expected_seq_num == recv_seq_num:
            helper(recv_data, packet_length)
            send_ack(0, 0)
        elif recv_seq_num > expected_seq_num:
            packets[str(recv_seq_num)] = (recv_data, packet_length)
            rwnd -= packet_length
            send_ack(0, 0)
        else:
            send_ack(0, 0)
