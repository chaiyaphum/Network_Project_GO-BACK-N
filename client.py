import sys
import socket
import threading;
import time

TCP_IP = ''
TCP_PORT = 3000
BUFFER_SIZE = 1024
seqMessage = []
WINDOW_SIZE = 5
segmentSend = ""
segmentReceive = ""
s = ""
#####################################
#Flag formate
startFlag = "000010"
ackFlag = "010000"
seqFlag = "001000"
finFlag = "000001"
finAckFlag = "010001"

# Timeout check
TIMEOUT = 2
temp_recentAck = 0
timmerThread = 0

#Packet number
sequenceSend = 0
ackSend = 0
sequenceReceived = 0
ackReceived = 0

# Check packet error
recentAck = 40
countFalseAck = 0

#Data index
index = 0
Sb = 0
Sm = WINDOW_SIZE - 1;

# Report
packetCount_send = 0
packetCountOK_send = 0

def CreateSeqMessage(fileName) :
	ref = 0;
	f = open (fileName,"r")
	data = f.read()
	while (ref <= len(data)) :
		restMsg = data[ref:]
		if(len(restMsg)>20) :
			subMsg = restMsg[0:20]
		else :
			subMsg = restMsg

		seqMessage.append(subMsg) 
		ref = ref+20
	seqMessage.append('a') 
	f.close()

def PrintClientSendInfo(sendData,data,sendSeq,ackServerRequest,sendFlag) :
	global packetCount_send
	packetCount_send = packetCount_send + 1
	print("\nClientr Send #", packetCount_send)
	print("Send packet : ", sendData)
	print("data  : ", data)
	print("Seq=%s || Ack=%s || Flag=%s\n" %(sendSeq,ackServerRequest,sendFlag))
	
def PrintClientRecivedInfo(receivedData,data,recvSeq,recvAck,recvFlag) :
	print("Client Received")
	print("Received packet : ", receivedData)
	print("data  : ", data)
	print("Seq=%s || Ack=%s || Flag=%s" %(recvSeq,recvAck,recvFlag))
	print("=============================================================\n")

def CreatSegment(seq,ack,flag,data) :
	# seq7 # ack7 # flag6 # data20 #
	seqHeader = str(seq).zfill(7)
	ackHeader = str(ack).zfill(7)
	header = seqHeader + ackHeader + flag
	return header + data

def CheckFlag(flagIn) :
	if(flagIn == "000010") :
		return "startFlag"
	if(flagIn == "010010") :
		return "startAckFlag"
	if(flagIn == "010000") :
		return "ackFlag"
	if(flagIn == "001000") :
		return "seqFlag"
	if(flagIn == "001000") :
		return "finFlag"
	if(flagIn == "010001") :
		return "finAckFlag"

def Timer() :
	global timmerThread, temp_recentAck
	timmerThread = threading.Timer(TIMEOUT, Timer)
	timmerThread.start();

	if(temp_recentAck == recentAck) :
		print("*************************** Timeout ***************************")
		SetReTransmit(recentAck,Sb)
		
	temp_recentAck = recentAck


def SetReTransmit(recentAckF,SbF) :
	global sequenceSend,index,countFalseAck
	print("\n================================ Re send ================================\n")
	sequenceSend = recentAckF
	index = SbF
	countFalseAck = 0

def ConnectionFinish() :
	global sequenceSend, ackSend, temp_recentAck, packetCount_send
	temp_recentAck = -1
	ackSend = ackSend + 20
	print("\n################### FIN ###################\n")
	segmentSend = CreatSegment(sequenceSend,ackSend,finFlag,"")
	PrintClientSendInfo(segmentSend,"",sequenceSend,ackSend,finFlag)
	s.send(bytes(segmentSend, 'utf-8'))

	segmentReceive = s.recv(BUFFER_SIZE).decode('utf-8')
	recvSeq = int(segmentReceive[0:7])
	recvAck = int(segmentReceive[7:14])
	recvFlag = segmentReceive[14:20]
	
	if(CheckFlag(recvFlag) == "finAckFlag") :
		PrintClientRecivedInfo(segmentReceive,"",recvSeq,recvAck,recvFlag)
		ackSend = recvSeq + 20
		sequenceSend = recvAck
		
		segmentSend = CreatSegment(sequenceSend,ackSend,ackFlag,"")
		PrintClientSendInfo(segmentSend,"",sequenceSend,ackSend,ackFlag)
		s.send(bytes(segmentSend, 'utf-8'))

	# Show report
	packetCount_send = (packetCount_send - 4)*40
	packetCountOK_send = len(seqMessage)*40
	utilization = float(packetCountOK_send)/float(packetCount_send)

	print("Send all packet = %s Bytes" %packetCount_send)
	print("Send all packet = %s Bytes" %packetCountOK_send)
	print("Utilization = %.2f" %utilization)

	timmerThread.cancel()
	sys.exit("\n\n############## CONNECTION FINISF ##############")


