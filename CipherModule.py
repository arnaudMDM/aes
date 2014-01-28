#!/bin/env python
"""
-------------------------------------------------------------------------
 Cipher module
 
 File name   : CipherModuleMashRSA.py
 Version     : Version 1.2
 Created     : JUL/2/2010
 Last update : JUN/10/2013
 Designed by : Takeshi Sugawara
 Modified by : Sho Endo
 
-----------------------------------------------------------------
 Copyright (C) 2010 - 2013 Tohoku University
 
 By using this code, you agree to the following terms and conditions.
 
 This code is copyrighted by Tohoku University ("us").
 
 Permission is hereby granted to copy, reproduce, redistribute or
 otherwise use this code as long as: there is no monetary profit gained
 specifically from the use or reproduction of this code, it is not sold,
 rented, traded or otherwise marketed, and this copyright notice is
 included prominently in any copy made.
 
 We shall not be liable for any damages, including without limitation
 direct, indirect, incidental, special or consequential damages arising
 from the use of this code.
 
 When you publish any results arising from the use of this code, we will
 appreciate it if you can cite our webpage
 (http://www.rcis.aist.go.jp/special/SASEBO/).
-------------------------------------------------------------------------
"""

import random
import copy
import time
from utility import *

random.seed()

rev1_cipher_list = {"AES_Comp"     : 0x0001,
                    "AES_Comp_ENC" : 0x0002,
                    "AES_TBL"      : 0x0004,
                    "AES_PPRM1"    : 0x0008,
                    "AES_PPRM3"    : 0x0010,
                    "DES"          : 0x0020,
                    "MISTY1"       : 0x0040,
                    "Camellia"     : 0x0080,
                    "SEED"         : 0x0100,
                    "CAST128"      : 0x0200,
                    "RSA"          : 0x0400,
                    "AES_SSS1"     : 0x0800,
                    "AES_S"        : 0x1000 }

rev1_addr_list = { "ADDR_CONT"    : 0x0002,
                   "ADDR_IPSEL"   : 0x0004,
                   "ADDR_OUTSEL"  : 0x0008,
                   "ADDR_ENCDEC"  : 0x000C,
                   "ADDR_RSEL"    : 0x000E,
                   "ADDR_KEY0"    : 0x0100,
                   "ADDR_ITEXT0"  : 0x0140,
                   "ADDR_OTEXT0"  : 0x0180,
                   "ADDR_RDATA0"  : 0x01C0,
                   "ADDR_EXP00"   : 0x0200,
                   "ADDR_MOD00"   : 0x0300,
                   "ADDR_IDATA00" : 0x0400,
                   "ADDR_ODATA00" : 0x0500,
                   "ADDR_VERSION" : 0xFFFC }

addr_list = {"DELAY"      : 0x0000,
         "PERIOD"     : 0x0001,
         "POSITION"   : 0x0002,
         "POS_FINE"   : 0x0003,
         "GLITCH_EN"  : 0x0004,
         "EXEC_TIME0" : 0x0005,
         "EXEC_TIME1" : 0x0006 }

class LocalBus(object):
    def __init__(self, interface="USB"):
        # Switching between USB and RS232C interfaces
        if interface == "USB":
            import d2xx
            self.ctrlif = d2xx.open(0)
            # setTimeouts(Read timeout, write timeout)
            self.ctrlif.setTimeouts(5000, 5000) 
        else:
            # Here, interface is expected to be like "COM1"
            # In this case, port number for pySecial should be 0
            import serial
            portNum = int(interface[3:]) - 1
            try:
                # Default baud rate is 19200.
                self.ctrlif = serial.Serial(port=portNum, baudrate=115200,timeout=1)
            except serial.serialutil.SerialException:
                import sys
                sys.exit("Cannot open port: " + interface)
        self.cipher_list = rev1_cipher_list
        self.addr_list = rev1_addr_list

    def __del__(self):
        if self.ctrlif:
            self.ctrlif.close()

    def reset_cipher(self):
        # Command for reset (supported by Glitcher)
        self.ctrlif.write(chr(0x04)) 

    def write(self, addr, dat):
        buf = []
        buf.append(0x01) # Magic number of writing
        buf.append( addr / 256)
        buf.append( addr % 256)
        buf.append( dat / 256)
        buf.append( dat % 256)
        self.ctrlif.write(bytelistToStr(buf))

    def write_burst(self, addr, dat):
        buf = []
        counter = 0
        for chunk in dat: # chunk is a 16-bit (positive) integer
            buf.append(0x01) # Magic number of writing
            buf.append( (addr + counter) / 256)
            buf.append( (addr + counter) % 256)
            buf.append( chunk / 256)
            buf.append( chunk % 256)
            counter += 2
        self.ctrlif.write(bytelistToStr(buf))

    def read(self, addr):
        buf = []
        buf.append(0x00) # Magic number for reading
        buf.append(addr / 256)
        buf.append(addr % 256)
        self.ctrlif.write(bytelistToStr(buf))
        
        tmp = self.ctrlif.read(2)
        # print "%.4x" % binstr_to_uint16(tmp)
        return binstr_to_uint16(tmp)

    def read_burst(self, addr, len=2):
        buf = []
        for offset in range(0, len, 2):
            buf.append(0x00)
            buf.append( (addr+offset) / 256 )
            buf.append( (addr+offset) % 256 )
        self.ctrlif.write(bytelistToStr(buf))
        tmp = self.ctrlif.read(len)
        return strToUint16List(tmp)
        

