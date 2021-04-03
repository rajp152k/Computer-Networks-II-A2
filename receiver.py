import logging
import socket
import time
import random
import hashlib
import argparse

from pathlib import Path
from datetime import datetime

parser = argparse.ArgumentParser(description='Receiver')

parser.add_argument('-o', '--output', default='outfile', type=str)

args = parser.parse_args()

now = datetime.now().strftime("%d-%m-%Y__%H:%M:%S")
(Path()/'receiver_logs').mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    filename=f'./receiver_logs/recvr_{now}.log',
    filemode='w')
logging.info('receiver initiated')

RECEIVER_ADDR = ('10.0.10.2', 8080)
SENDER_ADDR = ('10.0.10.1', 9090)
PACKET_SIZE = 1024 * 5
BUFFER_SIZE = 50 * PACKET_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(RECEIVER_ADDR)

logging.info(f'socket bound to {RECEIVER_ADDR}')

expected_seq_num = 0

file = open(args.output, "wb")

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
    logging.info(f'IO : {expected_seq_num}B written on file till now')


def send_ack(SYN_bit, FIN_bit):
    global expected_seq_num, rwnd
    ack_send = "SYN=" + str(SYN_bit) + ":FIN=" + str(FIN_bit) + \
        ":rwnd=" + str(rwnd) + ":ack=" + str(expected_seq_num)
    sock.sendto(ack_send.encode(), SENDER_ADDR)
    logging.info(f'OUT ==> sending ack no. {expected_seq_num}')


while True:
    try:
        message, _ = sock.recvfrom(PACKET_SIZE)
    except KeyboardInterrupt:
        print(f'KeyboardInterrupt: terminating receiver')
        break
    packet_length = len(message)
    temp = message.decode('latin-1').split(':')

    SYN_recv = int(temp[0][4])
    FIN_recv = int(temp[1][4])
    recv_seq_num = int(temp[2][4:])

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

        logging.info(f'IN <== received packet num {recv_seq_num}')

        checksum_start = len(temp[0])+len(temp[1])+len(temp[2])+2
        data = message[:checksum_start] + message[data_start-6:]
        recv_checksum = temp[3][9:]
        computed_checksum = hashlib.md5(data).hexdigest()

        if computed_checksum != recv_checksum:
            logging.info(f'Packet {recv_seq_num} was corrupted')
            continue

        if expected_seq_num == recv_seq_num:
            helper(recv_data, packet_length)
            send_ack(0, 0)
        elif recv_seq_num > expected_seq_num:
            logging.info(f'IO : buffering packet {recv_seq_num}')
            packets[str(recv_seq_num)] = (recv_data, packet_length)
            rwnd -= packet_length
            send_ack(0, 0)
        else:
            send_ack(0, 0)
