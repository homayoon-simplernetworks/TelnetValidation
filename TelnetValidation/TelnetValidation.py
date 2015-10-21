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
            global toBeLogItems
            toBeLogItems = {}


            #prepare list of all possible state 
        
            # list of all possible state after initially send user and pass
            InitialExpectedList = [b'Invalid user/password', b'Welcome to'  ]
        
            #list of all possible state after invalid user
            InvalidUserList = [ b'User    :', b'Too many invalid', b'Welcome to']
                    
            def Invaliduser():
                if testT == testType[0]:
                    toBeLog  = 'invalid user test has been passed'
                    print (toBeLog)
                elif testT == testType[1]:
                    toBeLog = 'invalid pass test has been passed'
                    print (toBeLog)
                elif testT == testType[2]:
                    tnexInvalid = tn.expect(InvalidUserList, 15)
                    
                    if tnexInvalid[0] == 0 :
                        
                        if TooManyPassTry<4 : 
                            userValidation(user, password, testT)
                        else:
                            toBeLog = 'too many invalid user/ pass failed, still system ask for new user '
                            print (toBeLog)
                            w = input ('press enter to close ...')
                            exit()
                    elif tnexInvalid[0] == 2:
                        toBeLog = 'too many invalid user/ pass test failed, system is logged in!!!'
                        print (toBeLog)
                        w = input ('press enter to exit ...')
                    elif tnexInvalid[0] == 1: 
                        toBeLog = 'too many invalid user/ pass test has been passed'
                        print (toBeLog)
                        tn.close()
                        # in this state connection has been closed, to continue the we need to re open the connection 
                        telnetConnection()
                    elif tnexInvalid[0] == -1:
                        toBeLog = 'too many invalid user/ pass failed, timeout'
                        print (toBeLog)
                        w= input('enter to exit....')
                        tn.close()
                        exit()
                if toBeLog: toBeLogItems[testT] = toBeLog

            def Validuser():
                toBeLog = 'valid user test has been passed'
                print (toBeLog )
                toBeLogItems[testT] = toBeLog
        
            def timeoutR():
                toBeLog = 'timeout'
                print(toBeLog)
                toBeLogItems[testT] = toBeLog
        
            InitialOptions = { -1: timeoutR,
                       0 : Invaliduser,
                       1: Validuser}
        
        
        
            def loginTo():

                #too many invalid user needs to recall the program, because already 'User    :' has been 
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
def logger(filename):
    #open file that has list of commands
    try:
        global lo
        lo={}
        with open(filename , 'r') as fi:
                Commands = fi.readlines()
        
        for command in Commands: 
                
                #because I don't know is system is waiting for command or there is something coming I put this      
                tn.read_until(b'CLI Telnet]$ ' , 3)
                time.sleep(1)
                print (command)
                tn.write(command.strip("\n").encode('ascii') + b'\r\n')
                # Cause a 3-second pause between sends by waiting for something "unexpected"
        		# with a timeout value.
                logg = tn.read_until(b'CLI Telnet]$ ' , 3)
                lo[command.strip("\n")] =  logg.decode("ascii") 
                print (lo)
    
        
        #log information into a yaml file
        tt = time.localtime()
        w = input('wait .................')
        ffp  = 'commandtest_'+ time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) +'.yaml'
        yf.yaml_dump(ffp,lo)
        tn.close()
        exit()

    except  Exception :
        print('it is not possible to open this file: commandlist.txt' , EXCEPTION)
        
    
