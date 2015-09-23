# this program will validate telnet connection to ez-edge ADF
import getpass
import telnetlib
import time
import binascii
import sys
import yaml
import yld


from tkinter import *
# this class is for future use,
class App(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()

        
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

                #too many invalid user needs to recall the program, becuase already 'User    :' has been 
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

#send commends and log message
# this code just will use to log system message for each command
def logger():
    #open file that has list of commands
    try:
        with open("commandlist.txt") as fi:
                Commands = fi.readlines()
        
        for command in Commands: 
                #because I don't know is system is waiting for command or there is something coming I put this      
                tn.read_until(b'[CLI Telnet]$' , 3)
                tn.write(commm.encode('ascii') + b'\r\n')
                # Cause a 3-second pause between sends by waiting for something "unexpected"
        		# with a timeout value.
                logg = tn.read_until(b'something',3)
                lo[comm] = logg.decode('ascii')
    except  Exception :
        print('it is not possible to open this file: commandlist.txt' , EXCEPTION)
        sys.exit(1)
        
    #log information into a yaml file
    tt = time.localtime()
    ffp  = 'commandtest_'+ time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
    yf.ymal_dump(ffp,lo)
    tn.close()
    exit()
    


if __name__ == "__main__":
    
    #load variables (Host IP, user , pass ...)
    fp = "variables.yaml"
    yf = yld.yld
    vars = yf.yaml_loader(fp)
    
    # variables
    global HOST
    HOST = vars['host'].strip() #'192.168.3.115'
    global PORT 
    PORT = vars['port'].strip()  # '5555'
    user= vars['user'].strip()  #     "admin"
    password=vars['password'].strip()  #"ez-edge#1"
    commandRef =vars['commandRef'].strip() #command and expected messages file address 
    
    
    testType = ['bad user','bad pass','Too many invalid user', 'valid user' , 'just login']
    #exit()
   

    
    
    #telnet to ez-edge
    telnetConnection()


    #these test steps will test bad user name 
    userValidation(user + 'ff',password ,testType[0])
    userValidation(user,password + 'ff' , testType[1])
    userValidation(user,password + 'ff' , testType[2])
    userValidation(user,password , testType[3])


    # this part checks if script has been run with logger command or not, if yes it will 
    # send series of commands to system and it will create yaml file to use it as reference for test 
    if str(sys.argv[1]).strip() =='logger':  logger()

   

    time.sleep(4)
    tn.write(b"exit\r\n")
    print("all I read" , tn.read_all().decode('ascii'))
    w= input('enter ...')


