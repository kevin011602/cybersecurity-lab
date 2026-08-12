import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# --- CONFIGURAZIONE ---
TARGET_DIR = "./data"
PRIVATE_KEY_PATH = "private_key.pem"
BLOB_PATH = "key_blob.bin"
RANSOM_NOTE = "RIPRISTINO_INFO.txt"

def decrypt_all():
    # 1. Caricamento Chiave Privata
    try:
        with open(PRIVATE_KEY_PATH, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
    except Exception as e:
        print(f"[-] Errore chiave: {e}")
        return

    # 2. Estrazione IV e Chiave AES dal blob
    if not os.path.exists(BLOB_PATH):
        print(f"[-] Errore: {BLOB_PATH} non trovato!")
        return

    with open(BLOB_PATH, "rb") as f:
        blob = f.read()
        iv = blob[:16]
        encrypted_aes_key = blob[16:]

    # 3. Decifratura Chiave AES tramite RSA
    print("[*] Recupero chiave AES...")
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )

    # 4. Decifratura File nella cartella /data
    for root, _, files in os.walk(TARGET_DIR):
        for file in files:
            # Salta i file di sistema e le note
            if file in [RANSOM_NOTE, BLOB_PATH, PRIVATE_KEY_PATH]: continue
            
            path = os.path.join(root, file)
            with open(path, "rb") as f:
                ct = f.read()

            try:
                cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
                decryptor = cipher.decryptor()
                padded_data = decryptor.update(ct) + decryptor.finalize()

                # Rimozione Padding PKCS7
                pad_len = padded_data[-1]
                if 1 <= pad_len <= 16:
                    if padded_data[-pad_len:] == bytes([pad_len]) * pad_len:
                        data = padded_data[:-pad_len]
                    else:
                        data = padded_data
                else:
                    data = padded_data

                with open(path, "wb") as f:
                    f.write(data)
                print(f"[+] Decifrato: {file}")
            except Exception as e:
                print(f"[-] Errore su {file}: {e}")

    # 5. PULIZIA FINALE (Ritorno allo stato iniziale)
    print("\n[*] Pulizia tracce in corso...")
    file_da_eliminare = [BLOB_PATH, PRIVATE_KEY_PATH, RANSOM_NOTE]
    
    for f_name in file_da_eliminare:
        if os.path.exists(f_name):
            os.remove(f_name)
            print(f"[PULIZIA] Eliminato: {f_name}")

    print("\n[SUCCESS] Sistema ripristinato e pulito correttamente.")

if __name__ == "__main__":
    decrypt_all()