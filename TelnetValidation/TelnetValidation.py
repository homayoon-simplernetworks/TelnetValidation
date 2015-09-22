# this program will validate telnet connection to ez-edge ADF

import getpass
import telnetlib
import time
import binascii
import sys
import yaml

from tkinter import *

class App(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()

        
class yld:
        def __init__ (self):
                data = {}
                
        def yaml_loader(filepath):
                """Loads a yaml file"""
                with open(filepath, "r") as file_descriptor:
                        data = yaml.load(file_descriptor)
                return data

        def ymal_dump(filepath, data):
                """Dump data to a yaml file"""
                with open(filepath, "w") as file_desxriptor:
                        yaml.dump(data, file_descriptor)

# open telnet connection
def telnetConnection():
    #telnet to ez-edge
    try:
       global tn 
       tn = telnetlib.Telnet(HOST, PORT)
       print ('connected to' , HOST,PORT,'....')
    except ValueError:
        print ( 'telnet connection to ' , HOST, PORT, 'is not possible: ' , ValueError)
        w = input ('press enter to exit')
        exit()
    
def userValidation(user, password, testT):
    try:
            
            global TooManyPassTry
            TooManyPassTry = 1
            #to keep tracking of Too many invalid user 
            if testT == testType[2]: TooManyPassTry += 1



            #prepare list of all possible state 
        
            # list of all possible state after initially send user and pass
            InitialExpectedList = [b'Invalid user/password', b'Welcome to'  ]
        
            #list of all possible state after invalid user
            InvalidUserList = [ b'User    :', b'Too many invalid', b'Welcome to']
                    
            def Invaliduser():
                if testT == testType[0]:
                    print ('invalid user test has been passed')
                elif testT == testType[1]:
                    print ('invalid pass test has been passed')
                elif testT == testType[2]:
                    tnexInvalid = tn.expect(InvalidUserList, 15)
                    
                    if tnexInvalid[0] == 0 :
                        
                        if TooManyPassTry<4 : 
                            userValidation(user, password, testT)
                        else:
                            print ('too many invalid user/ pass failed, still system ask for new user ')
                            w = input ('press enter to close ...')
                            exit()
                    elif tnexInvalid[0] == 2:
                        print ('too many invalid user/ pass test failed, system is loged in!!!')
                        w = input ('press enter to exit ...')
                    elif tnexInvalid[0] == 1: 
                        print ('too many invalid user/ pass test has been passed' )
                        tn.close()
                        # in this state connection has been closed, to continue the we need to re open the connection 
                        telnetConnection()
                    elif tnexInvalid[0] == -1:
                        print ('too many invalid user/ pass failed, timeout')
                        w= input('enter to exit....')
                        tn.close()
                        exit()

            def Validuser():
                print ('valid user test has been passed' )
        
            def timeoutR():
                print('timeout')
        
            InitialOptions = { -1: timeoutR,
                       0 : Invaliduser,
                       1: Validuser}
        
        
        
            def loginTo():
                if not testT == testType[2]: tn.read_until(b"User    : ")
                else:
                    tn.read_until(b"User    : ",2)
                tn.write( user.strip().encode('ascii') + b'\r\n')
                print ('user: ', user , ' has been sent to system')
                
                if not testT == testType[2]:tn.read_until(b"Password: ")
                else:
                    tn.read_until(b"Password: ",2)

                tn.write(password.encode('ascii') + b'\r\n')
                print ('Password: ', password , ' has been sent to system')
                
            

            loginTo()
            us = tn.expect(InitialExpectedList, 15)
        
            InitialOptions[us[0]]()
            
    except ValueError:
        print ( 'telnet connection to ' , HOST, PORT, 'is not possible: ' , ValueError)
        w = input ('press enter to exit')
        exit()

    except EOFError:
        print ('telnet connection to ' , HOST, PORT, 'has been closed: ' , EOFError)
        w = input('press enter ...')
        exit()

if __name__ == "__main__":
    global HOST
    HOST = '192.168.3.115'
    global PORT 
    PORT = '5555'
    #user = input("Enter your remote account: ")
    #password = getpass.getpass()
    user="admin"
    password="ez-edge#1"
    command ="help"

    global testType 
    testType = ['bad user','bad pass','Too many invalid user', 'valid user' , 'just login']

   
    #telnet to ez-edge
    telnetConnection()


    #these test steps will test bad user name 
    userValidation(user + 'ff',password ,testType[0])
    userValidation(user,password + 'ff' , testType[1])
    userValidation(user,password + 'ff' , testType[2])
    userValidation(user,password , testType[3])



    tn.read_until(b"User    : ")

    tn.write(b"admin\r\n")
    tn.read_until(b"Password: ")
    #print("all I read" , tn.read_eager().decode('ascii'))
    tn.write(b"ez-edge#1\r\n")
    print("4")
    time.sleep(4)
    tn.write(b"exit\r\n")
    print("all I read" , tn.read_all().decode('ascii'))
