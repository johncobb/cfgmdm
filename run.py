import time
import threading
import json
from serial import Serial

class ModemResponse:
    OK = "OK"
    ERROR = "ERROR"
    CONNECT = "CONNECT"
    NOCARRIER = "NO CARRIER"
    PROMPT = ">"
    CMGS = "+CMGS:"
    CREG = "+CREG:"

class ModemData:
    Success = False
    Data = ModemResponse.OK

ser = None
device = ""
baud = 115200
callbackFunc = None

error_count = 0

timeout = 0.0
timestamp = 0.0

def is_timeout():
    if ((time.time() - timestamp) > timeout):
        print("timedout")


def handler():

    # check to see if serial is already open if so close
    if (ser.isOpen()):
        ser.close()

    # open serial
    ser.open()

    for key in cfg["cfg"]:
        
        # store the command and expected response for later use
        cmd = key[0]
        rsp = key[1]

        # log
        # print("cmd: ", cmd)
        # print("rsp: ", rsp)

        # log current time
        timestamp = time.time()
        # set timeout duration
        timeout = 1.0

        # send command to modem
        send(cmd)

        while(True):

            result = ModemData()

            # process the modem's response
            while(ser.in_waiting > 0):
                
                line = ser.readline().decode("utf-8")
                print(line)
                result = parse(line, rsp)

                if(result.Success == True):
                    print("success")
                    if(callbackFunc != None):
                        callbackFunc(result)
                        break
                    else:
                        error_count += 1
                        print("error: cmd: ", cmd, " rsp: ", result.Data)

            if(result.Success == True):
                break

            # let outer while loop breathe
            time.sleep(.2)

    # close the port
    if (ser.isOpen()):
        ser.close()

def parse(result, expect):

    data = ModemData()
    data.Data = result

    if (result.find(expect) > -1):
        data.Success = True
    else:
        data.Success = False
    
    return data

"""
Write command to device
"""
def send( cmd):
    print('sending command: ', cmd)
    ser.write(cmd.encode())


def modemDataReceived(data):
    print('Callback function modemDataReceived ', data.Data)



if __name__ == '__main__':



    
    # TODO: pass following as args from terminal
    device = "/dev/tty.usbserial-FTASWORM"
    baud = 115200
    cfg = {"cfg": [["ATE0\r", "OK"], ["AT+CPIN?\r", "+CPIN:"], ["AT+QSIMSTAT?\r", "+QSIMSTAT:"]]}
    print("\r\n\r\n")
    print("--------------------------------------")
    print(" BG96 Confiuration Utility")
    print(" - device: ", device)
    print(" - baud: ", baud)
    print("--------------------------------------")
    try:
        with open('quec.config.json') as json_file:
            cfg = json.load(json_file)

            ser = Serial(device, baudrate=baud, parity='N', stopbits=1, bytesize=8, xonxoff=0, rtscts=0)

            callbackFunc = modemDataReceived

            handler()
    except IOError as e:
        print("Oops: ", e)
    


    print("Exiting App...")
    exit()




