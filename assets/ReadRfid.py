import threading

import time

import os
import datetime
import sys
import time
import subprocess
import serial
import base64

receivedData = ""
rfid = ""
uid = ""
temperature = " "
StatusReading = " "

currentDate = datetime.datetime.now().strftime("%Y-%m-%d")
currentTime = datetime.datetime.now().strftime("%H:%M:%S")

def fSerialCom(sendCommand):
    serialInput = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    serialInput.flush()
    stopLooping = 0

    while stopLooping == 0:
        if sendCommand != "waitForSignal":
            serialInput.write(sendCommand)

        # while startBit
        serialData = serialInput.readline().decode('utf-8').rstrip()
        print(serialData)
        for charIndex in serialData:
            if charIndex == "#":
                # print("yes")
                stopLooping = 1
                return serialData


#############################################################
def readRFID():
    # returns RFID
    print("reading RFID details")

    receivedData = fSerialCom(b"@RFID:START#")
    print(receivedData)
    cardUidNumber = receivedData[10: 18]
    print("check here")
    print(receivedData[30])
    if receivedData[30] == '\0':
        print("student srn")
        cardIdNumber = receivedData[22: 30]
    else:
        print("employee ID")
        cardIdNumber = receivedData[22: 31]

    print(cardUidNumber)
    print(cardIdNumber)
    #progress['value'] = 34
    # return(cardUidNumber,cardIdNumber)
    return (cardIdNumber)

def ControlData():
    while(True):
        data = readRFID()