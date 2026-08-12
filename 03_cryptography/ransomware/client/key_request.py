import socket

def request_key():
    KALI_IP = "192.168.188.130"
    PORT = 5555

    print(f"[*] Richiesta chiave privata a Kali ({KALI_IP})...")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((KALI_IP, PORT))
            key_data = s.recv(4096)
            
            if key_data:
                with open("private_key.pem", "wb") as f:
                    f.write(key_data)
                print("[+] Chiave privata ricevuta e salvata come 'private_key.pem'.")
                print("[!] Ora puoi eseguire 'python3 decryptor.py'.")
            else:
                print("[-] Errore: Ricevuti dati vuoti.")
    except Exception as e:
        print(f"[-] Errore durante il trasferimento: {e}")

if __name__ == "__main__":
    request_key()