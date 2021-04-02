# RDT for FTP over UDP

* Reliable Data Transfer for transferring files using UDP *

---

## Implementation Details

<iframe src="https://docs.google.com/document/d/e/2PACX-1vRJwBkgGhxVnR_eEtAnW5xpwk0rC6lU0XiF1i4doNmFAcJ2CeukTvzcIw2M9t9i3fbZdKnMmJRZm5rI/pub?embedded=true"></iframe>

# Instructions for use

## Sender 

The sender takes in the following arguments

- recvr_addr : the address of the receiver (default : 10.0.10.2), can use -r in the command line instead
- recvr_port : port number of the receiver (default : 8080)
- sendr_addr : the address of the sender   (default : 10.0.10.1), can use -s in the command line instead
- sendr_port : port number of the sender   (default : 9090)
- input      : name of the file to be sent over the connection

Sample Usage 

```
python3 sender.py -r 10.0.0.254 -s 10.0.0.253 --input 'test-1MB'
```

## Receiver 

The receiver takes in only one argument 

- output : name of the file in which the received contents are stored

Sample Usage

```
python3 receiver.py -o 'outfile'
```

### NOTE : receiver should be up and running before the sender code is executed
