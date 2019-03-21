import time
import threading
from serial import Serial
from multiprocessing import queues
import sys, getopt

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

# start_time = 0.0
# end_time = 0.0
device = ""
baud = 115200
callbackFunc = None
ser = None
timeout_max = 2.0
deviceid = []
finall = []
device = ""
script = ""
params = ""


def usage():
    print("-d/--device - device location")
    print("-s/--script - script location")
    print("-i/--deviceid - the devices id (separated by commas)")
    print("-p/--params - the params kore file location")

def handler(cmds):
    error_count = 0
    escape_loop = False
    # check to see if serial is already open if so close
    if (ser.isOpen()):
        ser.close()

    # open serial
    ser.open()

    for key in cmds["cfg"]:
        tmp_buffer = b""
        escape_loop = False
        # store the command and expected response for later use
        cmd = key[0]
        rsp = key[1]
        # log
        print("cmd: ", cmd, "rsp: ", rsp)

        # send command to modem
        send(cmd)
        # Reset start_time
        start_time = time.time()

        while(True):

            if (escape_loop == True):
                break
            
            # process timeout of command
            if ((time.time() - start_time) > timeout_max):
                print("timedout")
                break
    
            # process the modem's response
            while(ser.in_waiting > 0):
                # inefficient, but read one character at a time
                # TODO: refactor to read all bytes in serial buffer
                tmp_char = ser.read(1)
                print(tmp_buffer, " tmp_buffer")
                if(tmp_char == '\r'):
                    # parse the accumulated buffer
                    result = parse(tmp_buffer, rsp)
                    print ('received ', tmp_buffer)
                    # Check to see if we received what we were expecting
                    if(result.Success == True):
                        print("success")
                        if(callbackFunc != None):
                            callbackFunc(result)
                        # Escape time timeout loop
                        escape_loop = True
                        break
                    else:
                        error_count += 1
                        # print("error: cmd: ", cmd, " rsp: ", result.Data)
                    tmp_buffer= b""

                else:
                    tmp_buffer += tmp_char
                
            # let outer while loop breathe
            time.sleep(.005)

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
    # print('sending command: ', cmd)
    ser.write(cmd.encode())

def modemDataReceived(data):
    print('Callback function modemDataReceived ', data)

def parse_script():
    scriptdict = {"cfg" : []}
    scriptfile = open(script, "r")

    for line in scriptfile:
        line2 = line
        if line2.startswith("#"):
            continue
        elif line2.startswith(">"):
            line2 = line2.replace(">", "")
            if "{APN}" in line:
                line2 = line2.replace("{APN}", apn)
            elif "{DEVICEID}" in line:

                for id in deviceid:
                    line2 = line2.replace("{DEVICEID}", id)
                    # line2 = line2 + '\r\n'
                    line2 = line2.strip() + '\r'
                    scriptdict["cfg"].append([line2, "OK"])
                
                # for item in l:
                #     if item[0] == 1:
                #         finall.append([True, item[1], item[2]])
                #     else:
                #         finall.append([False, item[1], item[2]])
                continue
            elif "{SERVER}" in line and "{PORT}" in line:
                line2 = line2.replace("{SERVER}", server)
                line2 = line2.replace("{PORT}", port)
            
            line2 = line2.strip() + '\r'
            scriptdict["cfg"].append([line2, "OK"])
    
    scriptfile.close()
    return scriptdict

if __name__ == '__main__':

    print("running mdmcfg...")
    
    # TODO: pass following as args from terminal
    if not sys.argv[1:]:
        print("You didn't put any command line arguments. Please input some arguments!")
        sys.exit()
    args = sys.argv
    try:
        opts, args = getopt.getopt(args[1:], 'd:s:i:p:h', 
        ['device=', 'script=', 'deviceid=', 'params=', 'help'])
    except getopt.GetoptError:
        print("GetoptError")
        sys.exit(2)
    print("Parsing arguments.")
    for opt, arg in opts:
        if opt in ('-d', '--device'):
            device = arg
            print(device, " device")
        elif opt in ('-s', '--script'):
            script = arg
            print(script, " script")
        elif opt in ('-i', '--deviceid'):
            if "," in arg:
                deviceid = arg.split(",")
            else:
                deviceid.append(arg)
            
            print(deviceid, " deviceid")
        elif opt in ('-h', '--help'):
            usage()
        elif opt in ('-p', '--params'):
            params = arg
            print(params, " params")
        else:
            usage()

    if device == None or script == None or deviceid == None or params == None:
        print("Please pass the correct arguments")
        sys.exit(1)
    
    print("Parsing params file.")
    paramsfile = open(params, "r")
    for line in paramsfile:
        linesplit = line.split("=")
        if "baudrate" in line:
            baudrate = linesplit[1].rstrip()
            print(baudrate, " baud")
        elif "apn" in line:
            apn = linesplit[1].rstrip()
            print(apn, " apn")
        elif "server" in line:
            server = linesplit[1].rstrip()
            print(server, " server")
        elif "port" in line:
            port = linesplit[1]
            print(port, " port")
    
    print("Finished parsing the arguments and params file.")

    # device = "/dev/cu.UC-232AC"
    cfg = {"cfg": [["AT\r", "OK"], ["AT\r", "OK"]]}
    
    ser = Serial(device, baudrate=baudrate, parity='N', stopbits=1, bytesize=8, xonxoff=0, rtscts=0)
    
    callbackFunc = modemDataReceived

    scriptdict = parse_script()
    handler(scriptdict)

    ser.close()
    print("Exiting App...")
    
    exit()
