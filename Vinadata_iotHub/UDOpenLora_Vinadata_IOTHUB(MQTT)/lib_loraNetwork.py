#  python3 "/home/pi/mqtt_firebase/lib_loraNetwork.py"


import const as CONST

from threading import Thread
import _thread
import time
import serial
import sys
import random
import sys
sys.path[0:0] = [""]
import os
import os.path

import time
import paho.mqtt.client as paho
import ssl

#define callbacks
def on_message(client, userdata, message):
  print("received message =",str(message.payload.decode("utf-8")))

def on_log(client, userdata, level, buf):
  print("log: ",buf)

def on_connect(client, userdata, flags, rc):
 
  #client.subscribe(topic = "b118a39fd82b4916b3c217ffd2ce6f60:topic/sdcdevice5")
 # client.subscribe(topic= "b118a39fd82b4916b3c217ffd2ce6f60:topic/sdcdevice5/c1")
  print("publishing")
  #client.publish(topic = "b118a39fd82b4916b3c217ffd2ce6f60:topic/sdcdevice5", payload = "{\"data\": {\"c1\":8,\"c2\":ON}}") #  topic = <hubid>:tocpic/<mytopic>
  #client.loop_start()
  #client.publish("b118a39fd82b4916b3c217ffd2ce6f60:topic/sdcdevice5/c1","12")
  
  
   #client.subscribe(topic= "b118a39fd82b4916b3c217ffd2ce6f60:topic/sdcdevice5", qos=0)
client=paho.Client("b118a39fd82b4916b3c217ffd2ce6f60:client/sdcdevice5") # add client name / client id = <hubid:client>/<myclient> , client id defind in policy iot

client.tls_set(ca_certs = '/home/pi/cuong/ca.crt', certfile = '/home/pi/cuong/972aa862-40a6-11e9-af61-0a580a6403b5.crt', keyfile =  '/home/pi/cuong/972aa862-40a6-11e9-af61-0a580a6403b5.key',cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
client.on_message=on_message
client.on_log=on_log
client.on_connect=on_connect
client.tls_insecure_set(True)



# set pin of lora module
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
PinM0 = 27
PinM1 = 17
AUXPin = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(PinM0, GPIO.OUT)
GPIO.setup(PinM1, GPIO.OUT)
GPIO.setup(AUXPin, GPIO.IN)
GPIO.output(PinM0, 0)    # M0 M1 = LOW 
GPIO.output(PinM1, 0)
# set pin of lora module



lora_chanel = CONST.Str_HUB_lora_chanel
endMessSymbol = CONST.Str_endMessSymbol
HUB_LORA_ID = CONST.Str_HUB_LORA_ID

enable_add_device = False

pingQueue = list()

loraSerial = serial.Serial(  
   port='/dev/ttyS0',
   baudrate = 9600,
   parity=serial.PARITY_NONE,
   stopbits=serial.STOPBITS_ONE,
   bytesize=serial.EIGHTBITS,
   timeout=1
)



def parse_json_object(data, obj):
    prefix = "\"%s\":\"" % obj
    prefix2 = '\'%s\':' % obj
    data.find(prefix)
    if (data.find(prefix) != -1):        
        index_prefix = data.find(prefix)
        index1 = data.find('\"', (len(prefix) + index_prefix - 1)) + 1
        index2 = data.find('\"', index1)
        dataOUT = data[index1:index2]
        return dataOUT
    elif (data.find(prefix2) != -1):        
        index_prefix = data.find(prefix2)
        index1 = data.find('\'', (len(prefix2) + index_prefix - 1)) + 1
        index2 = data.find('\'', index1)
        dataOUT = data[index1:index2]
        return dataOUT
    else:
        return ''
        
        

def send_lora_mess(AH, AL, chan, mess):
    ADDR_H = AH
    ADDR_L = AL
    Lora_chanel = chan
    SendBuf =  ADDR_H + ADDR_L + Lora_chanel + HUB_LORA_ID + mess +  endMessSymbol
    print("SendBuf: %s\n" % SendBuf)    
    loraSerial.write(SendBuf.encode(encoding = 'cp855', errors='strict'))
    return;
 
    
def receive_Lora_Message(buf):
    try:  
        LORA_Mess = buf
        #print("Mess from : 0x%.2X%.2X\n" % LORA_Mess[0], LORA_Mess[1])
        #firebaseFunction.debugFirebase(LORA_Mess[0:2], LORA_Mess[2:])    
        print("LORA_Mess : %s\n" % LORA_Mess[2:])
        T1=parse_json_object(LORA_Mess, 'T')
        H1=parse_json_object(LORA_Mess, 'H')
        T_1=int(T1)/10
        H_1=int(H1)/10
        print("All_mess_1: %s\n" %T_1)
        print("All_mess_1: %s\n" %H_1)
        client.publish(topic = "b118a39fd82b4916b3c217ffd2ce6f60:topic/sdcdevice5", payload = ("{\"data\": {\"c1\":%s,\"c2\":%s}}" %(T_1,H_1))) #  topic = <hubid>:tocpic/<mytopic>
        return;
    except:
        print("error when receive_Lora_Message(buf)")



def check_lora_mess_receive_Loop():
    while True:      
        if(loraSerial.inWaiting() > 0):
            lora_mess = bytes()
            char = bytes()
            while True:
                char = loraSerial.read()
                lora_mess = lora_mess + char
                if (char == bytes.fromhex(CONST.endMessSymbol)):   
                    break      
            message = (lora_mess).decode(encoding = 'cp855', errors='strict')
            receive_Lora_Message(message)            
        time.sleep(0.1)


def loraNetwork_begin():
    try:
        _thread.start_new_thread(check_lora_mess_receive_Loop, ())
    except:
        print ("Error: unable to start thread")


print("connecting to broker")

client.connect("iot-s9.vinadata.vn",8883, 60)

##start loop to process received messages
client.loop_start()
print("1")
#wait to allow publish and logging and exit
time.sleep(1)


loraNetwork_begin()
while 1:
    pass
#firebase.firebase_admin_begin()