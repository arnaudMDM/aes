#!/bin/env python
# -*- coding: utf-8 -*-

"""
-------------------------------------------------------------------------
 Sample program of AES encryption with glitchy-clock
 
 File name   : sample.py
 Version     : Version 1.1
 Created     : APR/28/2011
 Last update : Dec/25/2013
 Designed by : Sho Endo
 
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

"""
聰ﾘﾅ室芝漆芝疾聰ﾔﾄ自聰ﾔﾅ而屡ﾃﾕ屡ﾃ｡屡ﾃ､屡ﾄ蒹猗ﾄ湿聰ﾔﾅ鴫聰ﾔﾅ､芬ﾂ識聰ﾔﾅ自聰ﾔﾄ漆聰ﾔﾅﾞ芬ﾃｸﾄﾀﾅﾚ芬ﾃ耳
"""


import os
import datetime
now_time = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
os.mkdir('results/' + now_time)
dir_name = 'results/' + now_time + '/'

    
#from Control.CipherModule import CipherModule
#from pyAES.myAES import AES
#from pyAES.myAES import AES_unroll
from utility import *
import random, time, datetime, visa


"""
屡ﾃｪ屡ﾃｷ屡ﾄﾄｺﾈﾃｹ屡ﾃｳ篠｡ｼ屡ﾃﾗ聰ﾔﾅｸﾄｾ芬ﾅ室篠ﾀﾅﾚ芬ﾃ耳
"""
gpibAddress = "USB0::0x0957::0x17A2::MY53100122"
    
print visa.get_instruments_list()
oscillo = visa.instrument(gpibAddress)
#oscillo.timeout = 5
#oscillo.chunk_size = 10 * 1024 * 1024
    
scan = [
    ":TIMebase:REFerence",
    ":TIMebase:SCALe",
    ":TIMebase:POSition",
    ":CHANnel1:IMPedance",
    ":CHANnel1:SCALe",
    ":CHANnel1:OFFSet",
    ":CHANnel1:BWLimit",
    ":CHANnel1:DISPlay",
    ":CHANnel2:IMPedance",
    ":CHANnel2:SCALe",
    ":CHANnel2:OFFSet",
    ":CHANnel2:BWLimit",
    ":CHANnel2:DISPlay",
    ":CHANnel3:IMPedance",
    ":CHANnel3:SCALe",
    ":CHANnel3:OFFSet",
    ":CHANnel3:BWLimit",
    ":CHANnel3:DISPlay",
    ":CHANnel4:IMPedance",
    ":CHANnel4:SCALe",
    ":CHANnel4:OFFSet",
    ":CHANnel4:BWLimit",
    ":CHANnel4:DISPlay",
    ":TRIGger:MODE",
    ":TRIGger:EDGE:SOURce",
    ":TRIGger:EDGE:SLOPe",
    ":TRIGger:EDGE:LEVel",
    ":TRIGger:SWEep",
]

prop = {}

for command in scan:
    oscillo.write(command + "?")
    prop.update({command:oscillo.read()})

prop.update({
    ":ACQuire:MODE":"RTIMe",
    ":ACQuire:TYPE":"NORMal",
    ":WAVeform:FORMat":"BYTE",
    ":WAVeform:UNSigned":"1",
    ":WAVeform:POINts":"MAX"
})

oscillo.write("*RST")
oscillo.write("*CLS")


f = open(dir_name + "proparty.txt", "a+")

for key, value in sorted(prop.items()):
    command = key + " " + value
    oscillo.write(command)
    print(command)
    f.write(command + "\n")

print("")
f.close()


oscillo.write(":STOP")
oscillo.write(":RUN")

wait_time = 3
print("Plese wait %d second(s)" % wait_time)
for i in range(wait_time, 0, -1):
    print("%d.." % i)
    time.sleep(1)

oscillo.write(":WAVeform:SOURce CHANnel3")
"""
屡ﾃｪ屡ﾃｷ屡ﾄﾄｺﾈﾃｹ屡ﾃｳ篠｡ｼ屡ﾃﾗ聰ﾔﾅｸﾄｾ芬ﾅ室篠ﾀﾅﾚ芬ﾃ耳聰ﾔﾄ竺聰ﾔﾄ竺聰ﾔﾅﾘ芬ﾃ
"""

import random

def random_pt_gen():
    buf = []
    for i in range(8):
        buf.append(random.randrange(0xffff)) #屡ﾄ芬ﾆﾄ芬ﾆﾃﾀ屡ﾄ荀ｮ聰ﾔﾅｰ芬ﾂ漆聰爾篠叱
    return buf    

def lst82str(lst):
    s = ""
    for i in range(8):
        s += ("%04x" % lst[i])
    return s

def lst82lst16(lst):
    result = []
    for i in lst:
        result.append(i >> 8)
        result.append(i % 256)
    return result

# Import requred modules

from CipherModule import CipherModule
from utility import *
from aes import *
from DFA import *

#The list of address
addr_list = {"DELAY"      : 0x0000,
	     "PERIOD"     : 0x0001,
	     "POSITION"   : 0x0002,
	     "POS_FINE"   : 0x0003,
	     "GLITCH_EN"  : 0x0004,
	     "EXEC_TIME0" : 0x0005,
	     "EXEC_TIME1" : 0x0006 }

# Main program
if __name__ == '__main__':
    
    #Instantiate the cipher module
    cm = CipherModule("COM8")

    target_round = 8 #屡ﾃｿ篠｡ｼ屡ﾃｲ屡ﾃﾃ屡ﾃﾈ聰ﾔﾅｸﾈﾄ芬ﾆﾃｦ屡ﾄ芬ﾆﾃﾉ聰ﾔﾅ鴫聰ﾔﾄ竺聰ﾔﾄ竺聰ﾔﾅｲ芬ﾃ湿聰ﾈﾅ
    
    # Period of glitch = 15
    cm.write_param(addr_list["DELAY"], 15)
    # Period of glitch = 30
    cm.write_param(addr_list["PERIOD"], 40)
    # Fine adjustment = 41
    cm.write_param(addr_list["POS_FINE"], 34 + target_round)
    # Enable glitch injection
    cm.write_param(addr_list["GLITCH_EN"], 0)

    key = [0x0001, 0x0203, 0x0405, 0x0607, 0x0809, 0x0a0b, 0x0c0d, 0x0e0f]
    #key = [0x2b7e, 0x1516, 0x28ae, 0xd2a6, 0xabf7, 0x1588, 0x09cf, 0x4f3c]
    pt  = [0x3243, 0xf6a8, 0x885a, 0x308d, 0x3131, 0x98a2, 0xe037, 0x0734]

    print "key", hex_str(key)
    print "pt", hex_str(pt)
    
    #cm.select("AES_TBL")
    #cm.encdec(0x0000)

    cm.set_key(key)
    import time

    counter = 0

    while True:
        for w in range(100, 20, -1):
            pt = random_pt_gen()
            
            pc_ct = convertLst4x4x8Lst8x1x16(aes(convertLst8x1x16Lst4x4x8(pt),convertLst8x1x16Lst4x4x8(key)))

            #oscillo.write(":RUN")
            oscillo.write(":SINGle")
            time.sleep(0.1)

            print "w =", w
            #篠ｺﾅｾ蒹獪ﾅｸ芬ﾂ而聰ﾔﾄ質篠ｾﾅ璽聰ﾔﾄ蒔聰ﾔﾅ耳屡ﾃｨ屡ﾃﾃ屡ﾃｸ聰ﾔﾅｺﾅｾ蒹獪ﾅｸ芬ﾂ而聰鴫篠室聰ﾔﾅ耳屡ﾃｨ屡ﾃﾃ屡ﾃｸ聰ﾔﾅ偲ｸﾇﾈﾇ
            cm.write_param(addr_list["DELAY"], 10) 
            #篠ｺﾅｾ蒹獪ﾅｸ芬ﾂ而聰ﾔﾄ質篠ｾﾅ璽聰ﾔﾄ蒔聰ﾔﾅ耳屡ﾃｨ屡ﾃﾃ屡ﾃｸ聰ﾔﾅ聰ﾚﾅﾈ芬ﾃﾔ芬ﾃｸ芬ﾂ而聰ﾔﾄ質篠ｾﾅ璽聰ﾔﾄ蒔聰ﾔﾅ耳屡ﾃｨ屡ﾃﾃ屡ﾃｸ聰ﾔﾅ偲ｸﾇﾈﾇ
            cm.write_param(addr_list["PERIOD"], w)
            ct = cm.encrypt(pt)
            print [hex(x) for x in ct]

            oscillo.write(":WAVeform:DATA?")
            wave = oscillo.read()
            wave = wave[10:]
            wave = [ord(i) for i in wave]
            wave = ", ".join(map(str, wave))

            if pc_ct == ct:
                print 'cipher OK'
                f = open(dir_name + ("c_voltage_wave.csv"), "a+")
                f.write(("#%d#, " % counter) + wave + "\n")
                f.close()
            else:
                print 'cipher failed'
                f = open(dir_name + ("i_voltage_wave.csv"), "a+")
                f.write(("#%d#, " % counter) + wave + "\n")
                f.close()
                fault = injected_round(lst82lst16(ct), lst82lst16(pc_ct), lst82lst16(key))
                f = open(dir_name + ("fault_check.txt"), "a+")
                f.write(("#%d#, " % counter) + ("%d round, " % fault[0]) + ("%d bytes" % fault[1]) + "\n")
                f.write("pt : " + lst82str(pt) + "\n")
                f.write("ct : " + lst82str(ct) + "\n")
                f.write("pc_ct : " + lst82str(pc_ct) + "\n")
                f.close()
            counter += 1
    # Show result
    #print "result             = 0x" +  hex_str_noseg(res)
    # Show result
    #print "correct ciphertext = " + hex(ct_correct)

    
