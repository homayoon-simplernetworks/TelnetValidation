# potentially being missed.


import getpass
import telnetlib
import time
import binascii

HOST = "192.168.3.115"
#user = input("Enter your remote account: ")
#password = getpass.getpass()
user="admin"
password="ez-edge#1"
command ="help"

#telnet to ez-edge
tn = telnetlib.Telnet(HOST, 5555)


#these test steps will test bad user name 

tn.read_until(b"User    : ")
#send invalid user name with correct password
tn.write(b"admin\r\n")
tn.read_until(b"Password: ")
tn.write(b"ez-edge#1\r\n")
us = tn.read_until(b"Invalid user" , 6)

if 'Invalid' in str (us):
    print ('Invalid user tested')
else:
    print ('Invalid user has been sent to system but expected message is not sent by system')
    print(us)
    print("all I read" , tn.read_eager().decode('ascii'))
    ff = input('inter ...')
    tn.close()
    exit()  



tn.read_until(b"User    : ")

tn.write(b"admin\r\n")
tn.read_until(b"Password: ")
#print("all I read" , tn.read_eager().decode('ascii'))
tn.write(b"ez-edge#1\r\n")
print("4")
time.sleep(4)
tn.write(b"exit\r\n")
print("all I read" , tn.read_all().decode('ascii'))
