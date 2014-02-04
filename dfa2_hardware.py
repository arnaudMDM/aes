import dfa2
from CipherModule import CipherModule
import copy

#The list of address
addr_list = {"DELAY"      : 0x0000,
         "PERIOD"     : 0x0001,
         "POSITION"   : 0x0002,
         "POS_FINE"   : 0x0003,
         "GLITCH_EN"  : 0x0004,
         "EXEC_TIME0" : 0x0005,
         "EXEC_TIME1" : 0x0006 }

def aes_encrypt(_text, _key, typeFault = 0, indexBytes = 0):
    #Instantiate the cipher module
    cm = CipherModule("COM8")

    cm.set_key(copy.deepCopy(_key))

    if typeFault == 2:
        target_round = 9
        
        # Period of glitch = 15
        cm.write_param(addr_list["DELAY"], 15)
        # Period of glitch = 30
        cm.write_param(addr_list["PERIOD"], 40)
        # Fine adjustment = 41
        cm.write_param(addr_list["POS_FINE"], 34 + target_round)
        # Enable glitch injection
        cm.write_param(addr_list["GLITCH_EN"], 0)

    cm.encrypt(copy.deepCopy(_text))
    

if __name__ == "__main__":


    dfa2 = dfa2.DFA2(aes_encrypt)
    dfa2.execute()