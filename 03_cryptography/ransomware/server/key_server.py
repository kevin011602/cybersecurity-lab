import socket
import logging
import os # Necessario per eliminare il file

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def start_key_server():
    IP = "0.0.0.0" 
    PORT = 5555    
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Permette di riutilizzare subito la porta se riavvii lo script
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((IP, PORT))
        s.listen(1)
        logging.info(f"Server di recupero chiavi attivo sulla porta {PORT}...")
        
        conn, addr = s.accept()
        with conn:
            logging.info(f"Connessione ricevuta da {addr}. Invio chiave privata...")
            try:
                # 1. Legge e invia il file
                with open("private_key.pem", "rb") as f:
                    key_data = f.read()
                    conn.sendall(key_data)
                
                logging.info("Chiave privata inviata con successo.")

                # 2. CANCELLAZIONE DAL SERVER (Kali)
                os.remove("private_key.pem")
                logging.info("File 'private_key.pem' rimosso dal server Kali.")

            except FileNotFoundError:
                logging.error("Errore: private_key.pem non trovata su Kali!")
            except Exception as e:
                logging.error(f"Errore durante l'invio o la rimozione: {e}")

if __name__ == "__main__":
    start_key_server()