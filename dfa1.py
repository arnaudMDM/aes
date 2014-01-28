import random
from aes import aes,sbox
import copy

ITERATION = 5

random.seed()

def subytesPoint(point):
    point = sbox[point / 16][point % 16]
    return point

def unshiftRows(tab):
    for i in range(4):
        for j in range(i):
            tab[i].insert(0, tab[i].pop(3))
    return tab

byte = random.randrange(16)
text = [[0x32,0x88,0x31,0xe0],[0x43,0x5a,0x31,0x37],[0xf6,0x30,0x98,0x07],[0xa8,0x8d,0xa2,0x34]]
key = [[0x2b,0x28,0xab,0x09],[0x7e,0xae,0xf7,0xcf],[0x15,0xd2,0x15,0x4f],[0x16,0xa6,0x88,0x3c]]

d = []
for i in range(ITERATION):
    d.append(aes(copy.deepcopy(text), copy.deepcopy(key), 1, byte))
c = aes(text, key)

xor = [[[c[i][j] ^ d[l][i][j] for j in range(4)] for i in range(4)] for l in range(ITERATION)]

xor = filter(lambda x: x != 0, reduce(lambda a,b: a + b, reduce(lambda a,b: a + b, xor)))

possible = []
for k in range(ITERATION):
    possible.append([[],[]])
    for i in range(8):
        for j in range(256):
            correctM = j
            faultM = j ^ 2**i# ~(j & 2**i) & (j | 2**i)
            if (subytesPoint(correctM) ^ subytesPoint(faultM)) == xor[k]:
                possible[k][0].append(correctM)
                possible[k][1].append(faultM)

print byte
# print possible
# print xor

candidat = []
for i in range(len(possible[0][0])):
    for j in range(1,ITERATION):
        if possible[0][0][i] not in possible[j][0]:
            break
    else:
        candidat.append([possible[0][0][i],possible[0][1][i]])
# print xor
# print possible
print candidat
for i in candidat:
    print unshiftRows(c)[byte % 4][byte / 4] ^ subytesPoint(i[0])
print unshiftRows([i[40:] for i in key])[byte % 4][byte / 4]
# print key[3]
