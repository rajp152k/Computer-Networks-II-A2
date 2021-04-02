import logging
import socket
import random
import time
import _thread
import os
import hashlib

from pathlib import Path
from datetime import datetime

now = datetime.now().strftime("%d-%m-%Y__%H:%M:%S")
(Path()/'sender_logs').mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(message)s',
    filename=f'./sender_logs/sendr_{now}.log',
    filemode='w')
logging.info('sender initiated')

RECEIVER_ADDR = ('10.0.10.2', 8080)
SENDER_ADDR = ('10.0.10.1', 9090)
TIMEOUT_INTERVAL = 1
PACKET_SIZE = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(SENDER_ADDR)

logging.info(f'socket bound to {SENDER_ADDR}')

SLOW_START = 1
CONGESTION_AVOIDANCE = 2
FAST_RECOVERY = 3

CONGESTION_STATE = SLOW_START

MSS = PACKET_SIZE

cwnd = 1 * MSS
ssthresh = 64 * 1024

next_seq_num = 0
expected_ack_number = 0
rwnd = None
start_time = -1

packets = dict()
count = dict()

lock = _thread.allocate_lock()

completed = False

total_timeout_packets = 0
total_fast_retransmit = 0

# the name of file we want to send, make sure it exists
filename = "test-1MB"
# get the file size
filesize = os.path.getsize(filename)
file = open(filename, "rb")


def get_packet(seq_num, SYN_bit, FIN_bit):
    global next_seq_num, PACKET_SIZE, packets
    if SYN_bit == 1:
        temp = ("SYN=1:FIN=0:seq="+str(next_seq_num)).encode()
        checksum = hashlib.md5(temp)
        data = ("SYN=1:FIN=0:seq="+str(next_seq_num) +
                ":checksum="+checksum.hexdigest()).encode()
    elif FIN_bit == 1:
        temp = ("SYN=0:FIN=1:seq="+str(next_seq_num)).encode()
        checksum = hashlib.md5(temp)
        data = ("SYN=0:FIN=1:seq="+str(next_seq_num) +
                ":checksum="+checksum.hexdigest()).encode()
    else:
        if str(seq_num) in packets.keys():
            return packets[str(seq_num)]
        else:
            data = file.read(PACKET_SIZE)
            if not data:
                logging.info('IO : file exhausted')
                return None
            temp = ("SYN=0:FIN=0:seq=" +
                    str(next_seq_num) + ":data=").encode() + data
            checksum = hashlib.md5(temp)
            data = ("SYN=0:FIN=0:seq=" +
                    str(next_seq_num) + ":checksum=" + checksum.hexdigest() + ":data=").encode() + data

    packets[str(next_seq_num)] = data
    return data


def send(next_packet, seq_num):
    global sock
    logging.info(
        f'OUT ==> sending packet : {next_seq_num}, size :{len(next_packet)}')
    sock.sendto(next_packet, RECEIVER_ADDR)


def send_packet(seq_num, is_retransmission):
    lock.acquire()
    global start_time, expected_ack_number
    if not is_retransmission:
        global next_seq_num
        next_packet = get_packet(next_seq_num, 0, 0)
        if next_packet == None:
            lock.release()
            return False
        while (next_seq_num - expected_ack_number + len(next_packet)) <= min(cwnd, rwnd):
            send(next_packet, next_seq_num)
            next_seq_num += len(next_packet)
            next_packet = get_packet(next_seq_num, 0, 0)
            if next_packet == None:
                lock.release()
                return False
    else:
        packet_resent = get_packet(seq_num, 0, 0)
        logging.info(f'OUT ==> resending packet {seq_num}')
        send(packet_resent, seq_num)
        logging.info('resetting timer')
        start_time = time.time()
    if start_time == -1:
        logging.info('starting timer')
        start_time = time.time()
    lock.release()
    return True


def timer_thread():
    global completed, expected_ack_number, start_time, ssthresh, cwnd, CONGESTION_STATE, total_timeout_packets
    while not completed:
        if start_time != -1 and time.time() - start_time > TIMEOUT_INTERVAL:
            logging.info(
                f'TIMEOUT : Resending packet num : {expected_ack_number}')
            send_packet(expected_ack_number, True)
            total_timeout_packets += 1
            ssthresh = cwnd/2
            cwnd = 1 * MSS
            CONGESTION_STATE = SLOW_START


