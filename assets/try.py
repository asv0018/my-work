# Try
from tkinter import *
from tkinter.ttk import Progressbar
from PIL import ImageTk, Image
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


#############################################################

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
    progress['value'] = 34
    # return(cardUidNumber,cardIdNumber)
    return (cardIdNumber)

    # print(cardNumber)


#############################################################

def readTemperature():
    # returns Temperature read
    print("temp read")
    receivedData = fSerialCom(b"@TEMP:GET=START# ")
    print(receivedData[20: 24])

    temp = receivedData[10: 14]
    progress['value'] = 70
    return (temp)


def captureImage():
    print("taking photo")
    receivedData = fSerialCom(b"@DIST:GET=START#")
    print(receivedData)
    if receivedData[11] == '#':
        distance = int(receivedData[10])
    else:
        distance = int(receivedData[10: 12])

    print(distance)
    if distance <= 40 or distance > 60:
        print("maintain a proper distance for photo capturing")
        # fSerialCom(b"@LED:SET=R# ")

    fSerialCom(b"@LED:SET=W# ")
    time.sleep(1)

    # returns captured image
    # read the absolute path
    script_dir = os.path.dirname("Desktop/Images")
    # call the .sh to capture the image
    os.system('fswebcam -r 352x288 --no-banner ' + rfid + '.jpg')
    # get the date and time, set the date and time as a filename.
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    # create the real path
    rel_path = "/home/pi/Desktop/currentImage.jpg"
    #  join the absolute path and created file name
    abs_file_path = os.path.join(script_dir, rel_path)
    # print (abs_file_path)
    progress['value'] = 50
    global StatusReading
    StatusReading = ("image captured")
    return (rfid + ".jpg")


def faceMaskDetection():
    # returns boolean value, 0 if mask not found and 1 if mask found
    return (1)


def faceRecognition():
    # returns boolean value, 1 if face detected or 0 if face not found
    return (1)


def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


def sendData():
    # sends Temperature reading and Image to the data base based on rfid
    import socket

    # Create a socket object
    s = socket.socket()

    # Define the port on which you want to connect
    port = 4444

    # connect to the server on local computer
    s.connect(('172.22.3.104', port))
    if (len(rfid) == 9):
        id = 1  # rfid is Employee ID
    else:
        id = 0  # rfid is Student

    # punch = 0 means first punch, punc = 1 means second punch
    # need to create a file to store rfid and identify whether he/she punched for first time or second time
    punch = 0

    if punch == 0:
        data = str(punch) + '|' + str(
            id) + '|' + uid + '|' + rfid + '|' + temperature + '|' + currentDate + '|' + currentTime + '|' + str(
            faceMaskDetection())
    else:
        data = str(punch) + '|' + str(id) + '|' + uid + '|' + rfid + '|' + currentDate + '|' + currentTime

    print(data)
    d = bytes(data, "utf-8")
    s.send(d)
    s.send(bytes(get_base64_encoded_image(rfid + ".jpg"), "utf-8"))

    # receive data from the server \
    buff = s.recv(1024)
    # check for authentication
    # buff = INVALID then user is not authenticated, buff = name if user is authenticated
    if (str(buff) == 'INVALID'):
        print("Unauthorized User")
    else:
        print('Name:' + str(buff))

        # if (buff):
    # image = c.recv(10000000000000)
    # fp = open("/home/pi/Desktop/Recieved_image.jpg","wb")
    # fp.write(image.decode('base64'))
    # fp.close()
    print(buff)
    # close the connection
    s.close()
    return (1)


def validate():
    if (int(readTemperature()) < 98 and faceMaskDetection() == 1):
        return (1)
    else:
        return (0)


# '''


# GUI Code
# creating basic window
window = Tk()
window.geometry("800x450")  # size of the window width:- 500, height:- 375
window.configure(bg='gray')
m = window.maxsize()
# window.geometry('{}x{}+0+0'.format(*m))
# window.resizable(0, 0) # this prevents from resizing the window

window.title("REVA University Thermal Scanning System")

progress = Progressbar(window, orient=HORIZONTAL, mode='determinate')
progress.pack(side='bottom', fill='x')
# progress.start()