class CipherModule(LocalBus):
    def __init__(self, interface="USB"):
        super(CipherModule, self).__init__(interface)
        
    def select(self, cipher):
        version = self.read(self.addr_list["ADDR_VERSION"])
        #print "SASEBO version:", version
        # Select input
        self.write(self.addr_list["ADDR_IPSEL"], self.cipher_list[cipher])
        # Reset
        self.write(self.addr_list["ADDR_CONT"], 0x0004)
        self.write(self.addr_list["ADDR_CONT"], 0x0000)
        # Select output
        self.write(self.addr_list["ADDR_OUTSEL"], self.cipher_list[cipher])

    def encdec(self, dat):
        self.write(self.addr_list["ADDR_ENCDEC"], dat)

    def set_key(self, key_list):
        self.key = key_list # Store the key
        self.write_burst(self.addr_list["ADDR_KEY0"], key_list)
        # Execute key generation
        self.write(self.addr_list["ADDR_CONT"], 0x0002)
        # Wait for key schedule
        for i in range(10):
            cont = self.read(self.addr_list["ADDR_CONT"])
            if cont & 0x0002 == 0x0000:
                #print "key scheduling was done."
                return
            else:
                print cont
                #time.sleep(0.1) # wait for 0.1 sec
        #raise "Error in key scheduling: never return"
        # Error handling
        # print "Error in key scheduling"
        return "Error in key scheduling"
        
    
    def encrypt(self, dat):
        self.write_burst(self.addr_list["ADDR_ITEXT0"], dat)
        self.write(self.addr_list["ADDR_CONT"], 0x0001) # kick the cipher
        return self.read_burst(self.addr_list["ADDR_OTEXT0"], 16)

    def encrypt_again(self):
        self.write(self.addr_list["ADDR_CONT"], 0x0001) # kick the cipher
        return self.read_burst(self.addr_list["ADDR_OTEXT0"], 16)

    def read_key(self):
        return self.read_burst(self.addr_list["ADDR_KEY0"], 16)

    def read_otext(self):
        return self.read_burst(self.addr_list["ADDR_OTEXT0"], 16)

    def read_rdata(self):
        return self.read_burst(self.addr_list["ADDR_RDATA0"], 16)    

    def set_rsel(self, dat=0x8000):
        self.write(self.addr_list["ADDR_RSEL"],dat)
        #print self.read(self.addr_list["ADDR_RSEL"])

    def read_rsel(self):
        print self.read(self.addr_list["ADDR_RSEL"])

    def set_ipsel(self, dat=0x8000):
        self.write(self.addr_list["ADDR_IPSEL"], dat)
        return self.read(self.addr_list["ADDR_IPSEL"])

    def read_param(self, addr):
        """
        Read parameters from the FPGA
        read_param(addr)
        """
        buf = []
        buf.append(0x02) # Magic number for reading
        buf.append(addr / 256)
        buf.append(addr % 256)
        self.ctrlif.write(bytelistToStr(buf))
        
        tmp = self.ctrlif.read(2)
        #print "%.4x" % binstr_to_uint16(tmp)
        return binstr_to_uint16(tmp)

    def write_param(self, addr, dat):
        """
        Write parameters to the FPGA
        write_param(addr, dat)
        dat: array of uint16
        """
        buf = []
        buf.append(0x03) # Magic number of setting parameter
        buf.append( addr / 256)
        buf.append( addr % 256)
        buf.append( dat / 256)
        buf.append( dat % 256)
        self.ctrlif.write(bytelistToStr(buf))
        #print addr, dat

    def glitch_switch(self, glitch_on, trigger_on):
        self.write_param(4, glitch_on)

    def configure_delay_lines(self, critical_delay, tw):
        #delay = int((tw << 8) + critical_delay)
        delay = int(tw + (critical_delay << 8))
        #print delay
        self.write(0x0600, delay)

if __name__ == '__main__':
    key = [0x2b7e, 0x1516, 0x28ae, 0xd2a6, 0xabf7, 0x1588, 0x09cf, 0x4f3c]
    original  = [0x3243, 0xf6a8, 0x885a, 0x308d, 0x3131, 0x98a2, 0xe037, 0x0734]
    cm = CipherModule("COM8")

    print "key", hex_str(key)
    # print "pt", hex_str(pt)
    
    cm.select("AES_TBL")
    cm.encdec(0x0000)

    cm.set_key(key)

    target_round = 1
    
    # Period of glitch = 15
    cm.write_param(addr_list["DELAY"], 15)
    # Period of glitch = 30
    cm.write_param(addr_list["PERIOD"], 30)
    # Fine adjustment = 41
    cm.write_param(addr_list["POS_FINE"], 34 + target_round)
    # Enable glitch injection
    cm.write_param(addr_list["GLITCH_EN"], 1)


    fault = []
    MAX = 1000
    for i in range(MAX):
        # pt = [random.randrange(2**16) for j in range(8)]
        pt = copy.deepcopy(original)
        result = hex_str(cm.encrypt(pt))
        print float(i)/MAX*100.0
        # del cm

        from aes_v001_wrapper import AES_wrapper
        aobj = AES_wrapper()
        recalc = hex_str(aobj.encrypt(pt, key, AES_wrapper.keySize["SIZE_128"]))
        # print "Recalc:", recalc
        if recalc != result:
            fault.append(result)
            fault.append(recalc)
    for i in range(0, len(fault), 2):
        print i/2
        print "correct : ", fault[i + 1]
        print "incorrect : ", fault[i]
        print ""
    print "nb glitches : ", len(fault) / 2, "\n"
    del cm


    
