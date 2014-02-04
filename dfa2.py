from aes import aes,sbox,subytesTab,mixColumns,shiftRows,keySchedule,mixColumnsVecVert,subytesVecHor

text = [[0x32,0x88,0x31,0xe0],[0x43,0x5a,0x31,0x37],[0xf6,0x30,0x98,0x07],[0xa8,0x8d,0xa2,0x34]]
key = [[0x2b,0x28,0xab,0x09],[0x7e,0xae,0xf7,0xcf],[0x15,0xd2,0x15,0x4f],[0x16,0xa6,0x88,0x3c]]

RAW = 4
COL = 4

def subytesPoint(point):
    point = sbox[point / 16][point % 16]
    return point

def k9_K9J(ckdk, ej):
    for j in range(256):
        sub1 = subytesPoint(j)
        sub2 = subytesPoint(j ^ ej)
        diff2 = sub1 ^ sub2
        if diff2 == ckdk:
            return j, j ^ ej
    else:
        raise "error line 21"

def k9_CheckDiffPattern(tab):
    temp = []
    for i in range(4):
        temp.append([tab[i][COL - 1],i])
    temp = filter(lambda x: x[0] > 0, temp)
    if len(temp) == 2 and (temp[0][1] + temp[1][1]) % 2 == 1:
        return True
    else:
        return False

def k9(correct):
    result = [-1,-1,-1,-1]
    finish = [[],[],[]]
    while len(finish[2]) < RAW:
        fault = aes(text, key, 2, -1)
        diff = [[correct[i][j] ^ fault[i][j] for j in range(COL)] for i in range(RAW)]
        if k9_CheckDiffPattern(diff):
            for i in range(RAW):
                if diff[i][COL - 1] != 0 and diff[(i + 1) % 4][COL - 1] == 0:
                    ckdk = diff[(i - 1) % 4][0]
                    ej = diff[i][COL - 1]
                    sub1,sub2 = k9_K9J(ckdk, ej)
                    if i not in finish[0]:
                        finish[0].append(i)
                        finish[1].append([ej,sub1,sub2])
                    elif i not in finish[2]:
                        indice = finish[0].index(i)
                        if finish[1][indice][0] == ej:
                            break
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

def k8_Ej(j, cjdj):
    if j > 0:
        return [cjdj]
    else:
        result = []
        for i in range(256):
            for k in range(256):
                if cjdj == (subytesPoint(k) ^ subytesPoint(k ^ i) ^ i):
                    result.append(i)
                    break
        return result

def k8_Fj(k9K, cjM2djM2):
    for i in range(256):
        if cjM2djM2 == (subytesPoint(k9K) ^ subytesPoint(k9K ^ i)):
            return i

def k8_K8J(fj, ej):
    for i in range(256):
        if fj == (subytesPoint(i ^ ej) ^ subytesPoint(i)):
            return i ^ ej, i
    return -1,-1

def k8(correct, k9):
    result = [-1,-1,-1,-1]
    finish = [[],[],[]]
    while len(finish[2]) < RAW:
        fault = aes(text, key, 3, -1)
        diff = [[correct[i][j] ^ fault[i][j] for j in range(COL)] for i in range(RAW)]
        for i in range(RAW):
            if i not in finish[2] and diff[i][COL - 1] == 0 and diff[(i - 1) % 4][COL - 1] != 0 and diff[(i - 2) % 4][COL - 1] != 0 and diff[(i - 3) % 4][COL - 1] != 0:
                lstEj = k8_Ej((i - 1) % 4, diff[(i - 1) % 4][COL - 1])
                fj = k8_Fj(k9[(i - 2) % 4], diff[(i - 3) % 4][0])
                if i not in finish[0]:
                    temp = [[],[],[]]
                    for j in lstEj:
                        sub1, sub2 = k8_K8J(fj, j)
                        if sub1 == -1:
                            continue
                        temp[0].append(j)
                        temp[1].append(sub1)
                        temp[2].append(sub2)
                    if len(temp[0]) == 0:
                        break
                    finish[1].append(temp)
                    finish[0].append(i)
                else:
                    indice = finish[0].index(i)
                    temp2 = finish[1][indice]
                    temp = [[],[],[]]
                    for j in lstEj:
                        if j not in temp2[0]: 
                            sub1, sub2 = k8_K8J(fj, j)
                            if sub1 == -1:
                                continue
                            temp[0].append(sub1)
                            temp[1].append(sub2)
                            temp[2].append(j)
                    length = len(temp2[1])
                    if length == 0:
                        break
                    elif length > 1:
                        k = 0
                        print "ha1", zip(*temp2)
                        print "he", zip(*temp)
                        while k < len(temp2[1]):
                            if temp2[1][k] not in temp[0] and temp2[1][k] not in temp[1] and temp2[2][k] not in temp[1] and temp2[2][k] not in temp[0]:
                                del(temp2[0][k])
                                del(temp2[1][k])
                                del(temp2[2][k])
                            else:
                                k += 1
                        print "ha", zip(*temp2)
                    else:
                        for k in range(len(finish[1][indice][1])):
                            if temp2[1][k] in temp[0] or temp2[1][k] in temp[1]:
                                result[(i - 1) % 4] = temp2[1][k] ^ k9[(i - 1) % 4]
                            elif temp2[2][k] in temp[1] or temp2[2][k] in temp[0]:
                                result[(i - 1) % 4] = temp2[2][k] ^ k9[(i - 1) % 4]
                            else:
                                break
                            finish[2].append(i)
                break
    return result

