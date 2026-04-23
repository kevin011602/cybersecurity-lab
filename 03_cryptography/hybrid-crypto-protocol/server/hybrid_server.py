import socket
import struct
from cryptography.hazmat.primitives import hashes, serialization, hmac
from cryptography.hazmat.primitives.asymmetric import padding as rsa_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def recv_exact(sock, n):
    """Assicura la ricezione di esattamente n byte, evitando troncamenti TCP."""
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Connessione interrotta durante la ricezione.")
        data += chunk
    return data

def run_server(host='0.0.0.0', port=8082):
    with open("server_private.pem", "rb") as k:
        private_key = serialization.load_pem_private_key(k.read(), password=None)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)
        print(f"[*] Server C2 in ascolto su {port}...")

        conn, addr = s.accept()
        with conn:
            print(f"[*] Connessione sicura stabilita con {addr}")

            # 1. Ricezione Header e Chiavi
            key_len = struct.unpack('!I', recv_exact(conn, 4))[0]
            encrypted_aes_key = recv_exact(conn, key_len)
            iv = recv_exact(conn, 16)
            
            # 2. Ricezione Dati e Tag di Integrità (HMAC)
            file_len = struct.unpack('!I', recv_exact(conn, 4))[0]
            ciphertext = recv_exact(conn, file_len)
            received_hmac = recv_exact(conn, 32) # SHA-256 produce 32 byte

            # 3. Decifratura della Session Key (AES)
            aes_key = private_key.decrypt(
                encrypted_aes_key,
                rsa_padding.OAEP(
                    mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # 4. VERIFICA INTEGRITÀ (HMAC)
            h = hmac.HMAC(aes_key, hashes.SHA256())
            h.update(ciphertext)
            try:
                h.verify(received_hmac)
                print("[+] Verifica Integrità: OK (Il file non è stato manipolato)")
            except Exception:
                print("[!] ERRORE: Integrità compromessa! Il file potrebbe essere stato alterato.")
                conn.sendall(b"ERROR: Integrity check failed.")
                return

            # 5. Decifratura finale dei dati
            cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv))
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            with open("received_decrypted.txt", "wb") as f:
                f.write(plaintext)
            
            print("[+] Decifratura completata con successo.")
            conn.sendall(b"OK: File ricevuto e verificato.")

if __name__ == "__main__":
    run_server()