#////////////////////// Main function \\\\\\\\\\\\\\\\\\\\\\\\\\\\\

CreateSeqMessage("t.txt");

TCP_IP = input("Input Server ip address : ")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
s.connect((TCP_IP, TCP_PORT))
print("Connected: server address is :", TCP_IP)

################## 3 way handshaking ##################

# Send first packet for 3 way handshaking
print("\n#################### 3 way handshaking ####################\n")

segmentSend = CreatSegment(sequenceSend,"0",startFlag,"")
PrintClientSendInfo(segmentSend,"",sequenceSend,"0",startFlag)
s.send(bytes(segmentSend, 'utf-8'))

segmentReceive = s.recv(BUFFER_SIZE).decode('utf-8')

# split header and data -> packet formate: |seq7|ack7|flag6|data20|
recvSeq = int(segmentReceive[0:7])
recvAck = int(segmentReceive[7:14])
recvFlag = segmentReceive[14:20]
recvData = segmentReceive[20:]
PrintClientRecivedInfo(segmentReceive,recvData,recvSeq,recvAck,recvFlag)

if(CheckFlag(recvFlag) == "startAckFlag") :
	sequenceSend = recvAck
	sequenceReceived = recvSeq
	ackSend = recvSeq + len(segmentReceive)
	ackReceived = recvAck

	segmentSend = CreatSegment(sequenceSend,ackSend,ackFlag,"")
	PrintClientSendInfo(segmentSend,"",sequenceSend,ackSend,ackFlag)
	s.send(bytes(segmentSend, 'utf-8'))
print("\n#################### Start send data ####################\n")

sequenceSend = sequenceSend + len(segmentSend)

Timer();
############################### Start go-back-n process ###############################

while 1:

	while(Sb <= index and index <= Sm) :
		if(countFalseAck >= 3) :
			print("*************************** 3 Duplicate ACK ***************************")
			SetReTransmit(recentAck,Sb)

		ackSend = recvSeq + len(segmentReceive)

		segmentSend = CreatSegment(sequenceSend,ackSend,seqFlag,seqMessage[index])
		PrintClientSendInfo(segmentSend,seqMessage[index],sequenceSend,ackSend,seqFlag)
		s.send(bytes(segmentSend, 'utf-8'))
		
		sequenceSend = sequenceSend + len(segmentSend)

		try :
			segmentReceive = s.recv(BUFFER_SIZE).decode('utf-8')
			recvSeq = int(segmentReceive[0:7])
			recvAck = int(segmentReceive[7:14])
			recvFlag = segmentReceive[14:20]
			recvData = segmentReceive[20:]

			PrintClientRecivedInfo(segmentReceive,recvData,recvSeq,recvAck,recvFlag)

			if( recvAck >= (len(seqMessage)*40)) :
				ConnectionFinish()
				break
			
			index = index + 1

			if((recentAck+40) == recvAck) :
				recentAck = recentAck + 40
				Sb = Sb + 1
				if((Sb + WINDOW_SIZE) >= len(seqMessage)) :
					Sm = len(seqMessage)-1
				else :
					Sm = Sb+(WINDOW_SIZE-1)

			else :
				countFalseAck  = countFalseAck + 1

		except socket.timeout :
			index = index + 1
			continue

		if(index >= (len(seqMessage)-1) and recentAck <= (len(seqMessage))*40) :
			index = Sb

	index = Sb

s.close()
ConnectionFinish()