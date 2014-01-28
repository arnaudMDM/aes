#!/bin/env python
# -*- coding: shift_jis -*-

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

# Import requred modules

from CipherModule import CipherModule
from utility import *

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
    cm = CipherModule()

    target_round = 8 #ターゲットのラウンドをここに入力
    
    # Period of glitch = 15
    cm.write_param(addr_list["DELAY"], 15)
    # Period of glitch = 30
    cm.write_param(addr_list["PERIOD"], 40)
    # Fine adjustment = 41
    cm.write_param(addr_list["POS_FINE"], 34 + target_round)
    # Enable glitch injection
    cm.write_param(addr_list["GLITCH_EN"], 1)

    key = [0x2b7e, 0x1516, 0x28ae, 0xd2a6, 0xabf7, 0x1588, 0x09cf, 0x4f3c]
    pt  = [0x3243, 0xf6a8, 0x885a, 0x308d, 0x3131, 0x98a2, 0xe037, 0x0734]

    print "key", hex_str(key)
    print "pt", hex_str(pt)
    
    #cm.select("AES_TBL")
    #cm.encdec(0x0000)

    cm.set_key(key)
    import time

    while True:
        for w in range(100, 20, -1):
            print "w =", w
            #最初の立ち上がりエッジと最初の立下りエッジとの間隔
            cm.write_param(addr_list["DELAY"], 10) 
            #最初の立ち上がりエッジと2番目の立ち上がりエッジとの間隔
            cm.write_param(addr_list["PERIOD"], w)
            ct = cm.encrypt(pt)
            print [hex(x) for x in ct]
            time.sleep(0.1)

    # Show result
    #print "result             = 0x" +  hex_str_noseg(res)
    # Show result
    #print "correct ciphertext = " + hex(ct_correct)

    
