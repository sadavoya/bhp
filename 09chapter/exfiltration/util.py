'''Various functions to do the exfilration grunt work'''
import zlib
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

VERBOSE = 0
CHUNK_SIZE = 256

def verbose(output, verbosity):
    '''prints the output if VERBOSE >= verbosity'''
    if VERBOSE >= verbosity:
        print output
def pad(target, padding, length):
    '''pad target with padding to length'''
    result = '%s' % target
    if len(result) % length != 0:
        result += padding * (length - len(result))
    return result

def encrypt_string(public_key, plaintext):
    '''encrypt and compress the plaintext using the public key'''
    verbosity = 4
    chunk_size = CHUNK_SIZE

    verbose('Encrypting %d bytes' % len(plaintext), verbosity)

    rsakey = RSA.importKey(public_key)
    rsakey = PKCS1_OAEP.new(rsakey)

    encrypted = ''
    offset = 0
    plaintext = pad(plaintext, ' ', chunk_size)

    while offset < len(plaintext):
        chunk = plaintext[offset:offset + chunk_size]
        chunk = pad(chunk, ' ', chunk_size)
        verbose(len(chunk), 4)
        encrypted += rsakey.encrypt(chunk)
        offset += chunk_size

    verbose('Compressing %d bytes' % len(encrypted), verbosity)
    compressed = zlib.compress(encrypted)
    compressed = compressed.encode('base64')
    verbose('Base64 encoded compressed crypto: %d' % len(compressed), verbosity)
    return compressed

def decrypt_string(private_key, base64_compressed_cipher_text):
    '''decompress and decrypt the base64 ciphertext using the private key'''
    verbosity = 4
    chunk_size = CHUNK_SIZE

    rsakey = RSA.importKey(private_key)
    rsakey = PKCS1_OAEP.new(rsakey)

    verbose('Base64 encoded compressed cipher text: %d'
            % len(base64_compressed_cipher_text), verbosity)
    compressed_cipher_text = base64.b64decode(base64_compressed_cipher_text)

    verbose('Decompressing %d bytes' % len(compressed_cipher_text), verbosity)
    cipher_text = zlib.decompress(compressed_cipher_text)

    offset = 0
    decrypted = ''
    while offset < len(cipher_text):
        decrypted += rsakey.decrypt(cipher_text[offset:offset + chunk_size])
        offset += chunk_size
    verbose('Decrypted %d bytes' % len(decrypted), verbosity)
    return decrypted

def genkeys(size=2048, e_parm=65537, export_type='PEM'):
    '''generate a public key pair'''
    verbosity = 4
    newkey = RSA.generate(size, e=e_parm)
    public_key = newkey.publickey().exportKey(export_type)
    private_key = newkey.exportKey(export_type)
    verbose('Public key: %s' % public_key, verbosity)
    verbose('Private key: %s' % public_key, verbosity)
    return public_key, private_key
def test_encryption():
    '''test encryption'''
    exp = 'The quick brown fox jumps over the lazy dog.'
    pub, priv = genkeys()
    enc = encrypt_string(pub, exp)
    act = decrypt_string(priv, enc)
    print enc
    print act

def main():
    '''test the utils'''
    global VERBOSE
    VERBOSE = 5
    test_encryption()


if __name__ == '__main__':
    main()