def main_thread():
    send_packet(None, False)

    while True:
        global start_time, expected_ack_number, completed, next_seq_num, rwnd, CONGESTION_STATE, cwnd, MSS, ssthresh, total_fast_retransmit

        if CONGESTION_STATE == SLOW_START and cwnd >= ssthresh:
            CONGESTION_STATE = CONGESTION_AVOIDANCE

        message, _ = sock.recvfrom(1024)
        message = message.decode()
        message = message.split(':')
        recv_ack = int(message[3][4:])
        recv_rwnd = int(message[2][5:])
        rwnd = recv_rwnd
        logging.info(f'IN <== ACK NO : {recv_ack}')

        if recv_ack > expected_ack_number:
            count[str(recv_ack)] = 1
            expected_ack_number = recv_ack
            if expected_ack_number == next_seq_num:
                start_time = -1
            else:
                start_time = time.time()

            if CONGESTION_STATE == SLOW_START:
                cwnd += MSS
            elif CONGESTION_STATE == CONGESTION_AVOIDANCE:
                cwnd += MSS * (MSS/cwnd)
            else:
                CONGESTION_STATE = CONGESTION_AVOIDANCE
                cwnd = ssthresh

            success = send_packet(None, False)
            if success == False and next_seq_num == expected_ack_number:
                return
        else:
            if(str(recv_ack) in count.keys()):
                count[str(recv_ack)] += 1
                if count[str(recv_ack)] == 3:
                    CONGESTION_STATE = FAST_RECOVERY
                    ssthresh = cwnd / 2
                    cwnd = ssthresh + 3 * MSS
                    logging.info(
                        f'FAST RETRANSMIT {expected_ack_number} at {time.time()}')
                    send_packet(expected_ack_number, True)
                    total_fast_retransmit += 1
                elif CONGESTION_STATE == FAST_RECOVERY:
                    cwnd += MSS


def connection_establishment():
    global next_seq_num, expected_ack_number, start_time, rwnd
    first_handshake = get_packet(next_seq_num, 1, 0)
    send(first_handshake, next_seq_num)
    start_time = time.time()
    _thread.start_new_thread(timer_thread, ())
    logging.info('timer thread dispatched')

    next_seq_num += len(first_handshake)
    second_handshake, _ = sock.recvfrom(1024)
    message = second_handshake.decode()
    message = message.split(':')
    SYN_recv = int(message[0][4])
    recv_ack = int(message[3][4:])
    recv_rwnd = int(message[2][5:])
    rwnd = recv_rwnd
    logging.info(f'Received Ack {recv_ack,recv_rwnd}')
    count[str(recv_ack)] = 1
    if SYN_recv != 1 and next_seq_num != recv_ack:
        logging.info('CONNECTION ATTEMPT FAILED')
        return False
    else:
        expected_ack_number = recv_ack
        start_time = -1
        logging.info('CONNECTION ESTABLISHED')
        return True


def close_connection():
    global next_seq_num, expected_ack_number, start_time, completed
    first_request = get_packet(next_seq_num, 0, 1)
    send(first_request, next_seq_num)
    start_time = time.time()
    next_seq_num += len(first_request)
    message, _ = sock.recvfrom(1024)
    message = message.decode().split(':')
    fin_recv = message[1][4]
    while fin_recv == 1:
        message, _ = sock.recvfrom(1024)
        message = message.decode().split(':')
        fin_recv = message[1][4]
    message, _ = sock.recvfrom(1024)
    message = message.decode().split(':')
    fin_recv = message[1][4]
    while fin_recv == 0:
        message, _ = sock.recvfrom(1024)
        message = message.decode().split(':')
        fin_recv = message[1][4]
    completed = False
    logging.info('CONNECTION TERMINATED')
    return True


def UDP_RDT():
    start = time.time()
    success = connection_establishment()
    if success:
        print('Connection Established Successfully')
        main_thread()
        close_connection()
        print('Connection Closed Successfully')
        sock.close()
        file.close()
    else:
        print('Connection Establishment Failed')
    end = time.time()
    print(f'TIME ELAPSED : {end-start}')
    logging.info(f'TIME ELAPSED : {end-start}')
    logging.info(f'TOTAL RESENT PACKETS FOR TIMEOUT : {total_timeout_packets}')
    logging.info(
        f'TOTAL RESENT PACKETS FOR FAST RETRANSMIT : {total_fast_retransmit}')


UDP_RDT()
