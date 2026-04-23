import socket
import struct
import os
from cryptography.hazmat.primitives import hashes, serialization, hmac
from cryptography.hazmat.primitives.asymmetric import padding as rsa_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt_and_send(server_ip, server_port, file_to_send):
    # 1. Setup Crittografico
    with open("server_public.pem", "rb") as k:
        public_key = serialization.load_pem_public_key(k.read())

    aes_key = os.urandom(32) 
    iv = os.urandom(16)

    with open(file_to_send, "rb") as f:
        plaintext = f.read()
    
    # 2. Cifratura Dati (Confidenzialità)
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # 3. Generazione HMAC (Integrità)
    h = hmac.HMAC(aes_key, hashes.SHA256())
    h.update(ciphertext)
    hmac_tag = h.finalize()

    # 4. Protezione della Session Key con RSA
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        rsa_padding.OAEP(
            mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 5. Trasmissione Protocollo: [LenK][K][IV][LenC][C][HMAC]
    with socket.create_connection((server_ip, server_port)) as sock:
        sock.sendall(struct.pack('!I', len(encrypted_aes_key)))
        sock.sendall(encrypted_aes_key)
        sock.sendall(iv)
        sock.sendall(struct.pack('!I', len(ciphertext)))
        sock.sendall(ciphertext)
        sock.sendall(hmac_tag) # Invio del "sigillo" di garanzia
        
        print(f"[*] Payload inviato. In attesa di conferma integrità...")
        response = sock.recv(1024)
        print(f"[*] Risposta server: {response.decode()}")

if __name__ == "__main__":
    encrypt_and_send("192.168.188.130", 8082, "testo_segreto.txt")