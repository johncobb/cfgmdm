import time
import datetime
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

class Modem(threading.Thread):

    def __init__(self, cfg, callback, device, baud, *args):
        self._target = self.handler
        self.cfg = cfg
        self.callbackFunc = callback
        self.ser = Serial(device, baudrate=baud, parity='N', stopbits=1, bytesize=8, xonxoff=0, rtscts=0)
        self.modemBusy = False
        self.errorCount = 0
        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)

    def handler(self):

        if (self.ser.isOpen()):
            self.ser.close()

        self.ser.open()

        for key in self.cfg["cfg"]:
            
            # store the command and expected response for later use
            cmd = key[0]
            rsp = key[1]
            # log
            print("cmd: ", cmd, "rsp: ", rsp)

            # send command to modem
            self.send(cmd)
        
            # process the modem's response
            while(self.ser.inWaiting() > 0):
                # inefficient, but read one character at a time
                # TODO: refactor to read all bytes in serial buffer
                tmp_char = self.ser.read(1)
                if(tmp_char == '\r'):
                    # parse the accumulated buffer
                    result = self.parse(tmp_buffer, rsp)
                    print ('received ', tmp_buffer)
                    # Check to see if we received what we were expecting
                    if(result.Success == True):
                        print("success")
                        if(self.callbackFunc != None):
                            self.callbackFunc(result)
                            self.modemBusy = False
                    else:
                        self.errorCount += 1
                        print("error: cmd: ", cmd, " rsp: ", result.Data)
                    #print 'modem response ', tmp_buffer
                    tmp_buffer= ""

                else:
                    tmp_buffer += tmp_char

            time.sleep(.005)

    def parse(self, result, expect):

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
    def send(self, cmd):
        print('sending command: ', cmd)
        self.ser.write(cmd)


def modemDataReceived(data):
    print('Callback function modemDataReceived ', data)


if __name__ == '__main__':

    print("running mdmcfg...")
    # TODO: pass following as args from terminal
    device = "/dev/tty.UC-232AC"
    baud = 115200
    config = {"cfg": [["AT", "OK"], ["AT", "OK"]]}

    modemThread = Modem(config, modemDataReceived, device, baud)
    modemThread.start()

    while(modemThread.isAlive()):
        time.sleep(.005)

    
    print("Exiting App...")
    exit()




