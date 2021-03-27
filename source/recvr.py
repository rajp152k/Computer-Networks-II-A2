from utils import *

parser = argparse.ArgumentParser()

parser.add_argument('--recvr_IP',dest='R_IP',default='127.0.0.1',type=str)
parser.add_argument('--recvr_port',dest='R_P',default=9898,type=int)
parser.add_argument('--recv_dest',dest='r_f',default='./recv/test.txt',type=str)

def recv(args):
    sock = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)
    sock.bind((args.R_IP,args.R_P))

    print('sock alive and listening for connections')

    ################
    # connection establishment logic:
    #    accept first packet with certain semantics and accept future packets from that addr
    #    UDP is connectionless so will have to implement the connection tunnel ourselves
    ################
    
    # connection established
    while 1:
        try:
            # start receiving data packets from authenticated address    
            time.sleep(1)
            print('UDP sock alive and in receiving state')


            # check if all data has been received and break
        except KeyboardInterrupt:
            print('exiting without complete transfer')
            # all other necessary cleanups need to be done here
            break;

    ###############

    sock.close()

if __name__ =='__main__':
    args = parser.parse_args()
    recv(args)
