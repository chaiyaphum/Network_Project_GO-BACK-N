import socket
from random import randint

TCP_IP = ''
TCP_PORT = 3000
BUFFER_SIZE = 1024
segmentSend = ""
segmentReceive = ""
#######################################
#Flag formate
startFlag = "000010"
startAckFlag = "010010"
ackFlag = "010000"
seqFlag = "001000"
finFlag = "000001"
finAckFlag = "010001"

## Check packet error
confirm_RecvAck = 0

#packet number
sequenceSend = 0
ackSend = 0
sequenceReceived = 0
ackReceived = 0

Rn = 40
message = ""

def CreatSegment(seq,ack,flag,data) :
	# seq7 # ack7 # flag6 # data20 #
	seqHeader = str(seq).zfill(7)
	ackHeader = str(ack).zfill(7)
	header = seqHeader + ackHeader + flag
	return header + data

def PrintServerSendInfo(sendData,data,sendSeq,ackClientRequest,sendFlag) :
    print("\nServer Send")
    print("Send packet : ", sendData)
    print("data  : ", data)
    print("Seq=%s || Ack=%s || Flag=%s" %(sendSeq,ackClientRequest,sendFlag))
    print("============================================================\n")

def PrintServerRecivedInfo(receivedData,data,recvSeq,recvAck,recvFlag) :
    print("\nServer Received")
    print("Received packet : ", receivedData)
    print("data  : ", data)
    print("Seq=%s || Ack=%s || Flag=%s" %(recvSeq,recvAck,recvFlag))

def CheckFlag(flagIn) :
	if(flagIn == "000010") :
		return "startFlag"
	if(flagIn == "010010") :
		return "startAckFlag"
	if(flagIn == "010000") :
		return "ackFlag"
	if(flagIn == "001000") :
		return "seqFlag"
	if(flagIn == "000001") :
		return "finFlag"
	if(flagIn == "010001") :
		return "finAckFlag"

# Input Server ip address
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(7)

conn, addr = s.accept()

while 1 :

	segmentReceive = (conn.recv(BUFFER_SIZE)).decode('utf-8')
	if not segmentReceive: break

	# split header and data -> packet formate: |seq7|ack7|flag6|data20|
	recvSeq = int(segmentReceive[0:7])
	recvAck = int(segmentReceive[7:14])
	recvFlag = segmentReceive[14:20]
	recvData = segmentReceive[20:]
	
################## 3 way handshaking ##################
	if(CheckFlag(recvFlag) == "startFlag") :
		print("\n#################### 3 way handshaking ####################\n")
		PrintServerRecivedInfo(segmentReceive,recvData,recvSeq,recvAck,recvFlag)

		ackSend = ackSend + len(segmentReceive)
		segmentSend = CreatSegment(sequenceSend,ackSend,startAckFlag,"")
		PrintServerSendInfo(segmentSend,"",sequenceSend,ackSend,startAckFlag)
		conn.send(bytes(segmentSend, 'utf-8'))
		continue

	if(CheckFlag(recvFlag) == "ackFlag" and recvSeq == 20) :
		PrintServerRecivedInfo(segmentReceive,recvData,recvSeq,recvAck,recvFlag)
		Rn = recvSeq + len(segmentReceive)
		ackSend = ackSend + len(segmentReceive)
		print("\n################### Start send data ###################\n")
		continue
################## 3 way handshaking ##################

################## Close commection ###################
	if(CheckFlag(recvFlag) == "finFlag") :
		print("\n#################### FIN ####################\n")
		PrintServerRecivedInfo(segmentReceive,recvData,recvSeq,recvAck,recvFlag)

		sequenceSend = recvAck
		ackSend = sequenceSend + len(segmentReceive)
		segmentSend = CreatSegment(sequenceSend,ackSend,finAckFlag,"")
		PrintServerSendInfo(segmentSend,"",sequenceSend,ackSend,finAckFlag)
		conn.send(bytes(segmentSend, 'utf-8'))
		continue

	if(CheckFlag(recvFlag) == "ackFlag") :
		PrintServerRecivedInfo(segmentReceive,recvData,recvSeq,recvAck,recvFlag)
		print("\n####################  CONNECTION FINISF  ####################\n")
		print("Message receive is :")
		print(message)
		break
################## Close commection ###################

	# Random drop packet 20%
	randDropPacket = randint(0,4)
	if(randDropPacket == 0) :
		print("-------------------- DROP --------------------> packet : %s" %recvSeq)
		continue

	#print("%s %s" %(Rn,recvSeq))
	
	if(Rn == recvSeq) :
		PrintServerRecivedInfo(segmentReceive,recvData,recvSeq,recvAck,recvFlag)
		Rn = Rn + len(segmentReceive)
		sequenceSend = recvAck
		sequenceReceived = recvSeq
		ackReceived = recvAck
		confirm_RecvAck = Rn

		message = message + recvData
				
		segmentSend = CreatSegment(sequenceSend,confirm_RecvAck,ackFlag,"")
		PrintServerSendInfo(segmentSend,"",sequenceSend,confirm_RecvAck,ackFlag)
		conn.send(bytes(segmentSend, 'utf-8'))

	else :
		PrintServerRecivedInfo(segmentReceive,recvData,recvSeq,recvAck,recvFlag)
		sequenceSend = recvAck
		print("**Send old ACK :",confirm_RecvAck)		
		segmentSend = CreatSegment(sequenceSend,confirm_RecvAck,ackFlag,"")
		PrintServerSendInfo(segmentSend,"",sequenceSend,confirm_RecvAck,ackFlag)
		conn.send(bytes(segmentSend, 'utf-8'))

conn.close()