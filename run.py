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
    ExpectFound = False
    ExpectData = ""

# serial vars
ser = None
device = ""
baud = 115200
callbackFunc = None

error_count = 0

# command timeout vars
app_timeout = 0.0
timestamp = 0.0


delimeters = ["OK", ">", "ERROR"]
buffer = ""

def handler():

    # check to see if serial is already open if so close
    if (ser.isOpen()):
        ser.close()

    # open serial
    ser.open()

    # loop through each command
    for key in cfg["cfg"]:
        
        # pull command, expect and timeout from config
        cmd = key[0]
        rsp = key[1]
        cmd_to = float(key[2])

        # store the start time of the command
        cmd_ts = time.time()

        # send command to modem
        send(cmd)
        # reset the buffer
        buffer = ""
        # reset delimeter_found flag
        delimeter_found = False

        while(True):
            # calculate elapsed time
            elapsed = (time.time() - cmd_ts)

            # if the command times out break out of the loop
            if (elapsed > cmd_to):
                print("Error: Modem timeout waiting response.")
                break

            result = ModemData()

            # process the modem's response
            while(ser.in_waiting > 0):
                # read next line form serial port
                line = ser.readline().decode("utf-8")
                # accumulate a local buffer
                buffer += line

                # did we get a delimeter?
                delimeter_found = line_handler(buffer)

            if delimeter_found:
                # data = expect(buffer, rsp)
                # if data.ExpectFound:
                #     print("ExpectData: ", data.ExpectData)
                callbackFunc(buffer)
                print("elapsed: ", elapsed)
                print("--------------------------------------")
                break

            # let outer while loop breathe
            time.sleep(.1)

    # close the port
    if (ser.isOpen()):
        ser.close()

def line_handler(buffer):

    for x in delimeters:
        if (buffer.find(x) > -1):
            return True
    
    return False

def expect(result, parm):
    data = ModemData()

    if (result.find(parm) > -1):
        data.ExpectFound = True
        data.ExpectData = result

    return data


"""
Write command to device
"""
def send(cmd):
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




