import sys, getopt, os, glob
import time
import threading
import json
from serial import Serial

device = "/dev/tty.usbserial-FTASWORM"
baud = 115200
config = ""

### arg parsing from command line ###
arg_device_found = False
arg_baud_found = False
arg_config_found = False

def usageFunc():
    global d, b, c
    print("{0}\n{1}\n{2}\n".format(d,b,c))

usageDict = {
    "d": " -d, --device, is the serial device path",
    "b": " -b, --baud, is the serial baud rate",
    "c": " -c, --config, is the path to config file",
    "h": usageFunc
}

d = usageDict['d']
b = usageDict['b']
c = usageDict['c']

def argParse(opts, args):

    global device, baud, config
    for opt, arg in opts:
        optc = opt.lower()
        if optc in ['--help', '-h']:
            usageDict['h']()
            sys.exit()
        elif optc in ["--device", "-d"]:
            arg_device_found = True
            device = arg
        elif optc in ["--baud", "-b"]:
            arg_baud_found = True
            baud = arg
        elif optc in ["--config", "-c"]:
            arg_config_found = True
            config = arg
        elif optc in ['--gen', '-g']:
            pass
        
    if not arg_device_found:
        print("Error: --device is a required argument.")
        sys.exit()
    if not arg_baud_found:
        print("Error: --baud is a required argument.")
        sys.exit()
### end args handling ###

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

def greeting():
    print("\r\n")
    print("--------------------------------------")
    print(" BG96 Confiuration Utility")

def footer():
    print("--------------------------------------")


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
                footer()
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

    if not sys.argv[1:]:
        greeting()
        print(" Error: The following arguments are required.")
        usageDict['h']()
        footer()
        sys.exit()

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:b:c:h', ['device=', 'baud=', 'config=', 'help'])
    except getopt.GetoptError:
        print("Error: invalid argument.")
        sys.exit(2)

    if not opts and not args:
        print("Error: No parameters provided.")
        usageDict['h']
        sys.exit()

    argParse(opts, args)


    # TODO: pass following as args from terminal
    # device = "/dev/tty.usbserial-FTASWORM"
    # baud = 115200

    greeting()
    print(" - device: ", device)
    print(" - baud: ", baud)
    print(" - config: ", config)
    footer()
    
    try:
        with open(config) as json_file:
            cfg = json.load(json_file)

            ser = Serial(device, baudrate=baud, parity='N', stopbits=1, bytesize=8, xonxoff=0, rtscts=0)
            callbackFunc = modemDataReceived

            handler()
    except IOError as e:
        print("Oops: ", e)
    
    print("Exiting App...")
    exit()




