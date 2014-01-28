from aes_v001 import AES

class AES_wrapper:
    """
    A wrapper module for aes_v001.py.
    This wrapper wraps the AES class
    so that the I/O is conducted by
    a list containing uint16 values
    (cf. a list of byte values).

    2009/Dec/06
    Takeshi Sugawara
    """
    keySize = AES.keySize
    def __init__(self):
        """
        Note that the wrapping is achieved by
        has-a relationship (instead of is-a).
        This is because the method encrypt
        is an instance method.
        """
        self.aobj = AES()

    @staticmethod
    def uint16listToBytelist(uint16list):
        buf = []
        for uint16element in uint16list:
            buf.append(uint16element / 256)
            buf.append(uint16element % 256)
        return buf

    @staticmethod
    def bytelistToUint16list(bytelist):
        buf = []
        for i in range(len(bytelist)/2):
            buf.append( bytelist[2*i] * 256 + bytelist[2*i+1] )
        return buf

    def encrypt(self, pt_uint16, key_uint16, keysize):
        pt  = AES_wrapper.uint16listToBytelist(pt_uint16)
        key = AES_wrapper.uint16listToBytelist(key_uint16)
        result_byte = self.aobj.encrypt(pt, key, keysize)
        return AES_wrapper.bytelistToUint16list(result_byte)
    
    def decrypt(self, pt_uint16, key_uint16, keysize):
        pt  = AES_wrapper.uint16listToBytelist(pt_uint16)
        key = AES_wrapper.uint16listToBytelist(key_uint16)
        result_byte = self.aobj.decrypt(pt, key, keysize)
        return AES_wrapper.bytelistToUint16list(result_byte)

if __name__ == '__main__':
    # key = [0x2b7e, 0x1516, 0x28ae, 0xd2a6, 0xabf7, 0x1588, 0x09cf, 0x4f3c]
    # pt  = [0x3243, 0xf6a8, 0x885a, 0x308d, 0x3131, 0x98a2, 0xe037, 0x0734]
    # aobj = AES_wrapper()
    # print aobj.encrypt(pt, key, AES_wrapper.keySize["SIZE_128"])
    import random
    aobj = AES_wrapper()

    def format_hex(result):
        tmp = map((lambda x: '%.4x' % x), result)
        return "128'h" + "_".join(tmp)

    key = [0x0001, 0x0203, 0x0405, 0x0607, 0x0809, 0x0a0b, 0x0c0d, 0x0e0f]
    for i in range(100):
        pt = [random.randrange(0, 65535) for i in range(8)]
        result = aobj.encrypt(pt, key, AES_wrapper.keySize["SIZE_128"])
        print "encrypt(", format_hex(pt), ',', format_hex(result), ");"
        result = aobj.decrypt(pt, key, AES_wrapper.keySize["SIZE_128"])
        print "decrypt(", format_hex(pt), ',', format_hex(result), ");"
    