# REVAIDReading=readRFID()
# TemperatureReading= readTemperature()
REVAIDReading = "r18mdn06"
TemperatureReading = "36.6"
DateReading = currentDate
TimeReading = currentTime
# StatusReading=StringVar()


'''logoFrame = Frame(window, width = 100,  bg='gray', bd = 0,highlightbackground = "black", highlightcolor = "black", highlightthickness = 1)
logoFrame.pack(side = TOP)

canvas = Canvas(logoFrame)  
img1 = ImageTk.PhotoImage(Image.open("REVALOGO.jpg"))  
canvas.create_image(10,10,anchor=NW, image=img1) 
canvas.pack()'''

load = (Image.open("/home/pi/Desktop/revaLogo.png")).resize((220, 50), Image.ANTIALIAS)
render = ImageTk.PhotoImage(load)
img = Label(window, image=render)
img.image = render
img.pack(side=TOP)

photoFrame = Frame(window, width=200, height=100, bg='gray', bd=0, highlightbackground="black", highlightcolor="black",
                   highlightthickness=1)
photoFrame.pack(side=TOP)

# creating an input field inside the 'Frame'
canvas1 = Canvas(photoFrame, width=220, height=200)
img2 = ImageTk.PhotoImage(Image.open(captureImage()))
canvas1.create_image(30, 30, anchor=NW, image=img2)
canvas1.pack()

detailsFrame = Frame(window, width=200, height=100, bg='gray', bd=0, highlightbackground="black",
                     highlightcolor="black", highlightthickness=1)
detailsFrame.pack(side=TOP)

REVAID = Label(detailsFrame, text="REVA_ID", bg="gray", relief='raised', justify='left', font=("Times New Roman", 14),
               width='12', padx=1, pady=1)
REVAID.config(anchor=W, justify=LEFT)
REVAID.grid(row=1, column=1)

RevaIDValue = Label(detailsFrame, text=REVAIDReading, bg="gray", relief='raised', width='12',
                    font=("Times New Roman", 14), padx=1, pady=1)
RevaIDValue.config(anchor=W, justify=LEFT)
RevaIDValue.grid(row=1, column=2)

Temperature = Label(detailsFrame, text="TEMP", bg="gray", relief='raised', width='12', font=("Times New Roman", 14),
                    padx=1, pady=1)
Temperature.config(anchor=W, justify=LEFT)
Temperature.grid(row=2, column=1)
TempValue = Label(detailsFrame, text=TemperatureReading, bg="gray", relief='raised', width='12',
                  font=("Times New Roman", 14), padx=1, pady=1)
TempValue.config(anchor=W, justify=LEFT)
TempValue.grid(row=2, column=2)

curDate = Label(detailsFrame, text="Date", bg="gray", relief='raised', width='12', font=("Times New Roman", 14), padx=1,
                pady=1)
curDate.config(anchor=W, justify=LEFT)
curDate.grid(row=3, column=1)

DateValue = Label(detailsFrame, text=DateReading, bg="gray", relief='raised', width='12', font=("Times New Roman", 14),
                  padx=1, pady=1)
DateValue.config(anchor=W, justify=LEFT)
DateValue.grid(row=3, column=2)

curTime = Label(detailsFrame, text="Time", bg="gray", relief='raised', width='12', font=("Times New Roman", 14), padx=1,
                pady=1)
curTime.config(anchor=W, justify=LEFT)
curTime.grid(row=4, column=1)
TimeValue = Label(detailsFrame, text=TimeReading, bg="gray", relief='raised', width='12', font=("Times New Roman", 14),
                  padx=1, pady=1)
TimeValue.config(anchor=W, justify=LEFT)
TimeValue.grid(row=4, column=2)

# progress['value'] = 20
# window.update_idletasks()
# time.sleep(1)
# Button(window, text = 'Start', command = bar).pack(pady = 10)
statusLabel = Label(window, text=StatusReading, bg="gray", width='25', font=("Times New Roman", 14), padx=1, pady=1)
statusLabel.pack(side=BOTTOM)
window.mainloop()

