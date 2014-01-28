# -*- coding: shift_jis -*-

from aes import *
from multiprocessing import Pool

def round_input(cphr, key, r_r):
    w_ary = 44 * [0]
    state = [[0 for i in range(4)] for j in range(4)]
    round_c = [[]]; rcon_gen(round_c)
    key_expansion(key, round_c, w_ary)

    for w in range(4):
        for byte in range(4):
            state[byte][w] = cphr[byte+4*w]

    add_round_key(state, w_ary, 10)
    inv_shift_rows(state)
    inv_sub_bytes(state)

    if r_r == 10:
        return copy.deepcopy(state)

    for r in range(9,0,-1):
        add_round_key(state, w_ary, r)
        inv_mix_columns(state)
        inv_shift_rows(state)
        inv_sub_bytes(state)
        if r_r == r:
            return copy.deepcopy(state)

    add_round_key(state, w_ary, 0)
    if r_r == 0:
        return copy.deepcopy(state)

    return False

def count_diff(state1, state2):
    diff = 0
    for w in range(4):
        for byte in range(4):
            if state1[byte][w] != state2[byte][w]:
                diff += 1
    return diff    

def injected_round(correct, incorrect, key):
    diff    = 11 * [None]
    w_ary = 44 * [0]
    c_state = [[0 for i in range(4)] for j in range(4)]
    i_state = [[0 for i in range(4)] for j in range(4)]
    round_c = [[]]; rcon_gen(round_c)
    key_expansion(key, round_c, w_ary)

    for w in range(4):
        for byte in range(4):
            c_state[byte][w] = correct[byte+4*w]
            i_state[byte][w] = incorrect[byte+4*w]

    add_round_key(c_state, w_ary, 10)
    add_round_key(i_state, w_ary, 10)
    inv_shift_rows(c_state)
    inv_shift_rows(i_state)
    inv_sub_bytes(c_state)
    inv_sub_bytes(i_state)

    diff[10] = count_diff(c_state, i_state)

    for r in range(9,0,-1):
        add_round_key(c_state, w_ary, r)
        inv_mix_columns(c_state)
        inv_shift_rows(c_state)
        inv_sub_bytes(c_state)
        add_round_key(i_state, w_ary, r)
        inv_mix_columns(i_state)
        inv_shift_rows(i_state)
        inv_sub_bytes(i_state)
        diff[r] = count_diff(c_state, i_state)
        
    min_byte = 16
    r = 0
    for i in range(1,11):
        if diff[i] < min_byte:
            min_byte = diff[i]
            r = i
    return [r, min_byte]

def key_reverse(key):
    round_c = [[]]; rcon_gen(round_c)
    w = [[0 for i in range(4)] for j in range(44)]
    for i in range(4):
        for j in range(4):
            w[i+40][j] = key[4*i+j]
    for i in range(43, 3, -1):
        temp = w[i-1][:]
        if i % 4 == 0:
            temp = sub_word(rot_word(temp))
            for j in range(4):
                temp[j] = temp[j] ^ round_c[i/4][j]
        for j in range(4):
            w[i-4][j] = w[i][j] ^ temp[j]
    ret_key = 16 * [0]
    for i in range(4):
        for j in range(4):
            ret_key[4*i+j] = w[i][j]
    return ret_key

def DFA_mix_columns(word):
    ret_w = [0,0,0,0]
    s0 = word[0]; t0 = mul2(s0)
    s1 = word[1]; t1 = mul2(s1)
    s2 = word[2]; t2 = mul2(s2)
    s3 = word[3]; t3 = mul2(s3)
    ret_w[0] = (     t0 ^ s1 ^ t1 ^ s2      ^ s3     ) & 0xFF
    ret_w[1] = (s0           ^ t1 ^ s2 ^ t2 ^ s3     ) & 0xFF
    ret_w[2] = (s0      ^ s1           ^ t2 ^ s3 ^ t3) & 0xFF
    ret_w[3] = (s0 ^ t0 ^ s1      ^ s2           ^ t3) & 0xFF
    return ret_w

