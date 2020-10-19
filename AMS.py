#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
#   Developer: Rushil Choksi
#   Email: rushil.rc@gmail.com
#

import os
import sys
import cv2
import csv
import time
import smtplib
import hashlib
import datetime
import mimetypes
import numpy as np
import pandas as pd
from email import encoders
from PIL import Image,ImageTk
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.message import EmailMessage
from tkinter.filedialog import askopenfilename
from email.mime.multipart import MIMEMultipart

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

import login_support

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = tk.Tk()
    logScreen = loginScreen (root)
    #login_support.init(root, top)
    root.mainloop()

w = None
def create_loginScreen(rt, *args, **kwargs):
    '''Starting point when module is imported by another module.
       Correct form of call: 'create_loginScreen(root, *args, **kwargs)' .'''
    global w, w_win, root
    #rt = root
    root = rt
    w = tk.Toplevel (root)
    logScreen = loginScreen (w)
    #login_support.init(w, top, *args, **kwargs)
    return (w, top)

def destroy_loginScreen():
    global w
    w.destroy()
    w = None

class loginScreen:
    def __init__(self, logScreen=None):
        '''This class configures and populates the toplevel window.
           logScreen is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'

        def logUser():
            Username = self.loginPanelUsername.get()
            Password = self.loginPanelPassword.get()
            if Username == "":
                self.loginPanelNotification.configure(background="#800000")
                self.loginPanelNotification.configure(foreground="#FFFFFF")
                self.loginPanelNotification.configure(text='''Please enter Username''')
            elif Password == "":
                self.loginPanelNotification.configure(background="#800000")
                self.loginPanelNotification.configure(foreground="#FFFFFF")
                self.loginPanelNotification.configure(text='''Please enter Password''')
            else:
                self.loginPanelUsername.delete(0, 30)
                self.loginPanelPassword.delete(0, 30)
                PasswordEncrypted = (hashlib.sha512(Password.encode())).hexdigest()
                print (PasswordEncrypted)
                ListofFiles = os.listdir('C:/Users/Rushil/OneDrive/Desktop/Attendance Management System/Login/') #Enter the file directory where you registered
                if Username in ListofFiles:
                    file1 = open(Username, "r")
                    Verify = file1.read().splitlines()
                    if PasswordEncrypted in Verify:
                        self.loginPanelNotification.configure(background="#008000")
                        self.loginPanelNotification.configure(foreground="#FFFFFF")
                        self.loginPanelNotification.configure(text='''Login Successful''')
                        logScreen.destroy()
                        def deleteID():
                            self.studentID.delete(first=0, last=30)

                        def deleteName():
                            self.studentName.delete(first=0, last=30)

                        def testVal(inStr, acttyp):
                            if acttyp == '1':
                                if not inStr.isdigit():
                                    return False
                            return True

                        def takeImage():
                            entryOne = self.studentID.get()
                            entryTwo = self.studentName.get()
                            if entryOne == "":
                                self.Notification.configure(background="#800000")
                                self.Notification.configure(foreground="#FFFFFF")
                                self.Notification.configure(text="Please enter ID!")
                            elif entryTwo == "":
                                self.Notification.configure(background="#800000")
                                self.Notification.configure(foreground="#FFFFFF")
                                self.Notification.configure(text="Please enter Name!")
                            else:
                                try:
                                    cam = cv2.VideoCapture(0)
                                    detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
                                    ID = self.studentID.get()
                                    Name = self.studentName.get()
                                    sampleNum = 0
                                    while (True):
                                        ret, img = cam.read()
                                        gray = cv2.cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                                        faces = detector.detectMultiScale(gray, 1.3, 5)
                                        for (x, y, w, h) in faces:
                                            cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,255), 5)
                                            sampleNum += 1
                                            cv2.imwrite("TrainingImage/ " + Name + "." + ID + "." + str(sampleNum) + ".png", gray[y:y + h, x:x + w])
                                            cv2.imshow("Taking images for student " + self.studentName.get(), img)
                                        if 0xFF == ord('Q') & cv2.waitKey(1):
                                            break
                                        elif sampleNum >= 150:
                                            break
                                    cam.release()
                                    cv2.destroyAllWindows()
                                    ts = time.time()
                                    ######################Check for errors below######################
                                    print(ID)
                                    print(Name)
                                    Date = datetime.datetime.fromtimestamp(ts).strftime("%d/%m/%Y")
                                    Time = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                                    row = [ID, Name, Date, Time]
                                    with open("StudentDetails.csv", "a+") as csvFile:
                                        writer = csv.writer(csvFile, delimiter=',')
                                        writer.writerow(row)
                                        csvFile.close()
                                    res = "Images Saved for ID : " + ID + " Name : " + Name
                                    self.Notification.configure(text=res, bg="#008000", width=64, font=('SF Pro Display', 16, 'bold'))
                                    self.Notification.place(x=92, y=430)
                                except FileExistsError as F:
                                    f = 'Student Data already exists'
                                    self.Notification.configure(text=f, bg="Red", width=64)
                                    self.Notification.place(x=92, y=430)

                        def trainImage():
                            recognizer = cv2.face.LBPHFaceRecognizer_create()
                            global detector
                            detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
                            global faces,Id
                            os.chdir("C:/Users/Rushil/OneDrive/Desktop/Attendance Management System")
                            faces, Id = getImagesAndLabels("TrainingImage")
                            '''except Exception as e:
                                l='please make "TrainingImage" folder & put Images'
                                self.Notification.configure(text=l, bg="#008000", width=64, font=('SF Pro Display', 16, 'bold'))
                                self.Notification.place(x=92, y=430)'''
                            recognizer.train(faces, np.array(Id))
                            recognizer.write('TrainingImageLabel/Trainer.yml')
                            self.Notification.configure(text="Encrypting student's images", bg="#008000", width=64, font=('SF Pro Display', 16, 'bold'))
                            '''os.chdir("C:/Users/Rushil/OneDrive/Desktop/Attendance Management System/TrainingImage")
                            for file in os.listdir():
                                try:
                                    if file == "zencrypt_all.py":
                                        print("Done")
                                        print(time.process_time() - start)
                                    else:
                                        im = Image.open(file)
                                        im = im.convert('L')
                                        arr = np.fromiter(iter(im.getdata()), np.uint8)
                                        arr.resize(im.height, im.width)
                                        arr ^= 0xFF
                                        invertedIM = Image.fromarray(arr, mode='L')
                                        file = open(file,"w")
                                        array = np.asarray(im)
                                        result = (hashlib.sha512(str(im).encode())).hexdigest()
                                        file.write(result)
                                        file.close()
                                except Exception as e:
                                    continue
                            os.chdir("C:/Users/Rushil/OneDrive/Desktop/Attendance Management System")
                            except Exception as e:
                                q = 'An error was encountered.'#Please make a folder named "TrainingImageLabel"'
                                self.Notification.configure(text=q, bg="#008000", width=64, font=('SF Pro Display', 16, 'bold'))
                                self.Notification.place(x=92, y=430)'''
                            res = "Student has been trained by the software."
                            self.Notification.configure(text=res, bg="#008000", width=64, font=('SF Pro Display', 16, 'bold'))
                            self.Notification.place(x=92, y=430)

                        def getImagesAndLabels(path):
                            imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
                            faceSamples = []
                            ids = []
                            for imagePath in imagePaths:
                                PIL_img = Image.open(imagePath).convert('L')
                                img_numpy = np.array(PIL_img, 'uint8')
                                id = int(os.path.split(imagePath)[-1].split(".")[1])
                                faces = detector.detectMultiScale(img_numpy)
                                for (x, y, w, h) in faces:
                                    faceSamples.append(img_numpy[y:y + h, x:x + w])
                                    ids.append(id)
                            return faceSamples, ids
                        
                        def autoAttendance():
                            def fillAttendance():
                                SubjectEntry = self.subjectEntry.get()
                                now = time.time()
                                future = now + 25
                                if time.time() < future:
                                    if SubjectEntry == "":
                                        self.welcomeMessageAuto.configure(background="#800000")
                                        self.welcomeMessageAuto.configure(foreground="#FFFFFF")
                                        self.welcomeMessageAuto.configure(text="Please enter subject!")
                                    else:
                                        recognizer = cv2.face.LBPHFaceRecognizer_create()
                                        try:
                                            recognizer.read("TrainingImageLabel\Trainer.yml")
                                        except:
                                            self.welcomeMessageAuto.configure(text='Please make a folder names "TrainingImage"')
                                        harcascadePath = "haarcascade_frontalface_default.xml"
                                        faceCascade = cv2.CascadeClassifier(harcascadePath)
                                        df = pd.read_csv("StudentDetails.csv")
                                        cam = cv2.VideoCapture(0)
                                        font = cv2.FONT_HERSHEY_SIMPLEX
                                        colNames = ['ID','Date','Time']
                                        attendance = pd.DataFrame(columns = colNames)
                                        while True:
                                            ret, im = cam.read()
                                            gray = cv2.cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                                            faces = faceCascade.detectMultiScale(gray, 1.3, 5)
                                            for (x, y, w, h) in faces:
                                                global Id
                                                Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
                                                if conf <= 100:
                                                    global Subject, aa, date, timeStamp
                                                    Subject = self.subjectEntry.get()
                                                    ts = time.time()
                                                    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                                                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                                                    aa = df.loc[df['ID'] == Id]['Name'].values
                                                    tt = "ID: " + str(Id) + " %.2f" % conf
                                                    attendance.loc[len(attendance)] = [Id, date, timeStamp]
                                                    cv2.rectangle(im, (x,y), (x + w, y + h), (250, 250, 250), 7)
                                                    cv2.putText(im, (tt), (x, y-50), font, 1, (255, 255, 0,), 4)
                                                else:
                                                    ID = "Unknown"
                                                    cv2.rectangle(im, (x, y), (x + w, y + h), (0, 25, 255), 7)
                                                    cv2.putText(im, str(ID), (x + h, y), font, 1, (0, 25, 255), 4)
                                            if time.time() > future:
                                                break
                                            attendance = attendance.drop_duplicates(['ID'], keep = 'first')
                                            cv2.imshow("Filling attedance ...", im)
                                            key = cv2.waitKey(30) &0xFF
                                            if key == 27:
                                                break
                                        ts = time.time()
                                        date = datetime.datetime.fromtimestamp(ts).strftime("%d_%m_%Y")
                                        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                                        Hour, Minute, Second = timeStamp.split(":")
                                        fileName = "Attendance/" + self.subjectEntry.get() + "_" + date + "_Time_" + Hour + "_" + Second + ".csv"
                                        attendance = attendance.drop_duplicates(['ID'], keep = "first")
                                        print (attendance)
                                        ######################Check for errors below######################
                                        attendance.to_csv(fileName, index = False)
                                        dateForDB = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
                                        dbTableName = str(SubjectEntry + "_" + dateForDB + "_Time_" + Hour + "_" + Minute + "_" + Second)
                                        import mysql.connector
                                        try:
                                            connection = mysql.connector.connect(host='localhost', user='root', password='root', database='ams')
                                            cursor = connection.cursor()
                                        except Exception as e:
                                            print (e)
                                        sql = "CREATE TABLE " + dbTableName + """(SrNo INT NOT NULL AUTO_INCREMENT, ID varchar(100) NOT NULL, Name VARCHAR(255) NOT NULL, Date VARCHAR(20) NOT NULL, Time VARCHAR(20) NOT NULL, PRIMARY KEY (SrNo)); """
                                        insertData = "INSERT INTO " + dbTableName + " (SrNo, ID, Name, Date, Time) VALUES (0,%s,%s,%s,%s)"
                                        try:                                            
                                            cursor.execute(sql)
                                        except Exception as ex:
                                            print("1:",ex)
                                        try:
                                            dataList = [str(Id),str(aa),str(date),str(timeStamp)]
                                            cursor.execute(insertData, dataList)
                                            connection.commit()
                                        except Exception as ex:
                                            print("2:",ex)

                                        self.welcomeMessageAuto.configure(text="Attendance filled Successfully")
                                        cam.release()
                                        cv2.destroyAllWindows()
                                        root = tk.Tk()
                                        root.title("Attendance of " + Subject)
                                        root.configure(background="#1B1B1B")
                                        root.configure(highlightbackground="#d9d9d9")
                                        root.configure(highlightcolor="black")
                                        root.iconbitmap("mainIcon.ico")
                                        root.focus_force()
                                        cs = 'C:/Users/Rushil/OneDrive/Desktop/Attendance Management System/' + fileName
                                        with open(cs, newline="") as file:
                                            reader = csv.reader(file)
                                            r = 0
                                            for col in reader:
                                                c = 0
                                                for row in col:
                                                    label = tk.Label(root, width=8, height=1, fg="black", font=('SF Pro Display', 15, ' bold '), bg="#008000", text=row)
                                                    label.grid(row=r, column=c)
                                                    c += 1
                                                r += 1
                                        root.mainloop()

                                       
                            
                            def sendMail():
                                SubjectEntry = self.subjectEntry.get()
                                user = os.environ.get("adminUser")
                                passwd = os.environ.get("adminPassword")
                                fileCSV = askopenfilename()
                                msg = MIMEMultipart()
                                msg['Subject'] = "Attendance for subject: " + str(SubjectEntry)
                                msg['From'] = user
                                msg['To'] = 'rushil.rc@gmail.com'
                                msgContent = "Hi there,\n\nPlease find attached for attendance of " + str(SubjectEntry)
                                ctype, encoding = mimetypes.guess_type(fileCSV)
                                if ctype is None or encoding is not None:
                                    ctype = "application/octet-stream"
                                Content = MIMEText(msgContent,'plain')
                                maintype, subtype = ctype.split("/", 1)
                                fp = open(fileCSV,"rb")
                                attachment = MIMEBase(maintype, subtype)
                                attachment.set_payload(fp.read())
                                encoders.encode_base64(attachment)
                                attachment.add_header("Content-Disposition", "attachment", filename=fileCSV)
                                msg.attach(attachment)
                                msg.attach(Content)
                                with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
                                    smtp.login(user,passwd)
                                    smtp.send_message(msg)
                                    self.welcomeMessageAuto.focus_force()
                                    self.welcomeMessageAuto.configure(text="Mail sent to Admin")

                            subjectScreen = tk.Tk()
                            subjectScreen.iconbitmap("mainIcon.ico")
                            subjectScreen.title("Enter Subject for Automatic Attendance")
                            subjectScreen.geometry("585x325+316+165")
                            subjectScreen.resizable(0,0)
                            subjectScreen.configure(background="#1B1B1B")
                            subjectScreen.focus_force()

                            self.welcomeMessageAuto = tk.Message(subjectScreen)
                            self.welcomeMessageAuto.place(relx=0.12, rely=0.591, relheight=0.102, relwidth=0.742)
                            self.welcomeMessageAuto.configure(background="#008000")
                            self.welcomeMessageAuto.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.welcomeMessageAuto.configure(foreground="#FFFFFF")
                            self.welcomeMessageAuto.configure(highlightbackground="#d9d9d9")
                            self.welcomeMessageAuto.configure(highlightcolor="black")
                            self.welcomeMessageAuto.configure(text='''Welcome, '''+Username)
                            self.welcomeMessageAuto.configure(width=434)

                            self.enterSubject = tk.Label(subjectScreen)
                            self.enterSubject.place(relx=0.12, rely=0.431, height=29, width=132)
                            self.enterSubject.configure(activebackground="#f9f9f9")
                            self.enterSubject.configure(activeforeground="black")
                            self.enterSubject.configure(background="#1B1B1B")
                            self.enterSubject.configure(disabledforeground="#a3a3a3")
                            self.enterSubject.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.enterSubject.configure(foreground="#FFFFFF")
                            self.enterSubject.configure(highlightbackground="#d9d9d9")
                            self.enterSubject.configure(highlightcolor="black")
                            self.enterSubject.configure(text='''Enter Subject:''')

                            self.subjectEntry = tk.Entry(subjectScreen)
                            self.subjectEntry.place(relx=0.41, rely=0.431, height=27, relwidth=0.451)
                            self.subjectEntry.configure(background="#D9D9D9")
                            self.subjectEntry.configure(disabledforeground="#a3a3a3")
                            self.subjectEntry.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.subjectEntry.configure(foreground="#000000")
                            self.subjectEntry.configure(highlightbackground="#d9d9d9")
                            self.subjectEntry.configure(highlightcolor="black")
                            self.subjectEntry.configure(insertbackground="black")
                            self.subjectEntry.configure(selectbackground="#c4c4c4")
                            self.subjectEntry.configure(selectforeground="black")

                            self.fillAttendanceBtnAuto = tk.Button(subjectScreen)
                            self.fillAttendanceBtnAuto.place(relx=0.12, rely=0.769, height=38, width=154)
                            self.fillAttendanceBtnAuto.configure(activebackground="#ececec")
                            self.fillAttendanceBtnAuto.configure(activeforeground="#000000")
                            self.fillAttendanceBtnAuto.configure(background="#2E2E2E")
                            self.fillAttendanceBtnAuto.configure(disabledforeground="#a3a3a3")
                            self.fillAttendanceBtnAuto.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.fillAttendanceBtnAuto.configure(foreground="#FFFFFF")
                            self.fillAttendanceBtnAuto.configure(highlightbackground="#d9d9d9")
                            self.fillAttendanceBtnAuto.configure(highlightcolor="black")
                            self.fillAttendanceBtnAuto.configure(pady="0")
                            self.fillAttendanceBtnAuto.configure(text='''Fill Attendance''')
                            self.fillAttendanceBtnAuto.configure(command=fillAttendance)

                            self.sendMailBtn = tk.Button(subjectScreen)
                            self.sendMailBtn.place(relx=0.610, rely=0.769, height=38, width=148)
                            self.sendMailBtn.configure(activebackground="#ececec")
                            self.sendMailBtn.configure(activeforeground="#000000")
                            self.sendMailBtn.configure(background="#2E2E2E")
                            self.sendMailBtn.configure(disabledforeground="#a3a3a3")
                            self.sendMailBtn.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.sendMailBtn.configure(foreground="#FFFFFF")
                            self.sendMailBtn.configure(highlightbackground="#d9d9d9")
                            self.sendMailBtn.configure(highlightcolor="black")
                            self.sendMailBtn.configure(text='''Send Mail''')
                            self.sendMailBtn.configure(command=sendMail)

                            self.chooseSubject = tk.Message(subjectScreen)
                            self.chooseSubject.place(relx=0.0, rely=0.062, relheight=0.194, relwidth=1.009)
                            self.chooseSubject.configure(background="#2E2E2E")
                            self.chooseSubject.configure(font="-family {SF Pro Display} -size 36 -weight bold")
                            self.chooseSubject.configure(foreground="#FFFFFF")
                            self.chooseSubject.configure(highlightbackground="#d9d9d9")
                            self.chooseSubject.configure(highlightcolor="black")
                            self.chooseSubject.configure(text='''Choose Subject''')
                            self.chooseSubject.configure(width=590)

                            subjectScreen.mainloop()

                        def manualAttendance():
                            global subName
                            subName = tk.Tk()
                            subName.iconbitmap("mainIcon.ico")
                            subName.title("Enter Subject for Manual Attendance")
                            subName.geometry("585x325+316+165")
                            subName.configure(background='#1B1B1B')
                            subName.resizable(0, 0)
                            subName.focus_force()

                            def fillAttendanceManual():
                                ts = time.time()
                                Date = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
                                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                                Time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                                Hour, Minute, Second = timeStamp.split(":")
                                dateForDB = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
                                global subEntryText
                                subEntryText = self.subjectEntry.get()
                                dbTableName = str(subEntryText + "_" + Date + "_Time_" + Hour + "_" + Minute + "_" + Second)
                                import mysql.connector
                                try:
                                    global cursor
                                    connection = mysql.connector.connect(host='localhost', user='root', password='root', database='ams')
                                    cursor = connection.cursor()
                                except Exception as e:
                                    print(e)
                                sql = "CREATE TABLE " + dbTableName + """(SrNo INT NOT NULL AUTO_INCREMENT, ID varchar(100) NOT NULL, Name VARCHAR(50) NOT NULL, Date VARCHAR(20) NOT NULL, Time VARCHAR(20) NOT NULL, PRIMARY KEY (SrNo)); """
                                try:
                                    cursor.execute(sql)
                                except Exception as e:
                                    print(e)
                                    print("Add mysql.connector")
                                if subEntryText == "":
                                    self.welcomeMessageSubject.configure(background="#800000")
                                    self.welcomeMessageSubject.configure(foreground="#FFFFFF")
                                    self.welcomeMessageSubject.configure(text="Please enter subject!")
                                else:
                                    subName.destroy()
                                    manualFill = tk.Tk()
                                    manualFill.iconbitmap("mainIcon.ico")
                                    manualFill.title("Manual Attedance for " + str(subEntryText))
                                    manualFill.geometry("673x465+336+137")
                                    manualFill.configure(background="#1B1B1B")
                                    manualFill.resizable(1, 1)
                                    manualFill.focus_force()

                                    def removeID():
                                        self.studentIDManualEntry.delete(first=0, last=20)

                                    def removeName():
                                        self.studentNameManualEntry.delete(first=0, last=20)

                                    def enterDataDB():
                                        ID = self.studentIDManualEntry.get()
                                        Name = self.studentNameManualEntry.get()
                                        if ID == "":
                                            self.welcomeMessage.configure(background="#800000")
                                            self.welcomeMessage.configure(foreground="#FFFFFF")
                                            self.welcomeMessage.configure(text="Please enter ID!")
                                        elif Name == "":
                                            self.welcomeMessage.configure(background="#800000")
                                            self.welcomeMessage.configure(foreground="#FFFFFF")
                                            self.welcomeMessage.configure(text="Please enter Name!")
                                        else:
                                            time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                                            Hour, Minute, Second = time.split(":")
                                            insertData = "INSERT INTO " + dbTableName + " (SrNo,ID,Name,Date,Time) VALUES (0, %s, %s, %s,%s)"
                                            VALUES = (str(ID), str(Name), str(Date), str(time))
                                            try:
                                                cursor.execute(insertData, VALUES)
                                            except Exception as e:
                                                print(e)
                                            self.studentIDManualEntry.delete(first=0, last=20)
                                            self.studentNameManualEntry.delete(first=0, last=20)
                                    def createCSV():
                                        import mysql.connector
                                        cursor.execute("select * from " + dbTableName + ";")
                                        csvName='C:/Users/Rushil/OneDrive/Desktop/Attendance Management System/Attendance/' + dbTableName + '.csv'
                                        with open(csvName, "w") as csvFile:
                                            csvWriter = csv.writer(csvFile)
                                            csvWriter.writerow([i[0] for i in cursor.description])  # write headers
                                            csvWriter.writerows(cursor)
                                            self.welcomeMessage.configure(background="#008000")
                                            self.welcomeMessage.configure(text="CSV file created successfully")
                                            if self.welcomeMessage.configure(text="CSV file created successfully"):
                                                print ("Done")
                                        root = tk.Tk()
                                        root.iconbitmap("mainIcon.ico")
                                        root.title("Attendance of " + subEntryText)
                                        root.configure(background='#2B2B2B')
                                        root.focus_force()
                                        with open(csvName, newline="") as file:
                                            reader = csv.reader(file)
                                            r = 0
                                            for col in reader:
                                                c = 0
                                                for row in col:
                                                    label = tk.Label(root, width=13, height=1, fg="black", font=('SF Pro Display', 14, ' bold '), bg="#008000", text=row)
                                                    label.grid(row=r, column=c)
                                                    c += 1
                                                r += 1
                                        root.mainloop()

                                    def sendMailMan():
                                        user = os.environ.get("adminUser")
                                        passwd = os.environ.get("adminPassword")
                                        fileCSV = askopenfilename()
                                        msg = MIMEMultipart()
                                        msg['Subject'] = "Attendance for subject: " + str(subEntryText)
                                        msg['From'] = user
                                        msg['To'] = 'rushil.rc@gmail.com'
                                        msgContent = "Hi there,\n\nPlease find attached for attendance of " + str(subEntryText)
                                        ctype, encoding = mimetypes.guess_type(fileCSV)
                                        if ctype is None or encoding is not None:
                                            ctype = "application/octet-stream"
                                        Content = MIMEText(msgContent,'plain')
                                        maintype, subtype = ctype.split("/", 1)
                                        fp = open(fileCSV,"rb")
                                        attachment = MIMEBase(maintype, subtype)
                                        attachment.set_payload(fp.read())
                                        encoders.encode_base64(attachment)
                                        attachment.add_header("Content-Disposition", "attachment", filename=fileCSV)
                                        msg.attach(attachment)
                                        msg.attach(Content)
                                        with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
                                            smtp.login(user,passwd)
                                            smtp.send_message(msg)
                                            self.welcomeMessage.focus_force()
                                            self.welcomeMessage.configure(text="Mail sent to Admin")

                                    def testVal(inStr, acttyp):
                                        if acttyp == '1':
                                            if not inStr.isdigit():
                                                return False
                                        return True

                                    self.studentIDManual = tk.Label(manualFill)
                                    self.studentIDManual.place(relx=0.089, rely=0.344, height=35, width=155)
                                    self.studentIDManual.configure(background="#1B1B1B")
                                    self.studentIDManual.configure(disabledforeground="#a3a3a3")
                                    self.studentIDManual.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                                    self.studentIDManual.configure(foreground="#ffffff")
                                    self.studentIDManual.configure(text='''Enter Student ID:''')

                                    self.studentNameManual = tk.Label(manualFill)
                                    self.studentNameManual.place(relx=0.089, rely=0.473, height=35, width=186)
                                    self.studentNameManual.configure(background="#1B1B1B")
                                    self.studentNameManual.configure(disabledforeground="#a3a3a3")
                                    self.studentNameManual.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                                    self.studentNameManual.configure(foreground="#FFFFFF")
                                    self.studentNameManual.configure(text='''Enter Student Name:''')

                                    self.mainMessage = tk.Message(manualFill)
                                    self.mainMessage.place(relx=0.0, rely=0.043, relheight=0.135, relwidth=1.0)
                                    self.mainMessage.configure(background="#2E2E2E")
                                    self.mainMessage.configure(font="-family {SF Pro Display} -size 24 -weight bold")
                                    self.mainMessage.configure(foreground="#FFFFFF")
                                    self.mainMessage.configure(highlightbackground="#d9d9d9")
                                    self.mainMessage.configure(highlightcolor="black")
                                    self.mainMessage.configure(text='''Manual Attendance''')
                                    self.mainMessage.configure(width=880)

                                    self.studentIDManualEntry = tk.Entry(manualFill)
                                    self.studentIDManualEntry.place(relx=0.52, rely=0.344, height=33, relwidth=0.367)
                                    self.studentIDManualEntry.configure(background="#D9D9D9")
                                    self.studentIDManualEntry.configure(disabledforeground="#a3a3a3")
                                    self.studentIDManualEntry.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                                    self.studentIDManualEntry.configure(foreground="#000000")
                                    self.studentIDManualEntry.configure(insertbackground="black")
                                    self.studentIDManualEntry.configure(validate='key')
                                    self.studentIDManualEntry['validatecommand'] = (self.studentIDManualEntry.register(testVal), '%P', '%d')

                                    self.studentNameManualEntry = tk.Entry(manualFill)
                                    self.studentNameManualEntry.place(relx=0.52, rely=0.473, height=33, relwidth=0.368)
                                    self.studentNameManualEntry.configure(background="#D9D9D9")
                                    self.studentNameManualEntry.configure(disabledforeground="#a3a3a3")
                                    self.studentNameManualEntry.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                                    self.studentNameManualEntry.configure(foreground="#000000")
                                    self.studentNameManualEntry.configure(insertbackground="black")

                                    self.welcomeMessage = tk.Message(manualFill)
                                    self.welcomeMessage.place(relx=0.083, rely=0.615, relheight=0.092, relwidth=0.805)
                                    self.welcomeMessage.configure(background="#008000")
                                    self.welcomeMessage.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                                    self.welcomeMessage.configure(foreground="#FFFFFF")
                                    self.welcomeMessage.configure(highlightbackground="#d9d9d9")
                                    self.welcomeMessage.configure(highlightcolor="black")
                                    self.welcomeMessage.configure(text='''Welcome, '''+Username)
                                    self.welcomeMessage.configure(width=542)

                                    self.enterData = tk.Button(manualFill)
                                    self.enterData.place(relx=0.083, rely=0.768, height=38, width=110)
                                    self.enterData.configure(activebackground="#ececec")
                                    self.enterData.configure(activeforeground="#000000")
                                    self.enterData.configure(background="#2E2E2E")
                                    self.enterData.configure(disabledforeground="#a3a3a3")
                                    self.enterData.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                                    self.enterData.configure(foreground="#FFFFFF")
                                    self.enterData.configure(highlightbackground="#d9d9d9")
                                    self.enterData.configure(highlightcolor="black")
                                    self.enterData.configure(pady="0")
                                    self.enterData.configure(text='''Enter Data''')
                                    self.enterData.configure(command=enterDataDB)

                                    self.convertToCSV = tk.Button(manualFill)
                                    self.convertToCSV.place(relx=0.394, rely=0.768, height=38, width=134)
                                    self.convertToCSV.configure(activebackground="#ececec")
                                    self.convertToCSV.configure(activeforeground="#000000")
                                    self.convertToCSV.configure(background="#2E2E2E")
                                    self.convertToCSV.configure(disabledforeground="#a3a3a3")
                                    self.convertToCSV.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                                    self.convertToCSV.configure(foreground="#FFFFFF")
                                    self.convertToCSV.configure(highlightbackground="#d9d9d9")
                                    self.convertToCSV.configure(highlightcolor="black")
                                    self.convertToCSV.configure(pady="0")
                                    self.convertToCSV.configure(text='''Create Sheet''')
                                    self.convertToCSV.configure(command=createCSV)

                                    self.sendMailManual = tk.Button(manualFill)
                                    self.sendMailManual.place(relx=0.73, rely=0.768, height=38, width=107)
                                    self.sendMailManual.configure(activebackground="#ececec")
                                    self.sendMailManual.configure(activeforeground="#000000")
                                    self.sendMailManual.configure(background="#2E2E2E")
                                    self.sendMailManual.configure(disabledforeground="#a3a3a3")
                                    self.sendMailManual.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                                    self.sendMailManual.configure(foreground="#FFFFFF")
                                    self.sendMailManual.configure(highlightbackground="#d9d9d9")
                                    self.sendMailManual.configure(highlightcolor="black")
                                    self.sendMailManual.configure(pady="0")
                                    self.sendMailManual.configure(text='''Send Mail''')
                                    self.sendMailManual.configure(command=sendMailMan)

                                    manualFill.mainloop()

                            self.enterSubject = tk.Label(subName)
                            self.enterSubject.place(relx=0.12, rely=0.431, height=29, width=132)
                            self.enterSubject.configure(background="#1B1B1B")
                            self.enterSubject.configure(disabledforeground="#a3a3a3")
                            self.enterSubject.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.enterSubject.configure(foreground="#FFFFFF")
                            self.enterSubject.configure(text='''Enter Subject:''')

                            self.subjectEntry = tk.Entry(subName)
                            self.subjectEntry.place(relx=0.41, rely=0.431, height=27, relwidth=0.451)
                            self.subjectEntry.configure(background="#D9D9D9")
                            self.subjectEntry.configure(disabledforeground="#a3a3a3")
                            self.subjectEntry.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.subjectEntry.configure(foreground="#000000")
                            self.subjectEntry.configure(insertbackground="black")

                            self.fillAttendanceBtn = tk.Button(subName)
                            self.fillAttendanceBtn.place(relx=0.598, rely=0.769, height=38, width=154)
                            self.fillAttendanceBtn.configure(activebackground="#ececec")
                            self.fillAttendanceBtn.configure(activeforeground="#000000")
                            self.fillAttendanceBtn.configure(background="#2E2E2E")
                            self.fillAttendanceBtn.configure(disabledforeground="#a3a3a3")
                            self.fillAttendanceBtn.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.fillAttendanceBtn.configure(foreground="#FFFFFF")
                            self.fillAttendanceBtn.configure(highlightbackground="#d9d9d9")
                            self.fillAttendanceBtn.configure(highlightcolor="black")
                            self.fillAttendanceBtn.configure(pady="0")
                            self.fillAttendanceBtn.configure(text='''Fill Attendance''')
                            self.fillAttendanceBtn.configure(command=fillAttendanceManual)

                            self.chooseSubject = tk.Message(subName)
                            self.chooseSubject.place(relx=0.0, rely=0.062, relheight=0.217, relwidth=1.009)
                            self.chooseSubject.configure(background="#2E2E2E")
                            self.chooseSubject.configure(font="-family {SF Pro Display} -size 36 -weight bold")
                            self.chooseSubject.configure(foreground="#FFFFFF")
                            self.chooseSubject.configure(highlightbackground="#d9d9d9")
                            self.chooseSubject.configure(highlightcolor="black")
                            self.chooseSubject.configure(text='''Choose Subject''')
                            self.chooseSubject.configure(width=585)

                            self.welcomeMessageSubject = tk.Message(subName)
                            self.welcomeMessageSubject.place(relx=0.12, rely=0.591, relheight=0.102, relwidth=0.742)
                            self.welcomeMessageSubject.configure(background="#008000")
                            self.welcomeMessageSubject.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.welcomeMessageSubject.configure(foreground="#FFFFFF")
                            self.welcomeMessageSubject.configure(highlightbackground="#d9d9d9")
                            self.welcomeMessageSubject.configure(highlightcolor="black")
                            self.welcomeMessageSubject.configure(text='''Welcome, '''+Username)
                            self.welcomeMessageSubject.configure(width=434)

                            subName.mainloop()

                        def adminPanel():
                            adminScreen = tk.Tk()
                            adminScreen.geometry("730x389+225+149")
                            adminScreen.resizable(1, 1)
                            adminScreen.title("Admin Panel")
                            adminScreen.iconbitmap("mainIcon.ico")
                            adminScreen.configure(background="#1B1B1B")
                            adminScreen.focus_force()

                            def clearUsername():
                                self.adminUsernameEntry.delete(first=0, last=30)

                            def clearPassword():
                                self.adminPasswordEntry.delete(first=0, last=30)

                            def administratorLogin():
                                UserName = self.adminUsernameEntry.get()
                                Password = self.adminPasswordEntry.get()
                                if UserName == os.environ.get("panelUsername"):
                                    if Password == os.environ.get("panelPassword"):
                                        self.loginMessage.configure(background="#008000")
                                        self.loginMessage.configure(foreground="#FFFFFF")
                                        self.loginMessage.configure(text='''Login Success!''')
                                        studentDetails = tk.Tk()
                                        studentDetails.title("Student Details")
                                        studentDetails.iconbitmap("mainIcon.ico")
                                        studentDetails.configure(background="#1B1B1B")
                                        studentDetails.focus_force()
                                        location = 'C:/Users/Rushil/OneDrive/Desktop/Attendance Management System/StudentDetails.csv'
                                        with open (location, newline="") as file:
                                            reader = csv.reader(file)
                                            r = 0
                                            for col in reader:
                                                c = 0
                                                for row in col:
                                                    self.studentLabel = tk.Label(studentDetails)
                                                    self.studentLabel.configure(background="#008000")
                                                    self.studentLabel.configure(foreground="#000000")
                                                    self.studentLabel.configure(font="-family {SF Pro Display} -size 18 -weight bold")
                                                    self.studentLabel.configure(width=6, height=1)
                                                    self.studentLabel.configure(text=row)
                                                    self.studentLabel.grid(row = r, column = c)
                                                    c += 1
                                                r += 1
                                        adminScreen.iconify()
                                        studentDetails.mainloop()
                                    elif Password == "":
                                        self.loginMessage.configure(background="#800000")
                                        self.loginMessage.configure(foreground="#FFFFFF")
                                        self.loginMessage.configure(text='''Please enter password!''')
                                    else:
                                        self.loginMessage.configure(background="#800000")
                                        self.loginMessage.configure(foreground="#FFFFFF")
                                        self.loginMessage.configure(text='''Incorrect Password!''')
                                        clearPassword()
                                elif UserName == "":
                                    self.loginMessage.configure(background="#800000")
                                    self.loginMessage.configure(foreground="#FFFFFF")
                                    self.loginMessage.configure(text='''Please enter username!''')
                                else:
                                    self.loginMessage.configure(background="#800000")
                                    self.loginMessage.configure(foreground="#FFFFFF")
                                    self.loginMessage.configure(text='''Incorrect Username!''')
                                    clearUsername()

                            self.topMessage = tk.Message(adminScreen)
                            self.topMessage.place(relx=0.0, rely=0.051, relheight=0.175, relwidth=1.041)
                            self.topMessage.configure(background="#2E2E2E")
                            self.topMessage.configure(font="-family {SF Pro Display} -size 36 -weight bold")
                            self.topMessage.configure(foreground="#FFFFFF")
                            self.topMessage.configure(highlightbackground="#d9d9d9")
                            self.topMessage.configure(highlightcolor="black")
                            self.topMessage.configure(text='''Admin Panel''')
                            self.topMessage.configure(width=760)

                            self.adminUsername = tk.Label(adminScreen)
                            self.adminUsername.place(relx=0.096, rely=0.36, height=29, width=155)
                            self.adminUsername.configure(background="#1B1B1B")
                            self.adminUsername.configure(disabledforeground="#a3a3a3")
                            self.adminUsername.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.adminUsername.configure(foreground="#FFFFFF")
                            self.adminUsername.configure(text='''Enter Username:''')

                            self.adminPassword = tk.Label(adminScreen)
                            self.adminPassword.place(relx=0.096, rely=0.54, height=29, width=152)
                            self.adminPassword.configure(background="#1B1B1B")
                            self.adminPassword.configure(disabledforeground="#a3a3a3")
                            self.adminPassword.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.adminPassword.configure(foreground="#FFFFFF")
                            self.adminPassword.configure(text='''Enter Password:''')

                            self.adminUsernameEntry = tk.Entry(adminScreen)
                            self.adminUsernameEntry.place(relx=0.384, rely=0.36, height=27, relwidth=0.362)
                            self.adminUsernameEntry.configure(background="#D9D9D9")
                            self.adminUsernameEntry.configure(disabledforeground="#a3a3a3")
                            self.adminUsernameEntry.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.adminUsernameEntry.configure(foreground="#000000")
                            self.adminUsernameEntry.configure(insertbackground="black")

                            self.adminPasswordEntry = tk.Entry(adminScreen)
                            self.adminPasswordEntry.place(relx=0.384, rely=0.54, height=27, relwidth=0.362)
                            self.adminPasswordEntry.configure(background="#D9D9D9")
                            self.adminPasswordEntry.configure(disabledforeground="#a3a3a3")
                            self.adminPasswordEntry.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.adminPasswordEntry.configure(foreground="#000000")
                            self.adminPasswordEntry.configure(insertbackground="black")
                            self.adminPasswordEntry.configure(show="*")

                            self.clearAdminUsername = tk.Button(adminScreen)
                            self.clearAdminUsername.place(relx=0.803, rely=0.347, height=38, width=66)
                            self.clearAdminUsername.configure(activebackground="#ececec")
                            self.clearAdminUsername.configure(activeforeground="#000000")
                            self.clearAdminUsername.configure(background="#2E2E2E")
                            self.clearAdminUsername.configure(disabledforeground="#a3a3a3")
                            self.clearAdminUsername.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.clearAdminUsername.configure(foreground="#FFFFFF")
                            self.clearAdminUsername.configure(highlightbackground="#d9d9d9")
                            self.clearAdminUsername.configure(highlightcolor="black")
                            self.clearAdminUsername.configure(pady="0")
                            self.clearAdminUsername.configure(text='''Clear''')
                            self.clearAdminUsername.configure(command=clearUsername)

                            self.clearAdminPassword = tk.Button(adminScreen)
                            self.clearAdminPassword.place(relx=0.803, rely=0.527, height=38, width=66)
                            self.clearAdminPassword.configure(activebackground="#ececec")
                            self.clearAdminPassword.configure(activeforeground="#000000")
                            self.clearAdminPassword.configure(background="#2E2E2E")
                            self.clearAdminPassword.configure(disabledforeground="#a3a3a3")
                            self.clearAdminPassword.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.clearAdminPassword.configure(foreground="#FFFFFF")
                            self.clearAdminPassword.configure(highlightbackground="#d9d9d9")
                            self.clearAdminPassword.configure(highlightcolor="black")
                            self.clearAdminPassword.configure(pady="0")
                            self.clearAdminPassword.configure(text='''Clear''')
                            self.clearAdminPassword.configure(command=clearPassword)

                            self.adminLoginBtn = tk.Button(adminScreen)
                            self.adminLoginBtn.place(relx=0.452, rely=0.848, height=38, width=80)
                            self.adminLoginBtn.configure(activebackground="#ececec")
                            self.adminLoginBtn.configure(activeforeground="#000000")
                            self.adminLoginBtn.configure(background="#2E2E2E")
                            self.adminLoginBtn.configure(disabledforeground="#a3a3a3")
                            self.adminLoginBtn.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.adminLoginBtn.configure(foreground="#FFFFFF")
                            self.adminLoginBtn.configure(highlightbackground="#d9d9d9")
                            self.adminLoginBtn.configure(highlightcolor="black")
                            self.adminLoginBtn.configure(pady="0")
                            self.adminLoginBtn.configure(text='''Login''')
                            self.adminLoginBtn.configure(command=administratorLogin)

                            self.loginMessage = tk.Message(adminScreen)
                            self.loginMessage.place(relx=0.096, rely=0.694, relheight=0.111, relwidth=0.795)
                            self.loginMessage.configure(background="#1B1B1B")
                            self.loginMessage.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                            self.loginMessage.configure(foreground="#1B1B1B")
                            self.loginMessage.configure(highlightbackground="#d9d9d9")
                            self.loginMessage.configure(highlightcolor="black")
                            self.loginMessage.configure(text='''Login Success''')
                            self.loginMessage.configure(width=580)

                            adminScreen.mainloop()

                        mainGUI = tk.Tk()
                        mainGUI.geometry("1367x696+-9+0")
                        mainGUI.minsize(120, 1)
                        mainGUI.maxsize(1370, 749)
                        mainGUI.resizable(0, 0)
                        mainGUI.iconbitmap("mainIcon.ico")
                        mainGUI.focus_force()
                        mainGUI.title("Attendance Managment System - Rushil")
                        mainGUI.configure(background="#1B1B1B")
                        mainGUI.configure(highlightbackground="#d9d9d9")
                        mainGUI.configure(highlightcolor="black")

                        self.Title = tk.Message(mainGUI)
                        self.Title.place(relx=-0.007, rely=0.042, relheight=0.134, relwidth=1.005)
                        self.Title.configure(background="#2E2E2E")
                        self.Title.configure(font="-family {SF Pro Display} -size 36 -weight bold")
                        self.Title.configure(foreground="#FFFFFF")
                        self.Title.configure(highlightbackground="#D9D9D9")
                        self.Title.configure(highlightcolor="black")
                        self.Title.configure(text='''Face Recognition Attendance Management System''')
                        self.Title.configure(width=1374)

                        self.studentID = tk.Entry(mainGUI)
                        self.studentID.place(relx=0.338, rely=0.345,height=33, relwidth=0.237)
                        self.studentID.configure(background="#D9D9D9")
                        self.studentID.configure(disabledforeground="#a3a3a3")
                        self.studentID.configure(font="-family {SF Pro Display} -size 18 -weight bold")
                        self.studentID.configure(foreground="#000000")
                        self.studentID.configure(highlightbackground="#d9d9d9")
                        self.studentID.configure(highlightcolor="black")
                        self.studentID.configure(insertbackground="black")
                        self.studentID.configure(relief="flat")
                        self.studentID.configure(selectbackground="#007878d7d777")
                        self.studentID.configure(selectforeground="black")
                        self.studentID.configure(validate='key')
                        self.studentID['validatecommand'] = (self.studentID.register(testVal), '%P', '%d')

                        self.labelStudentID = tk.Label(mainGUI)
                        self.labelStudentID.place(relx=0.067, rely=0.348, height=31, width=204)
                        self.labelStudentID.configure(activebackground="#f9f9f9")
                        self.labelStudentID.configure(activeforeground="black")
                        self.labelStudentID.configure(background="#1B1B1B")
                        self.labelStudentID.configure(disabledforeground="#a3a3a3")
                        self.labelStudentID.configure(font="-family {SF Pro Display} -size 18 -weight bold")
                        self.labelStudentID.configure(foreground="#FFFFFF")
                        self.labelStudentID.configure(highlightbackground="#d9d9d9")
                        self.labelStudentID.configure(highlightcolor="black")
                        self.labelStudentID.configure(text='''Enter Student ID:''')

                        self.labelStudentName = tk.Label(mainGUI)
                        self.labelStudentName.place(relx=0.067, rely=0.454, height=35, width=245)
                        self.labelStudentName.configure(activebackground="#f9f9f9")
                        self.labelStudentName.configure(activeforeground="black")
                        self.labelStudentName.configure(background="#1B1B1B")
                        self.labelStudentName.configure(disabledforeground="#a3a3a3")
                        self.labelStudentName.configure(font="-family {SF Pro Display} -size 18 -weight bold")
                        self.labelStudentName.configure(foreground="#FFFFFF")
                        self.labelStudentName.configure(highlightbackground="#d9d9d9")
                        self.labelStudentName.configure(highlightcolor="black")
                        self.labelStudentName.configure(text='''Enter Student Name:''')

                        self.studentName = tk.Entry(mainGUI)
                        self.studentName.place(relx=0.338, rely=0.46,height=33, relwidth=0.237)
                        self.studentName.configure(background="#D9D9D9")
                        self.studentName.configure(disabledforeground="#a3a3a3")
                        self.studentName.configure(font="-family {SF Pro Display} -size 18 -weight bold")
                        self.studentName.configure(foreground="#000000")
                        self.studentName.configure(highlightbackground="#d9d9d9")
                        self.studentName.configure(highlightcolor="black")
                        self.studentName.configure(insertbackground="black")
                        self.studentName.configure(selectbackground="#c4c4c4")
                        self.studentName.configure(selectforeground="black")

                        self.clearID = tk.Button(mainGUI)
                        self.clearID.place(relx=0.636, rely=0.345, height=38, width=66)
                        self.clearID.configure(activebackground="#ececec")
                        self.clearID.configure(activeforeground="#000000")
                        self.clearID.configure(background="#2E2E2E")
                        self.clearID.configure(disabledforeground="#a3a3a3")
                        self.clearID.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                        self.clearID.configure(foreground="#FFFFFF")
                        self.clearID.configure(highlightbackground="#d9d9d9")
                        self.clearID.configure(highlightcolor="black")
                        self.clearID.configure(pady="0")
                        self.clearID.configure(text='''Clear''')
                        self.clearID.configure(command=deleteID)

                        self.clearName = tk.Button(mainGUI)
                        self.clearName.place(relx=0.636, rely=0.46, height=38, width=66)
                        self.clearName.configure(activebackground="#ececec")
                        self.clearName.configure(activeforeground="#000000")
                        self.clearName.configure(background="#2E2E2E")
                        self.clearName.configure(disabledforeground="#a3a3a3")
                        self.clearName.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                        self.clearName.configure(foreground="#FFFFFF")
                        self.clearName.configure(highlightbackground="#d9d9d9")
                        self.clearName.configure(highlightcolor="black")
                        self.clearName.configure(pady="0")
                        self.clearName.configure(text='''Clear''')
                        self.clearName.configure(command=deleteName)

                        self.Notification = tk.Label(mainGUI)
                        self.Notification.configure(text="Welcome,  "+Username)
                        self.Notification.configure(background="#008000")
                        self.Notification.configure(foreground="#FFFFFF")
                        self.Notification.configure(width=64, height=2)
                        self.Notification.configure(font="-family {SF Pro Display} -size 16 -weight bold")
                        self.Notification.place(x=92, y=430)

                        self.takeImages = tk.Button(mainGUI)
                        self.takeImages.place(relx=0.067, rely=0.818, height=38, width=133)
                        self.takeImages.configure(activebackground="#ececec")
                        self.takeImages.configure(activeforeground="#000000")
                        self.takeImages.configure(background="#2E2E2E")
                        self.takeImages.configure(disabledforeground="#a3a3a3")
                        self.takeImages.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                        self.takeImages.configure(foreground="#FFFFFF")
                        self.takeImages.configure(highlightbackground="#d9d9d9")
                        self.takeImages.configure(highlightcolor="black")
                        self.takeImages.configure(pady="0")
                        self.takeImages.configure(text='''Take Images''')
                        self.takeImages.configure(command=takeImage)

                        self.trainStudent = tk.Button(mainGUI)
                        self.trainStudent.place(relx=0.205, rely=0.818, height=38, width=139)
                        self.trainStudent.configure(activebackground="#ececec")
                        self.trainStudent.configure(activeforeground="#000000")
                        self.trainStudent.configure(background="#2E2E2E")
                        self.trainStudent.configure(disabledforeground="#a3a3a3")
                        self.trainStudent.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                        self.trainStudent.configure(foreground="#FFFFFF")
                        self.trainStudent.configure(highlightbackground="#d9d9d9")
                        self.trainStudent.configure(highlightcolor="black")
                        self.trainStudent.configure(pady="0")
                        self.trainStudent.configure(text='''Train Student''')
                        self.trainStudent.configure(command=trainImage)

                        self.automaticAttendance = tk.Button(mainGUI)
                        self.automaticAttendance.place(relx=0.344, rely=0.818, height=38, width=220)
                        self.automaticAttendance.configure(activebackground="#ececec")
                        self.automaticAttendance.configure(activeforeground="#000000")
                        self.automaticAttendance.configure(background="#2E2E2E")
                        self.automaticAttendance.configure(disabledforeground="#a3a3a3")
                        self.automaticAttendance.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                        self.automaticAttendance.configure(foreground="#FFFFFF")
                        self.automaticAttendance.configure(highlightbackground="#d9d9d9")
                        self.automaticAttendance.configure(highlightcolor="black")
                        self.automaticAttendance.configure(pady="0")
                        self.automaticAttendance.configure(text='''Automatic Attendance''')
                        self.automaticAttendance.configure(command=autoAttendance)

                        self.manualAttendance = tk.Button(mainGUI)
                        self.manualAttendance.place(relx=0.541, rely=0.818, height=38, width=194)
                        self.manualAttendance.configure(activebackground="#ececec")
                        self.manualAttendance.configure(activeforeground="#000000")
                        self.manualAttendance.configure(background="#2E2E2E")
                        self.manualAttendance.configure(disabledforeground="#a3a3a3")
                        self.manualAttendance.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                        self.manualAttendance.configure(foreground="#FFFFFF")
                        self.manualAttendance.configure(highlightbackground="#d9d9d9")
                        self.manualAttendance.configure(highlightcolor="black")
                        self.manualAttendance.configure(pady="0")
                        self.manualAttendance.configure(text='''Manual Attendance''')
                        self.manualAttendance.configure(command=manualAttendance)

                        self.adminPanel = tk.Button(mainGUI)
                        self.adminPanel.place(relx=0.797, rely=0.345, height=38, width=131)
                        self.adminPanel.configure(activebackground="#ececec")
                        self.adminPanel.configure(activeforeground="#000000")
                        self.adminPanel.configure(background="#2E2E2E")
                        self.adminPanel.configure(disabledforeground="#a3a3a3")
                        self.adminPanel.configure(font="-family {SF Pro Display} -size 14 -weight bold")
                        self.adminPanel.configure(foreground="#FFFFFF")
                        self.adminPanel.configure(highlightbackground="#d9d9d9")
                        self.adminPanel.configure(highlightcolor="black")
                        self.adminPanel.configure(pady="0")
                        self.adminPanel.configure(text='''Admin Panel''')
                        self.adminPanel.configure(command=adminPanel)

                        self.authorDetails = tk.Message(mainGUI)
                        self.authorDetails.place(relx=0.753, rely=0.46, relheight=0.407, relwidth=0.19)
                        self.authorDetails.configure(background="#2E2E2E")
                        self.authorDetails.configure(font="-family {SF Pro Display} -size 12 -weight bold")
                        self.authorDetails.configure(foreground="#ffffff")
                        self.authorDetails.configure(highlightbackground="#d9d9d9")
                        self.authorDetails.configure(highlightcolor="black")
                        self.authorDetails.configure(justify='center')
                        self.authorDetails.configure(text='''This software is designed by Rushil Choksi.\n(futher description\nto be added)''')
                        self.authorDetails.configure(width=260)
                    else:
                        self.loginPanelNotification.configure(background="#800000")
                        self.loginPanelNotification.configure(foreground="#FFFFFF")
                        self.loginPanelNotification.configure(text='''Incorrect Password''')
                else:
                    self.loginPanelNotification.configure(background="#800000")
                    self.loginPanelNotification.configure(foreground="#FFFFFF")
                    self.loginPanelNotification.configure(text='''Incorrect Username''')

        def admScreen():

            def checkAdmCredentials():
                UserName = self.adminPanelUsername.get()
                Password = self.adminPanelPassword.get()
                if UserName == os.environ.get("panelUsername"):
                    if Password == os.environ.get("panelPassword"):
                        def regUser():
                            UsernameInfo = self.registrationPanelUsername.get()
                            PasswordInfo = self.registrationPanelPassword.get()
                            PasswordEncryptedInfo = (hashlib.sha512(PasswordInfo.encode())).hexdigest()
                            print (PasswordEncryptedInfo)
                            file = open(UsernameInfo, "w")
                            file.write(UsernameInfo+"\n")
                            file.write(PasswordEncryptedInfo)
                            file.close()
                            self.registrationPanelUsername.delete(0, 30)
                            self.registrationPanelPassword.delete(0, 30)
                            self.registrationPanelNotification.configure(background="#008000")
                            self.registrationPanelNotification.configure(foreground="#FFFFFF")

                        def quitRegScreen():
                            regScreen.destroy()
                            admScreen.destroy()

                        regScreen = tk.Tk()
                        regScreen.iconbitmap("mainIcon.ico")
                        regScreen.geometry("602x405+365+170")
                        regScreen.minsize(120, 1)
                        regScreen.maxsize(1370, 749)
                        regScreen.resizable(0, 0)
                        regScreen.title("Registration Panel")
                        regScreen.configure(background="#1B1B1B")

                        self.mainRegistrationMessage = tk.Message(regScreen)
                        self.mainRegistrationMessage.place(relx=0.0, rely=0.062, relheight=0.153, relwidth=0.998)
                        self.mainRegistrationMessage.configure(background="#2B2B2B")
                        self.mainRegistrationMessage.configure(font="-family {SF Pro Display} -size 24 -weight bold")
                        self.mainRegistrationMessage.configure(foreground="#ffffff")
                        self.mainRegistrationMessage.configure(highlightbackground="#d9d9d9")
                        self.mainRegistrationMessage.configure(highlightcolor="black")
                        self.mainRegistrationMessage.configure(text='''Registration Panel''')
                        self.mainRegistrationMessage.configure(width=601)

                        self.registrationPanelLabelUsername = tk.Label(regScreen)
                        self.registrationPanelLabelUsername.place(relx=0.083, rely=0.346, height=19, width=171)
                        self.registrationPanelLabelUsername.configure(background="#1B1B1B")
                        self.registrationPanelLabelUsername.configure(disabledforeground="#a3a3a3")
                        self.registrationPanelLabelUsername.configure(font="-family {SF Pro Display} -size 16 -weight bold")
                        self.registrationPanelLabelUsername.configure(foreground="#ffffff")
                        self.registrationPanelLabelUsername.configure(text='''Enter Username:''')

                        self.registrationPanelLabelPassword = tk.Label(regScreen)
                        self.registrationPanelLabelPassword.place(relx=0.083, rely=0.519, height=19, width=166)
                        self.registrationPanelLabelPassword.configure(background="#1B1B1B")
                        self.registrationPanelLabelPassword.configure(disabledforeground="#a3a3a3")
                        self.registrationPanelLabelPassword.configure(font="-family {SF Pro Display} -size 16 -weight bold")
                        self.registrationPanelLabelPassword.configure(foreground="#ffffff")
                        self.registrationPanelLabelPassword.configure(text='''Enter Password:''')

                        self.registrationPanelUsername = tk.Entry(regScreen)
                        self.registrationPanelUsername.place(relx=0.449, rely=0.321, height=30, relwidth=0.422)
                        self.registrationPanelUsername.configure(background="white")
                        self.registrationPanelUsername.configure(disabledforeground="#a3a3a3")
                        self.registrationPanelUsername.configure(font="-family {SF Pro Display} -size 16 -weight bold")
                        self.registrationPanelUsername.configure(foreground="#000000")
                        self.registrationPanelUsername.configure(insertbackground="black")

                        self.registrationPanelPassword = tk.Entry(regScreen)
                        self.registrationPanelPassword.place(relx=0.449, rely=0.494, height=30, relwidth=0.422)
                        self.registrationPanelPassword.configure(background="white")
                        self.registrationPanelPassword.configure(disabledforeground="#a3a3a3")
                        self.registrationPanelPassword.configure(font="-family {SF Pro Display} -size 16 -weight bold")
                        self.registrationPanelPassword.configure(foreground="#000000")
                        self.registrationPanelPassword.configure(insertbackground="black")
                        self.registrationPanelPassword.configure(show="*")

                        self.registrationPanelNotification = tk.Message(regScreen)
                        self.registrationPanelNotification.place(relx=0.083, rely=0.647, relheight=0.094, relwidth=0.781)
                        self.registrationPanelNotification.configure(background="#1B1B1B")
                        self.registrationPanelNotification.configure(font="-family {SF Pro Display} -size 16 -weight bold")
                        self.registrationPanelNotification.configure(foreground="#1B1B1B")
                        self.registrationPanelNotification.configure(highlightbackground="#d9d9d9")
                        self.registrationPanelNotification.configure(highlightcolor="black")
                        self.registrationPanelNotification.configure(text='''Registered successfully!''')
                        self.registrationPanelNotification.configure(width=470)

                        self.registrationPanelLogin = tk.Button(regScreen)
                        self.registrationPanelLogin.place(relx=0.083, rely=0.822, height=34, width=103)
                        self.registrationPanelLogin.configure(activebackground="#ececec")
                        self.registrationPanelLogin.configure(activeforeground="#000000")
                        self.registrationPanelLogin.configure(background="#2E2E2E")
                        self.registrationPanelLogin.configure(disabledforeground="#a3a3a3")
                        self.registrationPanelLogin.configure(font="-family {SF Pro Display} -size 16 -weight bold")
                        self.registrationPanelLogin.configure(foreground="#FFFFFF")
                        self.registrationPanelLogin.configure(highlightbackground="#d9d9d9")
                        self.registrationPanelLogin.configure(highlightcolor="black")
                        self.registrationPanelLogin.configure(pady="0")
                        self.registrationPanelLogin.configure(text='''Login''')
                        self.registrationPanelLogin.configure(command=quitRegScreen)

                        self.registrationPanelRegister = tk.Button(regScreen)
                        self.registrationPanelRegister.place(relx=0.698, rely=0.822, height=34, width=103)
                        self.registrationPanelRegister.configure(activebackground="#ececec")
                        self.registrationPanelRegister.configure(activeforeground="#000000")
                        self.registrationPanelRegister.configure(background="#2E2E2E")
                        self.registrationPanelRegister.configure(disabledforeground="#a3a3a3")
                        self.registrationPanelRegister.configure(font="-family {SF Pro Display} -size 16 -weight bold")
                        self.registrationPanelRegister.configure(foreground="#ffffff")
                        self.registrationPanelRegister.configure(highlightbackground="#d9d9d9")
                        self.registrationPanelRegister.configure(highlightcolor="black")
                        self.registrationPanelRegister.configure(pady="0")
                        self.registrationPanelRegister.configure(text='''Register''')
                        self.registrationPanelRegister.configure(command=regUser)

                    else:
                        self.adminPanelNotification.configure(background="#800000")
                        self.adminPanelNotification.configure(foreground="#FFFFFF")
                        self.adminPanelNotification.configure(text='''Incorrect Password''')
                else:
                    self.adminPanelNotification.configure(background="#800000")
                    self.adminPanelNotification.configure(foreground="#FFFFFF")
                    self.adminPanelNotification.configure(text='''Incorrect Username''')

            admScreen = tk.Tk()
            admScreen.iconbitmap("mainIcon.ico")
            admScreen.geometry("602x405+365+170")
            admScreen.minsize(120, 1)
            admScreen.maxsize(1370, 749)
            admScreen.resizable(0, 0)
            admScreen.title("Admin Panel")
            admScreen.configure(background="#1B1B1B")
            admScreen.configure(highlightbackground="#d9d9d9")
            admScreen.configure(highlightcolor="black")

            self.mainAdminMessage = tk.Message(admScreen)
            self.mainAdminMessage.place(relx=0.0, rely=0.062, relheight=0.153, relwidth=0.998)
            self.mainAdminMessage.configure(background="#2B2B2B")
            self.mainAdminMessage.configure(font="-family {SF Pro Display} -size 24 -weight bold")
            self.mainAdminMessage.configure(foreground="#ffffff")
            self.mainAdminMessage.configure(highlightbackground="#d9d9d9")
            self.mainAdminMessage.configure(highlightcolor="black")
            self.mainAdminMessage.configure(text='''Admin Panel''')
            self.mainAdminMessage.configure(width=601)

            self.adminPanelLabelUsername = tk.Label(admScreen)
            self.adminPanelLabelUsername.place(relx=0.083, rely=0.346, height=19, width=181)
            self.adminPanelLabelUsername.configure(activebackground="#f9f9f9")
            self.adminPanelLabelUsername.configure(activeforeground="black")
            self.adminPanelLabelUsername.configure(background="#1B1B1B")
            self.adminPanelLabelUsername.configure(disabledforeground="#a3a3a3")
            self.adminPanelLabelUsername.configure(font="-family {SF Pro Display} -size 16 -weight bold")
            self.adminPanelLabelUsername.configure(foreground="#ffffff")
            self.adminPanelLabelUsername.configure(highlightbackground="#d9d9d9")
            self.adminPanelLabelUsername.configure(highlightcolor="black")
            self.adminPanelLabelUsername.configure(text='''Admin Username:''')

            self.adminPanelLabelPassword = tk.Label(admScreen)
            self.adminPanelLabelPassword.place(relx=0.083, rely=0.519, height=19, width=176)
            self.adminPanelLabelPassword.configure(activebackground="#f9f9f9")
            self.adminPanelLabelPassword.configure(activeforeground="black")
            self.adminPanelLabelPassword.configure(background="#1B1B1B")
            self.adminPanelLabelPassword.configure(disabledforeground="#a3a3a3")
            self.adminPanelLabelPassword.configure(font="-family {SF Pro Display} -size 16 -weight bold")
            self.adminPanelLabelPassword.configure(foreground="#ffffff")
            self.adminPanelLabelPassword.configure(highlightbackground="#d9d9d9")
            self.adminPanelLabelPassword.configure(highlightcolor="black")
            self.adminPanelLabelPassword.configure(text='''Admin Password:''')

            self.adminPanelUsername = tk.Entry(admScreen)
            self.adminPanelUsername.place(relx=0.449, rely=0.321, height=30, relwidth=0.422)
            self.adminPanelUsername.configure(background="white")
            self.adminPanelUsername.configure(disabledforeground="#a3a3a3")
            self.adminPanelUsername.configure(font="-family {SF Pro Text} -size 16 -weight bold")
            self.adminPanelUsername.configure(foreground="#000000")
            self.adminPanelUsername.configure(highlightbackground="#d9d9d9")
            self.adminPanelUsername.configure(highlightcolor="black")
            self.adminPanelUsername.configure(insertbackground="black")
            self.adminPanelUsername.configure(selectbackground="#c4c4c4")
            self.adminPanelUsername.configure(selectforeground="black")

            self.adminPanelPassword = tk.Entry(admScreen)
            self.adminPanelPassword.place(relx=0.449, rely=0.494, height=30, relwidth=0.422)
            self.adminPanelPassword.configure(background="#D9D9D9")
            self.adminPanelPassword.configure(disabledforeground="#a3a3a3")
            self.adminPanelPassword.configure(font="-family {SF Pro Text} -size 16 -weight bold")
            self.adminPanelPassword.configure(foreground="#000000")
            self.adminPanelPassword.configure(highlightbackground="#d9d9d9")
            self.adminPanelPassword.configure(highlightcolor="black")
            self.adminPanelPassword.configure(insertbackground="black")
            self.adminPanelPassword.configure(selectbackground="#c4c4c4")
            self.adminPanelPassword.configure(selectforeground="black")
            self.adminPanelPassword.configure(show="*")

            self.adminPanelNotification = tk.Message(admScreen)
            self.adminPanelNotification.place(relx=0.083, rely=0.647, relheight=0.094, relwidth=0.781)
            self.adminPanelNotification.configure(background="#1B1B1B")
            self.adminPanelNotification.configure(font="-family {SF Pro Display} -size 16 -weight bold")
            self.adminPanelNotification.configure(foreground="#FFFFFF")
            self.adminPanelNotification.configure(highlightbackground="#d9d9d9")
            self.adminPanelNotification.configure(highlightcolor="black")
            self.adminPanelNotification.configure(text='''*you need to be admin to register*''')
            self.adminPanelNotification.configure(width=470)

            self.adminPanelLogin = tk.Button(admScreen)
            self.adminPanelLogin.place(relx=0.698, rely=0.822, height=34, width=103)
            self.adminPanelLogin.configure(activebackground="#ececec")
            self.adminPanelLogin.configure(activeforeground="#000000")
            self.adminPanelLogin.configure(background="#2E2E2E")
            self.adminPanelLogin.configure(disabledforeground="#a3a3a3")
            self.adminPanelLogin.configure(font="-family {SF Pro Display} -size 16 -weight bold")
            self.adminPanelLogin.configure(foreground="#FFFFFF")
            self.adminPanelLogin.configure(highlightbackground="#d9d9d9")
            self.adminPanelLogin.configure(highlightcolor="black")
            self.adminPanelLogin.configure(pady="0")
            self.adminPanelLogin.configure(text='''Login''')
            self.adminPanelLogin.configure(command=checkAdmCredentials)

        logScreen.iconbitmap("mainIcon.ico")
        logScreen.geometry("602x405+365+170")
        logScreen.minsize(120, 1)
        logScreen.maxsize(1370, 749)
        logScreen.resizable(0, 0)
        logScreen.title("Login Panel")
        logScreen.configure(background="#1B1B1B")
        logScreen.configure(highlightbackground="#d9d9d9")
        logScreen.configure(highlightcolor="black")

        self.mainLoginMessage = tk.Message(logScreen)
        self.mainLoginMessage.place(relx=0.0, rely=0.062, relheight=0.153, relwidth=0.998)
        self.mainLoginMessage.configure(background="#2B2B2B")
        self.mainLoginMessage.configure(font="-family {SF Pro Display} -size 24 -weight bold")
        self.mainLoginMessage.configure(foreground="#ffffff")
        self.mainLoginMessage.configure(highlightbackground="#d9d9d9")
        self.mainLoginMessage.configure(highlightcolor="black")
        self.mainLoginMessage.configure(text='''Login Panel''')
        self.mainLoginMessage.configure(width=601)

        self.loginPanelLabelUsername = tk.Label(logScreen)
        self.loginPanelLabelUsername.place(relx=0.083, rely=0.346, height=19, width=171)
        self.loginPanelLabelUsername.configure(activebackground="#f9f9f9")
        self.loginPanelLabelUsername.configure(activeforeground="black")
        self.loginPanelLabelUsername.configure(background="#1B1B1B")
        self.loginPanelLabelUsername.configure(disabledforeground="#a3a3a3")
        self.loginPanelLabelUsername.configure(font="-family {SF Pro Display} -size 16 -weight bold")
        self.loginPanelLabelUsername.configure(foreground="#ffffff")
        self.loginPanelLabelUsername.configure(highlightbackground="#d9d9d9")
        self.loginPanelLabelUsername.configure(highlightcolor="black")
        self.loginPanelLabelUsername.configure(text='''Enter Username:''')

        self.loginPanelLabelPassword = tk.Label(logScreen)
        self.loginPanelLabelPassword.place(relx=0.083, rely=0.519, height=19, width=166)
        self.loginPanelLabelPassword.configure(activebackground="#f9f9f9")
        self.loginPanelLabelPassword.configure(activeforeground="black")
        self.loginPanelLabelPassword.configure(background="#1B1B1B")
        self.loginPanelLabelPassword.configure(disabledforeground="#a3a3a3")
        self.loginPanelLabelPassword.configure(font="-family {SF Pro Display} -size 16 -weight bold")
        self.loginPanelLabelPassword.configure(foreground="#ffffff")
        self.loginPanelLabelPassword.configure(highlightbackground="#d9d9d9")
        self.loginPanelLabelPassword.configure(highlightcolor="black")
        self.loginPanelLabelPassword.configure(text='''Enter Password:''')

        self.loginPanelUsername = tk.Entry(logScreen)
        self.loginPanelUsername.place(relx=0.449, rely=0.321, height=30, relwidth=0.422)
        self.loginPanelUsername.configure(background="#D9D9D9")
        self.loginPanelUsername.configure(disabledforeground="#a3a3a3")
        self.loginPanelUsername.configure(font="-family {SF Pro Text} -size 16 -weight bold")
        self.loginPanelUsername.configure(foreground="#000000")
        self.loginPanelUsername.configure(highlightbackground="#d9d9d9")
        self.loginPanelUsername.configure(highlightcolor="black")
        self.loginPanelUsername.configure(insertbackground="black")
        self.loginPanelUsername.configure(selectbackground="#c4c4c4")
        self.loginPanelUsername.configure(selectforeground="black")

        self.loginPanelPassword = tk.Entry(logScreen)
        self.loginPanelPassword.place(relx=0.449, rely=0.494, height=30, relwidth=0.422)
        self.loginPanelPassword.configure(background="#D9D9D9")
        self.loginPanelPassword.configure(disabledforeground="#a3a3a3")
        self.loginPanelPassword.configure(font="-family {SF Pro Text} -size 16 -weight bold")
        self.loginPanelPassword.configure(foreground="#000000")
        self.loginPanelPassword.configure(highlightbackground="#d9d9d9")
        self.loginPanelPassword.configure(highlightcolor="black")
        self.loginPanelPassword.configure(insertbackground="black")
        self.loginPanelPassword.configure(selectbackground="#c4c4c4")
        self.loginPanelPassword.configure(selectforeground="black")
        self.loginPanelPassword.configure(show="*")

        self.loginPanelNotification = tk.Message(logScreen)
        self.loginPanelNotification.place(relx=0.083, rely=0.647, relheight=0.094, relwidth=0.781)
        self.loginPanelNotification.configure(background="#1B1B1B")
        self.loginPanelNotification.configure(font="-family {SF Pro Display} -size 16 -weight bold")
        self.loginPanelNotification.configure(foreground="#1B1B1B")
        self.loginPanelNotification.configure(highlightbackground="#d9d9d9")
        self.loginPanelNotification.configure(highlightcolor="black")
        self.loginPanelNotification.configure(text='''Incorrect ID or Password''')
        self.loginPanelNotification.configure(width=470)

        self.loginPanelRegister = tk.Button(logScreen)
        self.loginPanelRegister.place(relx=0.083, rely=0.822, height=34, width=103)
        self.loginPanelRegister.configure(activebackground="#ececec")
        self.loginPanelRegister.configure(activeforeground="#000000")
        self.loginPanelRegister.configure(background="#2E2E2E")
        self.loginPanelRegister.configure(disabledforeground="#a3a3a3")
        self.loginPanelRegister.configure(font="-family {SF Pro Display} -size 16 -weight bold")
        self.loginPanelRegister.configure(foreground="#FFFFFF")
        self.loginPanelRegister.configure(highlightbackground="#d9d9d9")
        self.loginPanelRegister.configure(highlightcolor="black")
        self.loginPanelRegister.configure(pady="0")
        self.loginPanelRegister.configure(text='''Register''')
        self.loginPanelRegister.configure(command=admScreen)

        self.loginPanelLogin = tk.Button(logScreen)
        self.loginPanelLogin.place(relx=0.698, rely=0.822, height=34, width=103)
        self.loginPanelLogin.configure(activebackground="#ececec")
        self.loginPanelLogin.configure(activeforeground="#000000")
        self.loginPanelLogin.configure(background="#2E2E2E")
        self.loginPanelLogin.configure(disabledforeground="#a3a3a3")
        self.loginPanelLogin.configure(font="-family {SF Pro Display} -size 16 -weight bold")
        self.loginPanelLogin.configure(foreground="#ffffff")
        self.loginPanelLogin.configure(highlightbackground="#d9d9d9")
        self.loginPanelLogin.configure(highlightcolor="black")
        self.loginPanelLogin.configure(pady="0")
        self.loginPanelLogin.configure(text='''Login''')
        self.loginPanelLogin.configure(command=logUser)

if __name__ == '__main__':
    vp_start_gui()
