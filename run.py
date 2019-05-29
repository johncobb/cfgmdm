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

# serial vars
ser = None
device = ""
baud = 115200
callbackFunc = None

error_count = 0

# command timeout vars
timeout = 0.0
timestamp = 0.0

line_delimeter = "OK"

def is_timeout():
    if ((time.time() - timestamp) > timeout):
        print("timedout")

buffer = ""

def handler():

    # check to see if serial is already open if so close
    if (ser.isOpen()):
        ser.close()

    # open serial
    ser.open()

    for key in cfg["cfg"]:
        
        # pull command, expect and timeout from config
        cmd = key[0]
        rsp = key[1]
        timeout = key[2]

        # log current time
        timestamp = time.time()

        # send command to modem
        send(cmd)
        buffer = ""

        while(True):

            result = ModemData()

            # process the modem's response
            while(ser.in_waiting > 0):
                
                line = ser.readline().decode("utf-8")
                buffer += line
                #print(line)
                # result = parse(line, rsp)
                result = parse(line, line_delimeter)
                if(result.Success == True):
                    if(callbackFunc != None):
                        callbackFunc(buffer)
                        break
                    else:
                        error_count += 1
                        print("error: cmd: ", cmd, " rsp: ", result.Data)

            # found delimeter, break from outer loop
            # to handle next command
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


def modemDataReceived(buffer):
    print('Callback function modemDataReceived ', buffer)



if __name__ == '__main__':

    # TODO: pass following as args from terminal
    device = "/dev/tty.usbserial-FTASWORM"
    baud = 115200

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




