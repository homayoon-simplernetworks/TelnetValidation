# potentially being missed.


import getpass
import telnetlib
import time

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

tn.write(b"admin\r\n")
tn.read_until(b"Password: ")
#print("all I read" , tn.read_eager().decode('ascii'))
tn.write(b"ez-edge#1\r\n")
print("4")
time.sleep(4)
tn.write(b"exit\r\n")
print("all I read" , tn.read_all().decode('ascii'))