def commandTester(filename):
    #open file that has list of commands
    try:
        global allTestResultItems
        allTestResultItems = {}
        global recheckTestResultItems
        recheckTestResultItems = {}
        global failedTestResultItems
        failedTestResultItems = {}

        commandsMesages = yf.yaml_loader(filename)
               
        for item_name, item_value in commandsMesages.items():
            #print (item_name, item_value)
            #because I don't know is system is waiting for command or there is something coming I put this      
            tn.read_until(b'[CLI Telnet]$ ' , 3)
            time.sleep(0.5)
            tn.write(item_name.encode('ascii') + b'\r\n')
            print( 'command', item_name , ' has been sent ')
            
           
            #message normally contains 'Cmd Success.' to have both options in below list, I need to remove it form original message
            ms = str(item_value).strip()
            ms = ms[0:ms.find('Cmd Success')]
            ms = ms [:200]

            #list of possible message form ez-edge
            exList = [b'Cmd failed.' , b'Cmd Success.' , ms.strip().encode('ascii')]

            #wait 5 sec or receive one of the possible expected message
            #check if received value is same as expected value
            logg = tn.expect(exList,5)

            testResult = 'command failed'
            if logg[0] == 2 : 
                testResult = 'Pass'
                print( 'test has been passed')
                testResultItemAll = { 'test result': testResult , 'time' : time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()) , 'expected value' : item_value , 'received value' : logg[2].decode('ascii')}
            elif logg[0] == 1:
                print('ez-edge has accepted the command, but the message that is sent by system is not exactly same as expected message, please verify re_check logs ')
                testResult = 're-check please'
                testResultItemAll = { 'test result': testResult , 'time' : time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()) , 'expected value' : item_value , 'received value' : logg[2].decode('ascii')}
                recheckTestResultItems[item_name] = testResultItemAll
            elif logg[0] == 0:
                print('command failed please check failed log')
                testResult = 'command failed'
                testResultItemAll = { 'test result': testResult , 'time' : time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()) , 'expected value' : item_value , 'received value' : logg[2].decode('ascii')}
                failedTestResultItems[item_name] = testResultItemAll
            elif logg[0] == -1:
                print('command does not failed or passed please check recheck log')
                testResult = 'command failed or pass'
                testResultItemAll = { 'test result': testResult , 'time' : time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()) , 'expected value' : item_value , 'received value' : logg[2].decode('ascii')}
                recheckTestResultItems[item_name] = testResultItemAll
            else:
                print('state is unknown')
                testResult = 'unknown'
                testResultItemAll = { 'test result': testResult , 'time' : time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()) , 'expected value' : item_value , 'received value' : logg[2].decode('ascii')}
                failedTestResultItems[item_name] = testResultItemAll

            allTestResultItems[item_name] = testResultItemAll
            
        #log information into a yaml file
        #file name for test result (all)
        fileAllTestResultItems  = loggerPath + 'commandtest_'+ time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + '.yaml'
        yf.yaml_dump(fileAllTestResultItems,allTestResultItems)

        #file name for just failed test
        fileFailedTestResultItems  = loggerPath + 'failedCommandtest_'+ time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + '.yaml'
        #check if there is any failed test     
        if failedTestResultItems: yf.yaml_dump(fileFailedTestResultItems,failedTestResultItems)

        #file name for just recheck test
        fileRecheckTestResultItems  = loggerPath + 'recheckCommandtest_'+ time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + '.yaml'
        #check if there is any recheck test     
        if recheckTestResultItems: yf.yaml_dump(fileRecheckTestResultItems,recheckTestResultItems)

        

        tn.close()
        exit()
            
    #except  Exception :
        #print('it is not possible to open this file: commandlist.txt' , EXCEPTION)
        
    except EOFError:
        print ('telnet connection to ' , HOST, PORT, 'has been closed: ' , EOFError)
        w = input('press enter ...')
        
        
    
def timeoutSession(filemame):
    print('timeout test is running please do not close the program, start time: ' , time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()))
    time.sleep(16000)
    print('timeout test is running please do not close the program, start time: ' , time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()))




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
    loggerPath = vars['loggerPath'].strip() #address for save log files
    testMode = vars['testMode'].strip() # switch between 'logger' or 'command' validation and 'timeout' test
    loggerInput = vars['loggerInput']
    testType = ['bad user','bad pass','Too many invalid user', 'valid user' , 'just login']
   
    #telnet to ez-edge
    telnetConnection()

    toBeLogItemsAll = {}
    #these test steps will test bad user name or password
    if testMode == 'login' :
        userValidation(user + 'ff',password ,testType[0])
        toBeLogItemsAll.update ( toBeLogItems)
        userValidation(user,password + 'ff' , testType[1])
        toBeLogItemsAll.update ( toBeLogItems)
        userValidation(user,password + 'ff' , testType[2])
        toBeLogItemsAll.update ( toBeLogItems)

    # all other test modes needs login, 
    userValidation(user,password , testType[3])
    toBeLogItemsAll.update ( toBeLogItems)
        
    #log information into a yaml file
    #file name for login test result (all)
    fileLoginTestResultItems  = loggerPath + 'LoginTest_'+ time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + '.yaml'
    yf.yaml_dump(fileLoginTestResultItems,toBeLogItemsAll)

    # this part checks if script has been run with logger command or not, if yes it will 
    # send series of commands to system and it will create yaml file to use it as reference for test 
    if testMode =='logger':  logger(loggerInput)
    if testMode == 'command' : commandTester(commandRef)
    if testMode == 'timeout' : timeoutsession(commandRef)

    time.sleep(4)
    tn.write(b"exit\r\n")
    print("all I read" , tn.read_all().decode('ascii'))
    w= input('enter ...')


