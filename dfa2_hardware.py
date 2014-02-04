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

def flatten(tab):
    return [(tab[i][j] << 8) + tab[i + 1][j] for j in range(len(tab[0])) for i in range(0, len(tab), 2)]

def invFlatten(list):
    return [[(list[i + (j / 2)] >> (((j + 1) % 2) * 8)) % 256 for i in range(0, 8, 2)] for j in range(4)]

def aes_encrypt(_text, _key, typeFault = 0, indexBytes = 0):
    #Instantiate the cipher module
    cm = CipherModule("COM8")

    cm.set_key(flatten(copy.deepcopy(_key)))

    if typeFault == 2:
        target_round = 9

        # Period of glitch = 15
        cm.write_param(addr_list["DELAY"], 10)
        # Period of glitch = 30
        cm.write_param(addr_list["PERIOD"], 20)
        # Fine adjustment = 41
        cm.write_param(addr_list["POS_FINE"], 34 + target_round)
        # Enable glitch injection
        cm.write_param(addr_list["GLITCH_EN"], 1)
    else:
        cm.write_param(addr_list["GLITCH_EN"], 0)

    ct = cm.encrypt(flatten(copy.deepcopy(_text)))
    return invFlatten(ct)
    

if __name__ == "__main__":


    dfa2 = dfa2.DFA2(aes_encrypt)
    dfa2.execute()