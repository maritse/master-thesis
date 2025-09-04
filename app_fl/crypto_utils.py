import os
import sqlite3
import base64
import struct
import io
import numpy as np
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from flwr.common import parameters_to_ndarrays, ndarrays_to_parameters




#def extract_pub_keys_with 

def load_public_key_from_db(client_id: str):
    conn = sqlite3.connect("./app_fl/db.db")
    cur = conn.cursor()
    cur.execute("SELECT public_key FROM client_keys WHERE client_id = ?", (client_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        raise ValueError(f"No key found for client {client_id}")
    pem_b64 = row[0]
    pem_bytes = base64.b64decode(pem_b64)
    public_key = serialization.load_pem_public_key(
        pem_bytes,
        backend=default_backend()
    )
    """
    pem_out = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    """
    return public_key

def encrypt_data_pubkey_client(parameters, client_id) -> str:
    """
        Encrypt a string `data` for a specific client using hybrid RSA + AES-GCM.
        Returns a base64-encoded string containing:
        [4-byte encrypted AES key length] [encrypted AES key] [12-byte nonce] [ciphertext]
    """
    # new approach
    arrays = parameters_to_ndarrays(parameters)

    # Serialize ndarrays to bytes
    buf = io.BytesIO()
    np.savez_compressed(buf, *arrays)
    plaintext = buf.getvalue()

    
    client_pubkey = load_public_key_from_db(client_id)
    #print("client_pubkey: " + str(client_pubkey))
    #plaintext = str(data).encode("utf-8")

    # 3) Generate random AES key (256-bit) and nonce (12 bytes)
    aes_key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)

    # 4) Encrypt plaintext with AES-GCM
    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)

    encrypted_key = client_pubkey.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # 6) Pack lengths + bytes: [4-byte len_encrypted_key][encrypted_key][nonce][ciphertext]
    header = struct.pack(">I", len(encrypted_key))
    package = header + encrypted_key + nonce + ciphertext

    # 7) Return base64 string for easy transport/storage
    return ndarrays_to_parameters([np.frombuffer(package, dtype=np.uint8)])

def load_private_key_from_file(password: bytes = None):
    """
    Load RSA private key from PEM file.
    `password` is needed if the key is encrypted.
    """
    file_path = "./app_fl/private_key.pem"
    with open(file_path, "rb") as f:
        key_data = f.read()
        private_key = serialization.load_pem_private_key(
            key_data,
            password=password,
        )
    return private_key

def decrypt_data_privkey_client(ins_parameters: str) -> str:
    """
        Decrypt data with server's pub key at client side
    """
    # Flower gives you a Parameters object
    arrays = parameters_to_ndarrays(ins_parameters)
    package = arrays[0].tobytes()  # the encrypted blob
    # load private key
    private_key = load_private_key_from_file()
    # decode base64
    #package = base64.b64decode(ciphertext_b64)
    #  Extract length of RSA-encrypted AES key
    len_key = struct.unpack(">I", package[:4])[0]
    idx = 4
    encrypted_key = package[idx: idx+len_key]; idx += len_key
    #  Extract nonce (12 bytes for AES-GCM)
    nonce = package[idx: idx+12]; idx += 12
    #  Remaining is ciphertext
    ciphertext = package[idx:]
    # decrypt AES key with RSA priv key
    aes_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # decrypt cipher text with AES-GCM
    aesgcm = AESGCM(aes_key)
    plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, associated_data=None)

    # Deserialize back to list of ndarrays
    buf = io.BytesIO(plaintext_bytes)
    arrays = list(np.load(buf).values())
    #npz = np.load(buf, allow_pickle=False)
    #arrays = [npz[f] for f in npz.files]
    #return plaintext_bytes.decode("utf-8")
    #return ndarrays_to_parameters(arrays)
    return arrays

def encrypt_data_pubkey_server(parameters):
    """
        Encrypt data using server's public key
    """
    #arrays = parameters_to_ndarrays(parameters)

    # Serialize ndarrays to bytes
    buf = io.BytesIO()
    np.savez_compressed(buf, *parameters)
    plaintext = buf.getvalue()
    
    with open("./app_fl/public_key.pem", "rb") as f:
        server_pubkey = serialization.load_pem_public_key(f.read())

    aes_key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)

    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)

    encrypted_key = server_pubkey.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    header = struct.pack(">I", len(encrypted_key))
    package = header + encrypted_key + nonce + ciphertext

    return ndarrays_to_parameters([np.frombuffer(package, dtype=np.uint8)])

def decrypt_data_privkey_server(ins_parameters):
    """
        Decrypt data with server's pub key at client side
    """
    arrays = parameters_to_ndarrays(ins_parameters)
    package = arrays[0].tobytes()  # the encrypted blob
    # load private key
    private_key = load_private_key_from_file()
    #  Extract length of RSA-encrypted AES key
    len_key = struct.unpack(">I", package[:4])[0]
    idx = 4
    encrypted_key = package[idx: idx+len_key]; idx += len_key
    #  Extract nonce (12 bytes for AES-GCM)
    nonce = package[idx: idx+12]; idx += 12
    #  Remaining is AES-GCM ciphertext
    ciphertext = package[idx:]
    # decrypt AES key with RSA priv key
    aes_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # decrypt cipher text with AES-GCM
    aesgcm = AESGCM(aes_key)
    plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, associated_data=None)

    # Deserialize back to list of ndarrays
    buf = io.BytesIO(plaintext_bytes)
    arrays = list(np.load(buf).values())
    return arrays