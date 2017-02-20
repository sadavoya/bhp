'''Various functions to do the exfilration grunt work'''
import zlib
import base64
from Crypto.Util import number
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

VERBOSE = 0

def verbose(output, verbosity):
    '''prints the output if VERBOSE >= verbosity'''
    if VERBOSE >= verbosity:
        print output

class Encryption(object):
    ''' A class to handle encryption and decryption using rsa'''
    CHUNK_SIZE = 256 # how to arrive at 214? https://goo.gl/yhmRR8
    OAEP_PADDING_SIZE = 42
    def __init__(self, verbosity=4):
        self.verbosity = verbosity
    def prn(self, target):
        '''Print the text using my verbosity level'''
        verbose(target, self.verbosity)

    def pad(self, target, padding, length):
        '''pad target with padding to length'''
        result = '%s' % target
        rlen = len(result)
        rem = len(result) % length
        if rem != 0:
            diff = length - rlen
            padding = padding * diff
            result += padding
        return result

    def encrypt_string(self, public_key, plaintext):
        '''encrypt and compress the plaintext using the public key'''
        # encryption adds padding so our chunk size must reflect that
        chunk_size = self.CHUNK_SIZE - self.OAEP_PADDING_SIZE 

        self.prn('Encrypting %d bytes' % len(plaintext))

        rsakey = RSA.importKey(public_key)
        rsakey = PKCS1_OAEP.new(rsakey)

        encrypted = ''
        offset = 0
        plaintext = self.pad(plaintext, ' ', chunk_size)

        while offset < len(plaintext):
            chunk = plaintext[offset:offset + chunk_size]
            chunk = self.pad(chunk, ' ', chunk_size)
            encrypted += rsakey.encrypt(chunk)
            offset += chunk_size

        self.prn('Compressing %d bytes' % len(encrypted))
        compressed = zlib.compress(encrypted)
        compressed = compressed.encode('base64')
        self.prn('Base64 encoded compressed crypto: %d' % len(compressed))
        return compressed

    def decrypt_string(self, private_key, base64_compressed_cipher_text):
        '''decompress and decrypt the base64 ciphertext using the private key'''
        chunk_size = self.CHUNK_SIZE

        rsakey = RSA.importKey(private_key)
        rsakey = PKCS1_OAEP.new(rsakey)

        self.prn('Base64 encoded compressed cipher text: %d'
                 % len(base64_compressed_cipher_text))
        compressed_cipher_text = base64.b64decode(base64_compressed_cipher_text)

        self.prn('Decompressing %d bytes' % len(compressed_cipher_text))
        cipher_text = zlib.decompress(compressed_cipher_text)

        offset = 0
        decrypted = ''
        while offset < len(cipher_text):
            decrypted += rsakey.decrypt(cipher_text[offset:offset + chunk_size])
            offset += chunk_size
        self.prn('Decrypted %d bytes' % len(decrypted))
        return decrypted

    def genkeys(self, size=2048, e_parm=65537, export_type='PEM'):
        '''generate a public key pair'''
        newkey = RSA.generate(size, e=e_parm)
        public_key = newkey.publickey().exportKey(export_type)
        private_key = newkey.exportKey(export_type)
        self.prn('Public key: %s' % public_key)
        self.prn('Private key: %s' % private_key)
        return public_key, private_key

def test_encryption(keys=None, verbosity=6):
    '''test encryption'''
    encryptor = Encryption(verbosity=5)
    exp = 'The quick brown fox jumps over the lazy dog.'
    if keys is None:
        keys = encryptor.genkeys()
    pub, priv = keys
    enc = encryptor.encrypt_string(pub, exp)
    act = encryptor.decrypt_string(priv, enc)
    test(exp, act[:len(exp)], verbosity=verbosity)

def test(exp, act, msg='', verbosity=5):
    '''test if exp = act and print msg if not'''
    result = exp == act
    if not result:
        verbose('FAILED: %s != %s%s%s' % (exp, act, '' if len(msg) == 0 else ' - ', msg), -1)
    else:
        verbose('PASSED: %s = %s%s%s' % (exp, act, '' if len(msg) == 0 else ' - ', msg), verbosity)
    return result
def main():
    '''test the utils'''
    global VERBOSE
    VERBOSE = 5
    test_encryption()



if __name__ == '__main__':
    main()
