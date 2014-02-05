from CipherModule import CipherModule

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

def k9_CheckDiffPattern(self, tab):
    temp = []
    for i in range(4):
        temp.append([tab[i][COL - 1],i])
    temp = filter(lambda x: x[0] > 0, temp)
    if len(temp) == 2 and (temp[0][1] + temp[1][1]) % 2 == 1:
        return True
    else:
        return False

if __name__ == '__main__':

    text = [[0x32,0x88,0x31,0xe0],[0x43,0x5a,0x31,0x37],[0xf6,0x30,0x98,0x07],[0xa8,0x8d,0xa2,0x34]]
    key = [[0x2b,0x28,0xab,0x09],[0x7e,0xae,0xf7,0xcf],[0x15,0xd2,0x15,0x4f],[0x16,0xa6,0x88,0x3c]]

    #Instantiate the cipher module
    cm = CipherModule("COM8")

    cm.set_key(flatten(copy.deepcopy(_key)))

    cm.write_param(addr_list["GLITCH_EN"], 0)    
    correct = invFlatten(cm.encrypt(flatten(copy.deepcopy(_text))))

    cm.write_param(addr_list["GLITCH_EN"], 1)    
    target_round = 9
    cm.write_param(addr_list["POS_FINE"], 34 + target_round)

    result = []
    
    for i in range(100):
        cm.write_param(addr_list["DELAY"], i)
        for j in range(100):
            cm.write_param(addr_list["PERIOD"], j)
            fault = invFlatten(cm.encrypt(flatten(copy.deepcopy(_text))))
            diff = [[correct[i][j] ^ fault[i][j] for j in range(COL)] for i in range(RAW)]
            if self.k9_CheckDiffPattern(diff):
                result.append([i, j])

    for i in result:
        print result.index(i), ", delay: ", i[0], ", period: ", i[1]

