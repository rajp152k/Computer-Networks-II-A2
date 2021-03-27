from utils import *

parser = argparse.ArgumentParser()

parser.add_argument('--sendr_IP',dest='S_IP',default='127.0.0.1',type=str)
parser.add_argument('--sendr_port',dest='S_P',default=8989,type=str)
parser.add_argument('--recvr_IP',dest='R_IP',default='127.0.0.1',type=str)
parser.add_argument('--recvr_port',dest='R_P',default=9898,type=int)
parser.add_argument('--file',dest='s_f',default='./send/test.txt',type=str)


def send(args):
    print(f'sending \n  {Path(args.s_f).resolve()} \nto {args.R_IP}:{args.R_P}')
    sock = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)
    sock.bind((args.S_IP,args.S_P))
    
    print('sock alive and ready to establish connection')

    ################
    # connection establishment logic:
    #    send first packet with certain semantics to the recvr
    #    UDP is connectionless so will have to implement the connection tunnel ourselves
    ################

    while 1:    
        try:
            time.sleep(1)
            print('UDP sock alive and sending data')


            # communication with ack'er thread in here



        except KeyboardInterrupt:
            print('exiting without complete transfer')
            # all other necessary cleanups need to be done here
            break

    sock.close()

if __name__ == '__main__':
    args = parser.parse_args()
    send(args)