def DFA_add_round_key(state, key):
    for w in range(4):
        for byte in range(4):
            state[byte][w] = state[byte][w] ^ key[w][byte]

def reduce_candidate(cphr1, cphr2, col, keys = []):
    st1 = str2lst(cphr1)
    st2 = str2lst(cphr2)

    # Possible patterns
    D10 = [[0 for i in range(4)] for j in range(1024)]
    for i in range(4):
        for j in range(256):
            D10[256*i+j][i] = j
            D10[256*i+j]    = DFA_mix_columns(D10[256*i+j][:])
    # All key candidates
    state1 = [[0 for i in range(4)] for j in range(4)]
    state2 = [[0 for i in range(4)] for j in range(4)]
    for w in range(4):
        for byte in range(4):
            state1[byte][w] = st1[byte+4*w]
    for w in range(4):
        for byte in range(4):
            state2[byte][w] = st2[byte+4*w]
    cand_keys = []
    if len(keys) != 0:
        for key in keys:
            DFA_add_round_key(state1, key)
            DFA_add_round_key(state2, key)
            inv_shift_rows(state1)
            inv_shift_rows(state2)
            inv_sub_bytes(state1)
            inv_sub_bytes(state2)
            xor = [0,0,0,0]
            for i in range(4):
                xor[i] = state1[i][col] ^ state2[i][col]
            if xor in D10:
                cand_keys.append(key[:])
    else:
        for i in range(256):
            print 'i=%d' % i
            for j in range(256):
                print 'j=%d' % j
                for k in range(256):
                    print 'k=%d' % k
                    for l in range(256):
                        key = None
                        if col == 0:
                            key = [[i,0,0,0],[0,0,0,j],[0,0,k,0],[0,l,0,0]]
                        elif col == 1:
                            key = [[0,i,0,0],[j,0,0,0],[0,0,0,k],[0,0,l,0]]
                        elif col == 2:
                            key = [[0,0,i,0],[0,j,0,0],[k,0,0,0],[0,0,0,l]]
                        elif col == 3:
                            key = [[0,0,0,i],[0,0,j,0],[0,k,0,0],[l,0,0,0]]
                        DFA_add_round_key(state1, key)
                        DFA_add_round_key(state2, key)
                        inv_shift_rows(state1)
                        inv_shift_rows(state2)
                        inv_sub_bytes(state1)
                        inv_sub_bytes(state2)
                        xor = [0,0,0,0]
                        for i in range(4):
                            xor[i] = state1[i][col] ^ state2[i][col]
                        if xor in D10:
                            print 'hit'
                            print key
                            cand_keys.append(key[:])
    return cand_keys    

if __name__ == '__main__':
    round_10_key = 'd014f9a8c9ee2589e13f0cc8b6630ca6'
    correct_key  = '2b7e151628aed2a6abf7158809cf4f3c'

    print '10th round key    : ' + round_10_key
    print 'Original key      : ' + correct_key
    print
    res_key = key_reverse(str2lst(round_10_key))
    print 'Result of reverse : ' + lst2str(res_key)
    print
    res = ''
    if correct_key == lst2str(res_key):
        res = 'OK'
    else:
        res = 'NG'
    print 'Result -> ' + res

    correct_cphr1   = '7b0c785e27e8ad3f8223207104725dd4'
    incorrect_cphr1 = '15690bf76786831027ef13e25e61d893'
    correct_cphr2   = '0ec25b869f491a2ff044c88c17437adb'
    incorrect_cphr2 = '145de7b992f74e3011251f4b373bfb32'
    
    cand_keys = reduce_candidate(correct_cphr1, incorrect_cphr1, 0)
    cand_keys = reduce_candidate(correct_cphr2, incorrect_cphr2, 0, cand_keys)
    
    print cand_keys
