import time
import threading
from serial import Serial
from multiprocessing import queues

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
timeout_max = 1.0

def handler():
    error_count = 0
    escape_loop = False
    # check to see if serial is already open if so close
    if (ser.isOpen()):
        ser.close()

    # open serial
    ser.open()

    for key in cfg["cfg"]:
        tmp_buffer = ""
        escape_loop = False
        # store the command and expected response for later use
        cmd = key[0]
        rsp = key[1]
        # log
        print("cmd: ", cmd, "rsp: ", rsp)

        # send command to modem
        send(cmd)
        start_time = time.time()

        while(True):

            if (escape_loop == True):
                break
            
            # process timeout of command
            if ((time.time() - start_time) > timeout_max):
                print("timedout")
                break
    
            # process the modem's response
            while(ser.inWaiting() > 0):
                # inefficient, but read one character at a time
                # TODO: refactor to read all bytes in serial buffer
                tmp_char = ser.read(1)
                print(tmp_char, " tmp_char")
                if(tmp_char == '\r'):
                    # parse the accumulated buffer
                    result = parse(tmp_buffer, rsp)
                    print ('received ', tmp_buffer)
                    # Check to see if we received what we were expecting
                    if(result.Success == True):
                        print("success")
                        if(callbackFunc != None):
                            callbackFunc(result)
                        escape_loop = True
                        break
                    else:
                        error_count += 1
                        # print("error: cmd: ", cmd, " rsp: ", result.Data)
                    tmp_buffer= ""

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
    print('sending command: ', cmd)
    ser.write(cmd.encode())

def modemDataReceived(data):
    print('Callback function modemDataReceived ', data)


if __name__ == '__main__':


    print("running mdmcfg...")
    # TODO: pass following as args from terminal
    device = "/dev/tty.UC-232AC"
    baud = 115200
    cfg = {"cfg": [["AT\r", "OK"], ["AT\r", "OK"]]}
    ser = Serial(device, baudrate=baud, parity='N', stopbits=1, bytesize=8, xonxoff=0, rtscts=0)

    callbackFunc = modemDataReceived

    handler()


    print("Exiting App...")
    exit()




