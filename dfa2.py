from aes import aes

key = []
pt = []
correct = []

RAW = 4
COL = 4

def subytesPoint(tab):
    return tab

def findK9i(ckdk, ej):
    for j in range(256):
        sub1 = subytesPoint(j)
        sub2 = subytesPoint(j ^ ej)
        diff2 = sub1 ^ sub2
        if diff2 == ckdk:
            return sub1, sub2
    else:
        raise "error line 21"

def k9():
    result = [-1,-1,-1,-1]
    finish = [[],[],[]]
    while len(finish[2]) < RAW:
        fault = aes()
        diff = [[correct[i][j] ^ fault[i][j] for j in range(COL)] for i in range(RAW)]
        for i in range(RAW):
            if diff[i][COL] != 0 and diff[i][COL - 1] == 0:
                if i not in finish[0]:
                    finish[0].append(i)
                    ej = diff[finish[i]][COL]
                    ckdk = correct[i - 1][0] ^ fault[(i - 1) % 4][0]
                    sub1,sub2 = findK9i(ckdk, ej)
                    finish[1].append([ej,sub1,sub2])
                    break
                elif i not in finish[2]:
                    indice = finish[0].index(i):
                    ej = diff[finish[i]][COL]
                    if finish[1][indice][0] == ej:
                        break
                    ckdk = correct[i - 1][0] ^ fault[(i - 1) % 4][0]
                    sub1,sub2 = findK9i(ckdk, ej)
                    if sub1 in finish[1][indice][1:]:
                        result[i] = sub1
                    elif sub2 in finish[1][indice][1:]:
                        result[i] = sub2
                    else:
                        raise "error line 50"
                    finish[2].append(i)
                    break
        else:
            raise "error line 54"
    return result

def k8(correct):
    