def m8_CheckDiffPattern(tab):
    for i in range(2):
        for j in tab:
            if len(filter(lambda x: x > 0, j)) != 1:
                return False, None
        tab = map(list, zip(*tab))
    indice = 0
    if tab[0][COL - 1] != 0:
        indice = COL - 1
    elif tab[0][COL - 2] != 0:
        indice = COL - 2
    else:
        return False, None

    for i in range(1, 4):
        indice = (indice - 1) % 4
        if tab[i][indice] == 0:
            return False, None

    return True, (indice + 3) % 4

# def m8_CheckEquations(tab, diff, k9, ej, indice):
#     equations = [[0, 0, 0, ej], [0, 0, ej, 0], [0, ej, 0, 0], [ej, 0, 0, 0]]
#     temp = mixColumns(tab)
#     temp = subytesTab([[temp[i][j] ^ k9[i][j] for j in range(4)] for i in range(4)])
#     for k in range(4):
#         tab2 = [[tab[i][j] ^ equations[k][i] for j in range(4)] for i in range(4)]
#         temp2 = mixColumns(tab2)
#         temp2 = subytesTab([[temp2[i][j] ^ k9[i][j] for j in range(4)] for i in range(4)])
#         temp2 = [[temp2[i][j] ^ temp[i][j] for j in range(4)] for i in range(4)]
#         indice2 = indice
#         for l in range(4):
#             if temp2[l][(indice2 - l) % 4] != diff[l][(indice2 - l) % 4]:
#                 break
#         else:
#             return True,tab2
#     else:
#         return False, None

def m8_CheckEquations(vec, diffV, k9V, ej):
    equations = [[0, 0, 0, ej], [0, 0, ej, 0], [0, ej, 0, 0], [ej, 0, 0, 0]]
    temp = mixColumnsVecVert(vec)
    temp = subytesVecHor([temp[i] ^ k9V[i] for i in range(4)])
    for k in range(4):
        vec2 = [vec[i] ^ equations[k][i] for i in range(4)]
        temp2 = mixColumnsVecVert(vec2)
        temp2 = subytesVecHor([temp2[i] ^ k9V[i] for i in range(4)])
        temp2 = [temp2[i] ^ temp[i] for i in range(4)]
        if temp2 == diffV:
            return True,vec2
    else:
        return False, None

def m8(correct, k9):
    m8 = [[0 for i in range(COL)] for j in range(RAW)]
    # tab = [[0 for i in range(COL)] for j in range(RAW)]
    finish = [[],[],[]]
    while len(finish[2]) < 2:
        fault = aes(text, key, 4, -1)
        diff = [[correct[i][j] ^ fault[i][j] for j in range(COL)] for i in range(RAW)]
        test, indice = m8_CheckDiffPattern(diff)
        if test:
            print diff
            if indice not in finish[2]:
                candidat = [[],[]]
                diffV = [diff[i][(indice - i) % 4] for i in range(4)]    
                k9V = map(list, zip(*k9))[indice]
                for h in range(256):
                    vecV = [0,0,0,0]
                    i = 3
                    while i > -1:
                        while vecV[i] < 256:
                            test2, vecV2 = m8_CheckEquations(vecV, diffV, k9V, h)
                            if test2:
                                candidat[0].append(vecV)
                                candidat[1].append(vecV2)
                                i = -1
                                break    
                            vecV[i] += 1
                            if i < 3 and vecV[i] < 256:
                                i += 1
                                break
                        else:
                            vecV[i] = 0
                            i -= 1
                            if i == 1:
                                print vecV
                if len(finish[indice - 2]) == 0:
                    finish[indice - 2].append(candidat)
                else:
                    for i in finish[indice - 2][0]:
                        if i in candidat[0] or i in candidat[1]:
                            for j in range(4):
                                m8[j][indice] = i[j]
                    else:
                        for i in finish[indice - 2][1]:
                            if i in candidat[0] or i in candidat[1]:
                                for j in range(4):
                                    m8[j][indice] = i[j]
                        else:
                            raise "ERROR: line 213"
                    finish[2].append(indice)
                    break
    temp = mixColumns(m8)
    temp = [[temp[i][j] ^ k9[i][j] for j in range(COL)] for i in range(RAW)]
    m8 = mixColumns(shiftRows(subytesTab(temp)))
    result = [[m8[i][j] ^ correct[i][j] for j in range(4)] for i in range(4)]
    return result

def dfa():
    correct = aes(text, key)
    k = k9(correct)
    print k
    # k = k8(correct, k)
    # print k
    k=[[0,0,0,0],[0,0,0,0],[40, 209, 41, 65],[87, 92, 0, 110]]
    print m8(correct, map(list, zip(*k)))
    # k = key
    # for i in range(10):
    #     k = keySchedule(k, i)
    # print zip(*k)[38]

if __name__ == "__main__":
    dfa()