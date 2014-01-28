import copy
import random

random.seed()

sbox=[[0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76], [0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0], [0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15], [0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75], [0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84], [0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf], [0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8], [0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2], [0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73], [0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb], [0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79], [0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08], [0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a], [0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e], [0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf], [0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16]]

rcon = [[0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]] 

def hexTab(tab, nox = 0):
    if nox != 0:
        return str.join("", ("%02x" % j for i in tab for j in i))
    else: 
        return str.join("", (hex(j) for i in tab for j in i))


def subytesTab(tab):
    tab = [[sbox[tab[i][j] / 16][tab[i][j] % 16] for j in range(4)] for i in range(4)]
    return tab

def subytesVecHor(vec):
    vec = [sbox[vec[i] / 16][vec[i] % 16] for i in range(4)]
    return vec

def keySchedule(key):
    for i in range(0, 10):
        vec = subytesVecHor([key[1][(4 * i) + 3], key[2][(4 * i) + 3], key[3][(4 * i) + 3], key[0][(4 * i) + 3]])
        for l in range(4):
            key[l].append(vec[l] ^ key[l][4 * i] ^ rcon[l][i])
        for j in range(1, 4):
            for l in range(4):
                key[l].append(key[l][(4 * i) + 3 + j] ^ key[l][4 * i + j])
    return key

def shiftRows(tab):
    for i in range(4):
        for j in range(i):
            tab[i].append(tab[i].pop(0))
    return tab

def mixColumnsVecVert(vec):
    result = [-1, -1, -1, -1]
    vec2 = [-1, -1, -1, -1]
    for j in range(4):
        h = vec[j] & 0x80 #hight bit
        vec2[j] = vec[j] << 1
        if h == 0x80: #hight bit
            vec2[j] ^= 0x11b #rijnadel's galois field
    result[0] = vec2[0] ^ vec[3] ^ vec[2] ^ vec2[1] ^ vec[1]
    result[1] = vec2[1] ^ vec[0] ^ vec[3] ^ vec2[2] ^ vec[2]
    result[2] = vec2[2] ^ vec[1] ^ vec[0] ^ vec2[3] ^ vec[3]
    result[3] = vec2[3] ^ vec[2] ^ vec[1] ^ vec2[0] ^ vec[0]
    return result

def mixColumns(tab):
    result = []
    tab = zip(*tab)
    for i in range(4):
        result.append(mixColumnsVecVert(tab[i]))
    return map(list, zip(*result))

def convertStrInTab(str):
    if len(str) != 32:
        raise Exception('length','not egal')
    result = [[int(str[i + j]+str[ i + j + 1], 16) for i in range(0, 32, 8)] for j in range(0, 8, 2)]
    return result

def convertTabInStrHex(tab):
    return hexTab(zip(*tab), 1)

def addRoundKey(tab,key,iteration):
    for i in range(4):
        for j in range(4):
            tab[i][j] ^= key[i][j + 4 * iteration]
    return tab

def convertLst8x1x16Lst4x4x8(liste):
    return convertStrInTab(str.join("", ("%04x" % i for i in liste)))

def convertLst4x4x8Lst8x1x16(liste):
    result = [liste[i][j] + liste[i][j + 1]  for i in range(4) for j in range(0, 4, 2)]
    return result

def aes(text, key, typeFault = 0, indexBytes = 0):
    """
    typeFault = 0 means no Fault
    typeFault = 1 means one bit of indexBytes byte is changed randomly before the final round
    """
    # text = convertStrInTab(raw_input('what is the text to encrypt in hexadecimal: '))
    # key = convertStrInTab(raw_input('what is the 128 bits first key: '))
    #print 'plain text: ', hexTab(text)
    #print '128 bits of the key: ', hexTab(key)

    key = keySchedule(key)
    #print 'key after schedule: ', hexTab(key)

    #initial round
    #print 'initial round'
    addRoundKey(text, key, 0)
    #print 'cypher text after addRoundKey: ', hexTab(text)
    #round 1 to 9
    for i in range(1,10):
        #print 'round ', i
        text = subytesTab(text)
        #print 'cypher text after subytes: ', hexTab(text) 
        text = shiftRows(text)
        #print 'cypher text after shiftRows: ', hexTab(text)
        text = mixColumns(text)
        #print 'cypher text after mixColumns: ', hexTab(text)
        text = addRoundKey(text, key, i)
        #print 'cypher text after addRoundKey: ', hexTab(text)
    #round 10
    #print 'final round'

    if typeFault == 1:
        bit = random.randrange(8)
        text[indexBytes % 4][indexBytes / 4] = text[indexBytes % 4][indexBytes / 4] ^ 2**bit# ~(text[indexBytes % 4][indexBytes / 4] & 2**bit) & (text[indexBytes % 4][indexBytes / 4] | 2**bit)

    text = subytesTab(text)
    #print 'cypher text after subytes: ', hexTab(text) 
    text = shiftRows(text)
    #print 'cypher text after shiftRows: ', hexTab(text)
    text = addRoundKey(text, key, 10)
    #print 'cypher text after addRoundKey: ', hexTab(text)
    return text

if __name__ == "__main__":
    assert convertTabInStrHex(aes(convertStrInTab("3243f6a8885a308d313198a2e0370734"), convertStrInTab("2b7e151628aed2a6abf7158809cf4f3c"))) == "3925841d02dc09fbdc118597196a0b32"
    print "OK"
